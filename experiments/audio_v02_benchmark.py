#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Jean Camille d'Ornano; protocole exploratoire.
"""Campagne audio reproductible, à lancer: python experiments/audio_v02_benchmark.py

Les métriques calculées sont descriptives. Les taux de fausses alarmes avec peu
de clés ne constituent ni des probabilités de sécurité ni des p-values fiables.
"""
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.signal import resample_poly

import fractal_wm as wm


def perturb_audio(sig, name, rng):
    if name == "clean":
        return sig.copy()
    if name == "noise_40db":
        noise = rng.standard_normal(len(sig))
        noise *= np.linalg.norm(sig) / (np.linalg.norm(noise) * 100)
        return sig + noise
    if name == "time_shift_50ms":
        n = round(0.05 * wm.SR)
        return np.pad(sig[:-n], (n, 0))
    if name == "trim_100ms":
        n = round(0.1 * wm.SR)
        return np.pad(sig[n:], (0, n))
    if name == "resample_48k_44k":
        return resample_poly(resample_poly(sig, 160, 147), 147, 160)[:len(sig)]
    if name == "mp3_128k":
        return wm.codec_roundtrip(sig, "mp3", "128k")
    if name == "aac_96k":
        return wm.codec_roundtrip(sig, "aac", "96k")
    raise ValueError(name)


def score(sig, key):
    _, per, fused = wm.verify(sig, key, n_null=6)
    return {"mean_fused_z": float(np.mean(fused)),
            "per_process_mean_z": {p: float(np.mean(v)) for p, v in per.items()},
            "n_blocks": int(len(fused))}


def run():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--seeds", type=int, nargs="+", default=[11, 29])
    ap.add_argument("--deltas", type=float, nargs="+", default=[0.02, 0.04])
    ap.add_argument("--output", default="")
    ap.add_argument("--no-codecs", action="store_true")
    args = ap.parse_args()
    if args.seconds < 1 or not args.seeds or not args.deltas:
        ap.error("seconds >= 1; seeds et deltas non vides")
    attacks = ["clean", "noise_40db", "time_shift_50ms", "trim_100ms",
               "resample_48k_44k"]
    if not args.no_codecs:
        attacks.extend(["mp3_128k", "aac_96k"])
    report = {
        "status": "experimental", "date_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "fractal_wm.py v0.2; no source modification",
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__, "scipy": scipy.__version__,
                        "ffmpeg": subprocess.run(["ffmpeg", "-version"],
                          capture_output=True, text=True).stdout.splitlines()[0]},
        "parameters": {"seconds": args.seconds, "seeds": args.seeds,
                       "deltas": args.deltas, "n_null_internal": 6,
                       "attacks": attacks},
        "limitations": [
          "Synthetic signals only; no subjective listening or perceptual metric",
          "Scores are exploratory; n_null=6 and correlated fractals do not calibrate FPR",
          "One marked key per seed; no independent large-scale impostor distribution",
          "Shifts and trims have no synchronization correction",
          "Codec alignment/encoder delay not estimated",
          "No cryptographic security or watermark unforgeability claim"],
        "observations": []}
    for seed in args.seeds:
        orig = wm.make_test_signal(seconds=args.seconds, seed=seed)
        key = ("research-key-%d" % seed).encode()
        wrong = ("wrong-key-%d" % seed).encode()
        for delta in args.deltas:
            marked, fingerprint = wm.embed(orig, key, delta=delta)
            row = {"seed": seed, "delta": delta, "fingerprint": fingerprint,
                   "snr_db": float(wm.snr_db(orig, marked)),
                   "unmarked_control": score(orig, key),
                   "wrong_key_control": score(marked, wrong),
                   "attacks": {}}
            for name in attacks:
                try:
                    y = perturb_audio(marked, name, np.random.default_rng(seed + 719))
                    row["attacks"][name] = {
                        "score": score(y, key),
                        "snr_to_marked_db": float(wm.snr_db(marked, y))}
                except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                    row["attacks"][name] = {
                        "status": "unavailable", "reason": str(exc)}
            report["observations"].append(row)
            print("seed=%d delta=%.3f SNR=%.2f clean_z=%.3f" % (
                 seed, delta, row["snr_db"],
                 row["attacks"]["clean"]["score"]["mean_fused_z"]), flush=True)
    text = json.dumps(report, indent=2, allow_nan=False)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
        print("Wrote", path)
    else:
        print(text)


if __name__ == "__main__":
    run()
