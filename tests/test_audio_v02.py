# Tests de non-régression du prototype audio v0.2
# Copyright (c) 2026 Jean Camille d'Ornano; contribution de recherche.
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Tests exécutables : python -m unittest discover -s tests -v.

Ces tests sont des contrôles d'implémentation, pas une preuve de robustesse,
d'imperceptibilité ou de sécurité.
"""
import unittest
import numpy as np

import fractal_wm as wm


class TestAudioV02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.signal = wm.make_test_signal(seconds=2, seed=37)
        cls.key = b"test-only-key-not-secret"

    def test_cantor_endpoints_and_dimension(self):
        for levels in (1, 3, 5):
            starts, length = wm.cantor_starts(1 / 3, levels)
            self.assertEqual(len(starts), 2 ** levels)
            self.assertAlmostEqual(length, 3 ** (-levels))
            self.assertEqual(float(wm.cantor_mask(1 / 3, np.array([0.0]), levels)[0]), 1.0)
        self.assertAlmostEqual(wm.dim(1 / 3), np.log(2) / np.log(3))

    def test_all_nine_masks_and_key_separation(self):
        # Vérifie seulement la génération déterministe et les dimensions.
        nbins, nframes = len(wm.band_bins()), 3 * wm.BLOCK
        masks = {}
        for proc in wm.PROCESSES:
            for k in range(wm.N_FRACTALS):
                m = wm.perturbation(self.key, proc, k, nbins, nframes)
                self.assertEqual(m.shape, (nbins, nframes))
                self.assertTrue(np.all(np.isin(m, (-1, 0, 1))))
                np.testing.assert_array_equal(
                    m, wm.perturbation(self.key, proc, k, nbins, nframes))
                masks[(proc, k)] = m
            self.assertFalse(np.array_equal(masks[(proc, 0)], masks[(proc, 1)]))

    def test_short_window_supported(self):
        # max(n - 1, 1) garantit des abscisses strictement croissantes.
        m = wm.perturbation(self.key, "time", 0, len(wm.band_bins()), 12)
        self.assertEqual(m.shape, (len(wm.band_bins()), 12))

    def test_embed_preserves_length_and_finite_outputs(self):
        marked, fp = wm.embed(self.signal, self.key, delta=0.02)
        self.assertEqual(len(marked), len(self.signal))
        self.assertEqual(fp, "0")  # Fingerprint désactivé par défaut.
        self.assertTrue(np.isfinite(marked).all())
        self.assertTrue(np.isfinite(wm.snr_db(self.signal, marked)))
        self.assertGreater(np.linalg.norm(marked - self.signal), 0)

    def test_full_detector_smoke(self):
        marked, _ = wm.embed(self.signal, self.key, delta=0.02)
        z, per_process, fused = wm.verify(marked, self.key, n_null=3)
        self.assertEqual(len(z), 9)
        self.assertEqual(set(per_process), set(wm.PROCESSES))
        self.assertEqual(len(fused), wm._features(marked)["freq"].shape[1] // wm.BLOCK)
        self.assertGreater(len(fused), 0)
        self.assertTrue(np.isfinite(fused).all())
        # Aucune assertion « vraie clé > mauvaise clé » sur 2 s :
        # ce serait une généralisation scientifique injustifiée.


if __name__ == "__main__":
    unittest.main()
