#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright (c) 2026 Jean Camille d'Ornano
# Licensed under the PolyForm Noncommercial License 1.0.0 (see LICENSE).
# Commercial use requires a separate licence agreement with the author.
"""
Prototype of Cantor-trajectory watermarking (audio), v0.2.
Author: Jean Camille d'Ornano ("Doigtman") -- concept; prototype v0.2

Proof of concept ONLY. Not a security product. See README.md for the framework.

What is new in v0.2 (compared with v0.1, which had one process, one fractal):
  * Three watermarking PROCESSES are cumulated on the same audio
      "freq"  : 1D Cantor selection along the frequency bins (continuous r(t)),
      "time"  : 1D Cantor selection along time inside windows of BLOCK frames,
      "image" : 2D product F x F' of two Cantor sets on the (frequency, time) grid.
  * Each process carries N_FRACTALS = 3 INDEPENDENT fractals (own parameters,
    own phase/bin subset, all derived from the key with distinct HMAC labels).
    The perturbations add up: the sound changes more (see SNR), but a forger
    must now find 3 x 3 = 9 independent hidden objects instead of one.
  * Detection is per (process, fractal), with null distribution obtained from
    WRONG KEYS (honest null), then fused by Stouffer's rule.

Everything is derived from HMAC(key, fingerprint | label). No imperceptibility
test other than SNR has been run. See the paper, Part II, Sections 7-9.
"""
import hashlib, hmac, os, subprocess, tempfile
import numpy as np
from scipy.signal import stft, istft
from scipy.interpolate import CubicSpline
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d

SR = 44100
NFFT = 2048
HOP = 512
R_MIN, R_MAX = 0.30, 0.44          # contraction ratios -> dimension 0.58 .. 0.84
FMIN, FMAX = 300.0, 12000.0        # embedding band (survives MP3 low-pass)
HP_F = 129                         # spectral high-pass width (bins)
BLOCK = 64                         # frames per time window / tile (~0.74 s)
HP_T = 65                          # temporal high-pass width (frames)
N_FRACTALS = 3                     # independent fractals PER PROCESS (>= 3)
PROCESSES = ("freq", "time", "image")
LEVELS = {"freq": 5, "time": 4, "image": 3}   # truncation depth per process


# ---------- Cantor sets ----------
def cantor_starts(r, levels):
    starts, length = np.array([0.0]), 1.0
    for _ in range(levels):
        starts = np.concatenate([starts, starts + length * (1 - r)])
        length *= r
    return np.sort(starts), length


def cantor_mask(r, x, levels):
    """1.0 where x in [0,1] lies in the level-`levels` symmetric Cantor set."""
    starts, length = cantor_starts(r, levels)
    idx = np.clip(np.searchsorted(starts, x, side="right") - 1, 0, len(starts) - 1)
    return (x < starts[idx] + length).astype(float)


def dim(r):
    return np.log(2.0) / np.log(1.0 / r)


# ---------- key-derived parameters ----------
def _rng(key: bytes, label: str, fp: str = "0"):
    d = hmac.new(key, (fp + "|" + label).encode(), hashlib.sha256).digest()
    return np.random.default_rng(int.from_bytes(d[:8], "big"))


def smooth_traj(rng, n, every):
    """Smooth random path of n samples in [R_MIN, R_MAX] (spline of control points)."""
    n_ctrl = max(4, int(n / every) + 2)
    tc = np.linspace(0, max(n - 1, 1), n_ctrl)
    vals = rng.uniform(R_MIN, R_MAX, n_ctrl)
    return np.clip(CubicSpline(tc, vals)(np.arange(n)), R_MIN, R_MAX)


def freq_params(key, k, n_frames, fp="0"):
    """(phase s, trajectory r(t)) of the k-th fractal of the 'freq' process."""
    rng = _rng(key, f"freq:{k}", fp)
    s = rng.uniform()
    r_t = smooth_traj(rng, n_frames, 2.0 * SR / HOP)
    return s, r_t


def perturbation(key, proc, k, n_bins, n_frames, fp="0"):
    """S in {-1,0,+1}, shape (n_bins, n_frames): the k-th fractal of `proc`."""
    x = np.arange(n_bins) / (n_bins - 1)
    S = np.zeros((n_bins, n_frames), dtype=np.float32)
    L = LEVELS[proc]
    if proc == "freq":
        s, r_t = freq_params(key, k, n_frames, fp)
        xs = (x + s) % 1.0
        for j in range(n_frames):
            S[:, j] = 2 * cantor_mask(r_t[j], xs, L) - 1
        return S
    rng = _rng(key, f"{proc}:{k}", fp)
    n_win = -(-n_frames // BLOCK)
    tau = (np.arange(BLOCK) + 0.5) / BLOCK
    if proc == "time":
        group = rng.random(n_bins) < 0.5           # key-derived subset of bins
        r_w = smooth_traj(rng, n_win, 4)
        for w in range(n_win):
            a, b = w * BLOCK, min((w + 1) * BLOCK, n_frames)
            m = cantor_mask(r_w[w], tau[: b - a], L)
            S[np.ix_(group, np.arange(a, b))] = (2 * m - 1)[None, :]
        return S
    if proc == "image":                              # product F x F'
        s = rng.uniform()
        rf = smooth_traj(rng, n_win, 4)
        rt = smooth_traj(rng, n_win, 4)
        xs = (x + s) % 1.0
        for w in range(n_win):
            a, b = w * BLOCK, min((w + 1) * BLOCK, n_frames)
            m = np.outer(cantor_mask(rf[w], xs, L), cantor_mask(rt[w], tau[: b - a], L))
            S[:, a:b] = 2 * m - 1
        return S
    raise ValueError(proc)


# ---------- signal helpers ----------
def band_bins():
    freqs = np.fft.rfftfreq(NFFT, 1.0 / SR)
    ks = np.where((freqs >= FMIN) & (freqs <= FMAX))[0]
    return ks


def fingerprint(sig):
    """Crude 15-bit coarse fingerprint (unchanged from v0.1; known to be fragile)."""
    f, _, Z = stft(sig, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    P = (np.abs(Z) ** 2).mean(axis=1)
    edges = np.geomspace(100, 10000, 17)
    E = np.array([P[(f >= a) & (f < b)].sum() for a, b in zip(edges[:-1], edges[1:])])
    return "".join(map(str, (np.diff(np.log(E + 1e-12)) > 0).astype(int)))


# ---------- embedding ----------
def embed(sig, key, delta=0.04, processes=PROCESSES, n_fractals=N_FRACTALS,
          use_fingerprint=False):
    """Cumulate len(processes) x n_fractals fractal perturbations.
    delta is the amplitude PER fractal; the total change grows with their number."""
    fp = fingerprint(sig) if use_fingerprint else "0"
    f, t, Z = stft(sig, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    ks = band_bins()
    acc = np.zeros((len(ks), Z.shape[1]), dtype=np.float32)
    for p in processes:
        for k in range(n_fractals):
            acc += perturbation(key, p, k, len(ks), Z.shape[1], fp)
    G = np.ones(Z.shape)
    G[ks] = np.clip(1.0 + delta * acc, 0.2, 3.0)
    _, out = istft(Z * G, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    out = out[: len(sig)]
    if len(out) < len(sig):
        out = np.pad(out, (0, len(sig) - len(out)))
    return out, fp


# ---------- detection ----------
def _features(sig):
    f, t, Z = stft(sig, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    L = np.log(np.abs(Z[band_bins()]) + 1e-9)
    hpF = L - uniform_filter1d(L, size=HP_F, axis=0, mode="nearest")
    hpT = L - uniform_filter1d(L, size=HP_T, axis=1, mode="nearest")
    hpFT = hpF - uniform_filter1d(hpF, size=HP_T, axis=1, mode="nearest")
    return {"freq": hpF, "time": hpT, "image": hpFT}


def _block_corr(H, S):
    """Correlation between feature H and perturbation S, per block of BLOCK frames."""
    rows = np.abs(S).sum(1) > 0
    nb = H.shape[1] // BLOCK
    a = H[rows, : nb * BLOCK].reshape(rows.sum(), nb, BLOCK)
    s = S[rows, : nb * BLOCK].reshape(rows.sum(), nb, BLOCK).astype(np.float64)
    a = a - a.mean(axis=(0, 2), keepdims=True)
    s = s - s.mean(axis=(0, 2), keepdims=True)
    num = (a * s).sum(axis=(0, 2))
    den = np.sqrt((a ** 2).sum(axis=(0, 2)) * (s ** 2).sum(axis=(0, 2))) + 1e-12
    return num / den


def verify(sig, key, processes=PROCESSES, n_fractals=N_FRACTALS, n_null=6,
           use_fingerprint=False):
    """Key holder. Returns per-block z-scores: dict[(proc,k)] and fused array.
    Null distribution: the same test with WRONG keys (honest null)."""
    fp = fingerprint(sig) if use_fingerprint else "0"
    feats = _features(sig)
    nb_bins, n_frames = feats["freq"].shape
    z = {}
    for p in processes:
        for k in range(n_fractals):
            true = _block_corr(feats[p], perturbation(key, p, k, nb_bins, n_frames, fp))
            nulls = np.concatenate([
                _block_corr(feats[p], perturbation(b"null-%d" % i, p, k, nb_bins, n_frames, fp))
                for i in range(n_null)])
            z[(p, k)] = (true - nulls.mean()) / (nulls.std() + 1e-12)
    fused = sum(z.values()) / np.sqrt(len(z))                 # Stouffer
    per_proc = {p: sum(z[(p, k)] for k in range(n_fractals)) / np.sqrt(n_fractals)
                for p in processes}
    return z, per_proc, fused


# ---------- blind attack on the 'freq' process (finding 1 of the paper) ----------
def blind_attack_freq(sig, key, target_k=0, grid_r=15, grid_s=24):
    """An attacker who knows the METHOD but not the key scans (r, phase) per block
    and keeps the best correlation. Returns the fraction of blocks where the
    maximum locks onto fractal `target_k` (r within 0.02, phase within 0.05)
    and onto ANY of the embedded fractals, plus the mean confidence."""
    hpF = _features(sig)["freq"]
    nbins, n_frames = hpF.shape
    x = np.arange(nbins) / (nbins - 1)
    rs = np.linspace(R_MIN, R_MAX, grid_r)
    ss = np.linspace(0, 1, grid_s, endpoint=False)
    M = np.array([2 * cantor_mask(r, (x + s) % 1.0, LEVELS["freq"]) - 1
                  for r in rs for s in ss])                    # (grid_r*grid_s, nbins)
    M = M - M.mean(1, keepdims=True)
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    nb = n_frames // BLOCK
    params = [freq_params(key, k, n_frames) for k in range(N_FRACTALS)]
    hit_target, hit_any, conf = 0, 0, []
    for b in range(nb):
        seg = hpF[:, b * BLOCK:(b + 1) * BLOCK]
        seg = seg - seg.mean(0)
        seg = seg / (np.linalg.norm(seg, axis=0) + 1e-12)
        sc = (M @ seg).mean(1)
        i = sc.argmax(); conf.append(sc[i])
        r_hat, s_hat = rs[i // grid_s], ss[i % grid_s]
        def match(k):
            s, r_t = params[k]
            ds = abs((s_hat - s + 0.5) % 1.0 - 0.5)
            return abs(r_hat - r_t[b * BLOCK:(b + 1) * BLOCK].mean()) < 0.02 and ds < 0.05
        hit_target += match(target_k)
        hit_any += any(match(k) for k in range(N_FRACTALS))
    return hit_target / nb, hit_any / nb, float(np.mean(conf))


# ---------- experiment utilities ----------
def make_test_signal(seconds=24, seed=1):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    F = np.fft.rfft(rng.standard_normal(n))
    fr = np.fft.rfftfreq(n, 1 / SR); fr[0] = 1
    pink = np.fft.irfft(F / np.sqrt(fr), n)
    pink /= np.abs(pink).max()
    tt = np.arange(n) / SR
    tones = sum(0.15 / (k + 1) * np.sin(2 * np.pi * 220 * (k + 1) * tt
                + 3 * np.sin(2 * np.pi * 0.3 * tt)) for k in range(8))
    env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt)
    sig = (0.5 * pink + tones) * env
    return (0.8 * sig / np.abs(sig).max()).astype(np.float64)


def codec_roundtrip(sig, codec="mp3", bitrate="128k"):
    with tempfile.TemporaryDirectory() as d:
        w, c, o = (os.path.join(d, n) for n in ("a.wav", "a." + codec, "b.wav"))
        wavfile.write(w, SR, (sig * 32767).astype(np.int16))
        enc = {"mp3": "libmp3lame", "aac": "aac", "opus": "libopus"}[codec]
        ext = ["-ar", "48000"] if codec == "opus" else []
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-c:a", enc,
                        "-b:a", bitrate, *ext, c], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", c, "-ar", str(SR),
                        "-ac", "1", o], check=True)
        sr, y = wavfile.read(o)
    y = y.astype(np.float64) / 32767
    out = np.zeros(len(sig)); n = min(len(y), len(sig)); out[:n] = y[:n]
    return out


def snr_db(ref, x):
    n = min(len(ref), len(x))
    return 10 * np.log10(np.sum(ref[:n] ** 2) / np.sum((ref[:n] - x[:n]) ** 2))


def _fmt(z):
    return f"{np.mean(z):6.1f}"


if __name__ == "__main__":
    key = b"demo-secret-key"
    orig, other = make_test_signal(), make_test_signal(seed=7)
    print(f"v0.2: {len(PROCESSES)} processes x {N_FRACTALS} independent fractals "
          f"= {len(PROCESSES) * N_FRACTALS} hidden objects\n")

    # 1. strength / imperceptibility / compression sweep (fused z, mean over blocks)
    print("== delta sweep (per-fractal amplitude): SNR and fused tier-3 z ==")
    print(f"{'delta':>6} {'SNR(dB)':>8} {'clean':>7} {'mp3_128k':>9} {'mp3_64k':>8} "
          f"{'aac_96k':>8} {'opus_64k':>9}")
    for delta in (0.02, 0.04):
        wm, _ = embed(orig, key, delta=delta)
        row = [f"{delta:6.2f}", f"{snr_db(orig, wm):8.1f}", f"{verify(wm, key)[2].mean():7.1f}"]
        for codec, br in (("mp3", "128k"), ("mp3", "64k"), ("aac", "96k"), ("opus", "64k")):
            row.append(f"{verify(codec_roundtrip(wm, codec, br), key)[2].mean():8.1f}")
        print(" ".join(row))

    # 2. per-process breakdown after MP3 128k, controls
    delta = 0.04
    wm, _ = embed(orig, key, delta=delta)
    z, per, fused = verify(codec_roundtrip(wm, "mp3", "128k"), key)
    print("\n== Per process after MP3 128k (delta=0.04), mean z over blocks ==")
    for p in PROCESSES:
        print(f"{p:>6}: fused {_fmt(per[p])} | fractals "
              + " ".join(_fmt(z[(p, k)]) for k in range(N_FRACTALS)))
    print(f"unmarked control: fused z = {verify(orig, key)[2].mean():.1f} | "
          f"wrong key: fused z = {verify(wm, b'wrong-key')[2].mean():.1f}")

    # 3. splice test: 8-11 s replaced by unmarked audio, then MP3 128k
    a, b = int(8 * SR), int(11 * SR)
    forged = wm.copy()
    forged[a:b] = other[a:b] * (np.abs(wm[a:b]).max() / np.abs(other[a:b]).max())
    _, _, zf = verify(codec_roundtrip(forged, "mp3", "128k"), key)
    blk = BLOCK * HOP / SR
    tb = np.arange(len(zf)) * blk
    inside = (tb + blk > 8) & (tb < 11)
    flagged = zf < 0.5 * np.median(zf[~inside])
    print(f"\n== Splice 8-11 s + MP3 128k (blocks of {blk:.2f} s) ==")
    print(f"fused z untouched: mean {zf[~inside].mean():.1f} (min {zf[~inside].min():.1f}) | "
          f"spliced: mean {zf[inside].mean():.1f} (max {zf[inside].max():.1f})")
    print(f"flagged {flagged.sum()}/{len(zf)}; all spliced flagged: {flagged[inside].all()}; "
          f"false flags: {flagged[~inside].sum()}")

    # 4. blind attack on the 'freq' process: 1 fractal vs 3 fractals
    print("\n== Blind attack on 'freq' (scan of r and phase per block) ==")
    for nf in (1, 3):
        w, _ = embed(orig, key, delta=0.10, processes=("freq",), n_fractals=nf)
        t, anyk, conf = blind_attack_freq(w, key)
        print(f"{nf} fractal(s): locks on fractal 0 in {t:.0%} of blocks, on any in {anyk:.0%}; "
              f"mean confidence {conf:.2f}")
    print(f"unmarked: mean confidence {blind_attack_freq(orig, key)[2]:.2f}")

    # 5. fingerprint stability (open problem, unchanged from v0.1)
    fp0 = fingerprint(orig)
    ham = lambda a, b: sum(x != y for x, y in zip(a, b))
    print("\n== Fingerprint stability (15 bits) ==")
    print(f"after embedding only: {ham(fp0, fingerprint(wm))} bit(s) differ")
    for codec, br in (("mp3", "128k"), ("aac", "96k")):
        print(f"after embedding + {codec} {br}: "
              f"{ham(fp0, fingerprint(codec_roundtrip(wm, codec, br)))} bit(s) differ")