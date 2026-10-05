"""Tests for atlas_mpl_style.utils module."""

import unittest
import numpy as np
import atlas_mpl_style.utils as utils


class TestUtilsModule(unittest.TestCase):
    def test_significance_calculation(self):
        data = np.array([120.0, 80.0, 100.0])
        data_errs = np.sqrt(data)
        bkg = np.array([100.0, 100.0, 100.0])
        bkg_errs = np.array([10.0, 10.0, 10.0])

        sig = utils.significance(data, data_errs, bkg, bkg_errs)
        self.assertEqual(len(sig), 3)

        # When data > bkg, significance should be positive
        self.assertGreater(sig[0], 0.0)

        # When data < bkg, significance should be negative
        self.assertLess(sig[1], 0.0)

        # When data == bkg, significance should be approximately 0.0
        self.assertAlmostEqual(sig[2], 0.0, places=5)


if __name__ == "__main__":
    unittest.main()
