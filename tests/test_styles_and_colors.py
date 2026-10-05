"""Tests for styles, color cycles, extra colors, and colormaps."""

import unittest
from unittest.mock import patch
import matplotlib as mpl
import matplotlib.pyplot as plt
import atlas_mpl_style as ampl


class TestStylesAndColors(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_use_atlas_style_default(self):
        ampl.use_atlas_style()
        self.assertFalse(mpl.rcParams["text.usetex"])
        self.assertEqual(mpl.rcParams["mathtext.default"], "regular")
        self.assertFalse(mpl.rcParams["legend.frameon"])
        self.assertEqual(ampl.plot._atlas_label, "ATLAS")
        self.assertFalse(ampl.plot._usetex)
        self.assertTrue(mpl.rcParams["xtick.minor.visible"])
        self.assertTrue(mpl.rcParams["ytick.minor.visible"])

    def test_use_atlas_style_fancy_legend(self):
        mpl.rcParams["legend.frameon"] = True
        ampl.use_atlas_style(fancyLegend=True)
        self.assertTrue(mpl.rcParams["legend.frameon"])

    def test_use_atlas_style_custom_label(self):
        ampl.use_atlas_style(atlasLabel="CMS")
        self.assertEqual(ampl.plot._atlas_label, "CMS")
        ampl.use_atlas_style(atlasLabel="ATLAS")

    def test_use_atlas_style_usetex_fallback_warning(self):
        with patch("shutil.which", return_value=None):
            with self.assertWarns(UserWarning):
                ampl.use_atlas_style(usetex=True)
            self.assertFalse(mpl.rcParams["text.usetex"])
            self.assertFalse(ampl.plot._usetex)

    def test_use_atlas_style_usetex_success(self):
        with patch("shutil.which", return_value="/usr/bin/mock_latex"):
            ampl.use_atlas_style(usetex=True)
            self.assertTrue(ampl.plot._usetex)
            self.assertIn("siunitx", mpl.rcParams["text.latex.preamble"])
            # Reset
            ampl.use_atlas_style(usetex=False)

    def test_stylesheets_available(self):
        for style_name in ("atlas", "paper", "print", "slides"):
            plt.style.use(style_name)
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 1])
            plt.close(fig)

    def test_registered_colors(self):
        color_names = [
            "petroff:blue",
            "petroff:orange",
            "petroff:red",
            "petroff:gray",
            "petroff:purple",
            "petroff:brown",
            "petroff:orange2",
            "petroff:tan",
            "petroff:gray2",
            "petroff:lightBlue",
            "paper:bg",
            "paper:fg",
            "paper:bgAlt",
            "paper:red",
            "paper:green",
            "paper:blue",
            "paper:yellow",
            "paper:orange",
            "paper:pink",
            "paper:purple",
            "paper:lightBlue",
            "paper:olive",
            "on:bg",
            "on:fg",
            "on:bgAlt",
            "on:fgAlt",
            "on:red",
            "on:orange",
            "on:yellow",
            "on:green",
            "on:cyan",
            "on:blue",
            "on:pink",
            "on:brown",
            "hdbs:starcommandblue",
            "hdbs:spacecadet",
            "hdbs:mintcream",
            "hdbs:outrageousorange",
            "hdbs:pictorialcarmine",
            "hdbs:maroonX11",
            "hh:darkblue",
            "hh:darkpink",
            "hh:darkyellow",
            "hh:medturquoise",
            "hh:lightturquoise",
            "hh:offwhite",
            "atlas:onesigma",
            "atlas:twosigma",
            "transparent",
        ]
        for c in color_names:
            rgba = mpl.colors.to_rgba(c)
            self.assertEqual(len(rgba), 4)

        # Transparent alpha check
        rgba_trans = mpl.colors.to_rgba("transparent")
        self.assertEqual(rgba_trans[3], 0.0)

    def test_bird_colormap(self):
        cmap = mpl.colormaps["bird"]
        self.assertIsNotNone(cmap)
        val = cmap(0.5)
        self.assertEqual(len(val), 4)

    def test_set_color_cycle(self):
        # Default / None
        ampl.set_color_cycle(None)
        # ATLAS with various n
        ampl.set_color_cycle("ATLAS", n=1)
        ampl.set_color_cycle("ATLAS", n=6)
        ampl.set_color_cycle("ATLAS", n=8)
        ampl.set_color_cycle("ATLAS", n=10)
        # Petroff prefix
        ampl.set_color_cycle("Petroff", n=6)
        ampl.set_color_cycle("Petroff", n=8)
        ampl.set_color_cycle("Petroff", n=10)
        # Other palettes
        ampl.set_color_cycle("Paper")
        ampl.set_color_cycle("Oceanic")
        ampl.set_color_cycle("MPL")
        ampl.set_color_cycle("Tab")
        ampl.set_color_cycle("Tableau")
        ampl.set_color_cycle("HDBS")
        ampl.set_color_cycle("HH")
        ampl.set_color_cycle("series_other")


if __name__ == "__main__":
    unittest.main()
