"""Comprehensive tests for atlas_mpl_style.plot module."""

import unittest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import atlas_mpl_style as ampl
from atlas_mpl_style.plot import (
    Background,
    BinningMismatchError,
    plot_band,
    register_band,
    plot_backgrounds,
    plot_signal,
    plot_data,
    plot_ratio,
    draw_tag,
    plot_1d,
    plot_2d,
    plot_cutflow,
    plot_limit,
    set_xlabel,
    set_ylabel,
    set_zlabel,
    draw_atlas_label,
    draw_legend,
)


class TestPlotModule(unittest.TestCase):
    def setUp(self):
        ampl.use_atlas_style()

    def tearDown(self):
        plt.close("all")

    def test_background_class_and_methods(self):
        hist = np.array([10.0, 20.0, 30.0])
        stat_errs = np.array([1.0, 2.0, 3.0])
        syst_errs = np.array([0.5, 1.0, 1.5])
        bkg = Background("Bkg1", hist, stat_errs=stat_errs, syst_errs=syst_errs, color="paper:blue")

        self.assertEqual(bkg.label, "Bkg1")
        self.assertEqual(bkg.color, "paper:blue")
        np.testing.assert_array_equal(bkg.hist, hist)
        np.testing.assert_array_equal(bkg.stat_errs, stat_errs)
        np.testing.assert_array_equal(bkg.syst_errs, syst_errs)

        # Test errors
        with self.assertRaises(TypeError):
            Background("InvalidStat", hist, stat_errs="invalid_stat")

        with self.assertRaises(BinningMismatchError):
            Background("MismatchStat", hist, stat_errs=np.array([1.0, 2.0]))

        with self.assertRaises(BinningMismatchError):
            Background("MismatchSyst", hist, syst_errs=np.array([1.0, 2.0]))

    def test_plot_band_and_register_band(self):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax2)

        bins = np.array([0, 1, 2, 3])
        low = np.array([1, 2, 3])
        high = np.array([4, 5, 6])

        # Test plot_band with explicit ax=ax1
        poly = plot_band(bins, low, high, label="Band1", ax=ax1, color="red")
        self.assertEqual(len(ax1.collections), 1)
        self.assertEqual(len(ax2.collections), 0)
        self.assertIn("Band1", ax1._ampllegend.bands)

        # Test register_band
        register_band("CustomBand", poly, ax=ax2)
        self.assertIn("CustomBand", ax2._ampllegend.bands)

    def test_plot_backgrounds(self):
        bins = np.array([0, 1, 2, 3])
        bkg1 = Background("Bkg1", np.array([10, 20, 30]), stat_errs=np.array([1, 2, 3]), syst_errs=np.array([0.5, 1, 1.5]))
        bkg2 = Background("Bkg2", np.array([5, 10, 15]), stat_errs=np.array([0.5, 1, 1.5]))

        # Standard call with show_errs=True
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax2)
        total = plot_backgrounds([bkg1, bkg2], bins, show_errs=True, ax=ax1)
        np.testing.assert_array_equal(total[0], np.array([15, 30, 45]))
        # Bands must be on ax1, not ax2
        self.assertGreater(len(ax1.collections), 0)
        self.assertEqual(len(ax2.collections), 0)
        plt.close(fig)

        # Swapped arguments backwards compatibility: plot_backgrounds(bins, backgrounds)
        fig, ax = plt.subplots()
        total_swapped = plot_backgrounds(bins, [bkg1, bkg2], ax=ax)
        np.testing.assert_array_equal(total_swapped[0], np.array([15, 30, 45]))
        plt.close(fig)

        # Total err override and empty_stat_legend
        fig, ax = plt.subplots()
        plot_backgrounds([bkg1], bins, show_errs=True, total_err=np.array([10.0, 10.0, 10.0]), empty_stat_legend=True, ax=ax)
        self.assertTrue(ax._ampllegend.has_syst)
        self.assertTrue(ax._ampllegend.has_stat)
        plt.close(fig)

    def test_plot_signal(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([5, 10, 15])
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax2)

        # String stat_errs and syst_errs with attach_bands=True
        plot_signal("Sig", bins, hist, stat_errs="sqrt", syst_errs=np.array([1, 2, 3]), attach_bands=True, ax=ax1)
        self.assertIn("Sig", ax1._ampllegend.line_hists)
        self.assertEqual(len(ax2.collections), 0)

        # Invalid stat_errs
        with self.assertRaises(TypeError):
            plot_signal("BadSig", bins, hist, stat_errs="invalid", ax=ax1)

        with self.assertRaises(BinningMismatchError):
            plot_signal("BadSigLen", bins, hist, stat_errs=np.array([1, 2]), ax=ax1)

        plt.close(fig)

    def test_plot_data(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([10, 20, 30])
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax2)

        # Default Poisson errors
        plot_data(bins, hist, ax=ax1)
        self.assertIn("Data", ax1._ampllegend.data_hists)
        self.assertEqual(len(ax2.lines), 0)

        # String stat_errs
        plot_data(bins, hist, stat_errs="sqrt", ax=ax1)

        # Array stat_errs
        plot_data(bins, hist, stat_errs=np.array([1, 2, 3]), ax=ax1)

        # Bin mismatch
        with self.assertRaises(BinningMismatchError):
            plot_data(np.array([0, 1]), hist, ax=ax1)

        plt.close(fig)

    def test_plot_ratio(self):
        bins = np.array([0, 1, 2, 3])
        data = np.array([10, 20, 30])
        data_errs = np.array([3, 4, 5])
        bkg = np.array([10, 18, 32])
        bkg_errs = np.array([2, 3, 4])

        fig, rax = plt.subplots()
        # plottype="diff"
        plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax=rax, plottype="diff")

        # plottype="raw" with offscale_errs and max_ratio
        plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax=rax, max_ratio=2.0, plottype="raw", offscale_errs=True)

        # Invalid plottype
        with self.assertRaises(TypeError):
            plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax=rax, plottype="invalid")

        plt.close(fig)

    def test_draw_tag(self):
        fig, ax = plt.subplots()
        draw_tag("Preliminary", ax=ax)
        self.assertEqual(len(ax.texts), 1)
        self.assertEqual(ax.texts[0].get_text(), "Preliminary")
        plt.close(fig)

    def test_plot_1d(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([10, 20, 30])

        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax2)

        # Test ax parameter is honored for both hist and stat band
        plot_1d("1DTest", bins, hist, stat_errs="sqrt", attach_bands=True, ax=ax1)
        self.assertEqual(len(ax1.collections), 1)
        self.assertEqual(len(ax2.collections), 0)
        self.assertIn("1DTest", ax1._ampllegend.line_hists)

        # Invalid binning
        with self.assertRaises(BinningMismatchError):
            plot_1d("BadBin", np.array([0, 1]), hist, ax=ax1)

        plt.close(fig)

    def test_plot_2d(self):
        xbins = np.array([0, 1, 2])
        ybins = np.array([0, 1, 2, 3])
        hist = np.array([[1, 2, 3], [4, 5, 6]])

        fig, ax = plt.subplots()
        mesh, cbar = plot_2d(xbins, ybins, hist, ax=ax, pad=0.1)
        self.assertIsNotNone(mesh)
        self.assertIsNotNone(cbar)

        # Mismatch errors
        with self.assertRaises(BinningMismatchError):
            plot_2d(np.array([0, 1]), ybins, hist, ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_2d(xbins, np.array([0, 1]), hist, ax=ax)

        plt.close(fig)

    def test_plot_cutflow(self):
        labels = ["Initial", "Cut 1", "Cut 2"]
        hist = np.array([1000, 500, 100])

        # Horizontal cutflow
        fig, ax = plt.subplots()
        plot_cutflow(labels, hist, horizontal=True, text=True, ax=ax)
        self.assertEqual(len(ax.patches), 3)
        self.assertEqual(len(ax.texts), 3)
        plt.close(fig)

        # Vertical cutflow
        fig, ax = plt.subplots()
        plot_cutflow(labels, hist, horizontal=False, text=True, textcolor="red", ax=ax)
        self.assertEqual(len(ax.patches), 3)
        self.assertEqual(len(ax.texts), 3)
        plt.close(fig)

        # Binning mismatch
        with self.assertRaises(BinningMismatchError):
            plot_cutflow(["A", "B"], hist)

    def test_plot_limit(self):
        x = np.array([100, 200, 300, 400])
        expected = np.array([10.0, 5.0, 2.5, 1.0])
        m1 = expected * 0.8
        p1 = expected * 1.2
        m2 = expected * 0.6
        p2 = expected * 1.4
        observed = expected * 1.1

        fig, ax = plt.subplots()
        plot_limit(
            "Exp. Limit",
            x,
            expected,
            minus_one_sigma=m1,
            plus_one_sigma=p1,
            minus_two_sigma=m2,
            plus_two_sigma=p2,
            observed_label="Obs. Limit",
            observed=observed,
            ax=ax,
        )
        self.assertIn("Exp. Limit", ax._ampllegend.limits)
        self.assertTrue(ax._ampllegend.limits["Exp. Limit"].has_obs)

        # Draw limit legend
        draw_legend(ax=ax)
        self.assertIsNotNone(ax.get_legend())

        # Validation errors in plot_limit
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadExp", x, expected[:2], ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadM1", x, expected, minus_one_sigma=m1[:2], plus_one_sigma=p1, ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadP1", x, expected, minus_one_sigma=m1, plus_one_sigma=p1[:2], ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadM2", x, expected, minus_two_sigma=m2[:2], plus_two_sigma=p2, ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadP2", x, expected, minus_two_sigma=m2, plus_two_sigma=p2[:2], ax=ax)
        with self.assertRaises(BinningMismatchError):
            plot_limit("BadObs", x, expected, observed=observed[:2], observed_label="Obs", ax=ax)
        with self.assertRaises(ValueError):
            plot_limit("BadOneSig", x, expected, minus_one_sigma=m1, ax=ax)
        with self.assertRaises(ValueError):
            plot_limit("BadTwoSig", x, expected, minus_two_sigma=m2, ax=ax)
        with self.assertRaises(ValueError):
            plot_limit("BadObsPair", x, expected, observed=observed, ax=ax)
        plt.close(fig)

    def test_label_setters(self):
        fig, ax, rax = ampl.ratio_axes()

        # set_xlabel on main axis should set label on low_ax (rax)
        set_xlabel("X Label", ax=ax)
        self.assertEqual(rax.get_xlabel(), "X Label")

        # Custom kwargs
        set_xlabel("Custom X", ax=rax, ha="center", x=0.5)
        self.assertEqual(rax.get_xlabel(), "Custom X")

        # set_ylabel with ratio_axes
        set_ylabel("Y Label Main", ax=ax)
        set_ylabel("Y Label Ratio", ax=rax)
        self.assertEqual(ax.get_ylabel(), "Y Label Main")
        self.assertEqual(rax.get_ylabel(), "Y Label Ratio")

        # set_zlabel with colorbar explicit and implicit from ax
        fig2, ax2 = plt.subplots()
        _, cbar = plot_2d(np.array([0, 1]), np.array([0, 1]), np.array([[1]]), ax=ax2)
        set_zlabel("Z Value Explicit", cbar=cbar, ax=ax2)
        set_zlabel("Z Value Implicit", ax=ax2)

        # set_zlabel on plain ax should raise ValueError
        fig3, ax3 = plt.subplots()
        with self.assertRaises(ValueError):
            set_zlabel("Bad Z", ax=ax3)

        plt.close(fig)
        plt.close(fig2)
        plt.close(fig3)

    def test_draw_atlas_label_variants(self):
        statuses = ["int", "internal", "pre", "preliminary", "public", "final", "opendata", None, "Custom Status"]
        for st in statuses:
            fig, ax = plt.subplots()
            draw_atlas_label(0.1, 0.9, ax=ax, status=st, simulation=True, energy="13 TeV", lumi=140, desc="Test Description")
            self.assertEqual(len(ax.texts), 1)
            txt = ax.texts[0].get_text()
            self.assertIn(r"\mathbfit{ATLAS}", txt)
            if st == "opendata":
                self.assertIn("for education only", txt)
            else:
                self.assertIn(r"\mathit{s}", txt)
            plt.close(fig)

        # Test lumi without energy (no leading comma)
        fig, ax = plt.subplots()
        draw_atlas_label(0.1, 0.9, ax=ax, status="final", energy=None, lumi=140, lumi_lt=True)
        txt = ax.texts[0].get_text()
        self.assertNotIn(", $", txt)
        self.assertIn("<", txt)
        plt.close(fig)

    def test_draw_legend(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([10, 20, 30])
        fig, ax = plt.subplots()

        plot_data(bins, hist, ax=ax, label="Data")
        plot_1d("LineHist", bins, hist, ax=ax)
        plot_signal("Signal", bins, hist, stat_errs="sqrt", ax=ax)
        bkg = Background("Bkg", hist)
        plot_backgrounds([bkg], bins, ax=ax)

        # Matplotlib artists plotted directly on ax are picked up as extras
        ax.plot([0, 1], [0, 1], color="orange", label="Extra Line")
        draw_legend(ax=ax, ncols=2)
        self.assertIsNotNone(ax.get_legend())
        leg_labels = [t.get_text() for t in ax.get_legend().get_texts()]
        self.assertIn("Extra Line", leg_labels)
        plt.close(fig)

    def test_draw_legend_with_band_handler(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([10, 20, 30])
        fig, ax = plt.subplots()
        plot_1d("1D_with_band", bins, hist, stat_errs="sqrt", attach_bands=True, ax=ax)
        plot_signal("Sig_with_band", bins, hist, stat_errs="sqrt", attach_bands=True, ax=ax)
        draw_legend(ax=ax)
        self.assertIsNotNone(ax.get_legend())
        fig.canvas.draw()  # Triggers BandHandler.create_artists
        plt.close(fig)

    def test_draw_legend_multiple_limits(self):
        x = np.array([100, 200, 300])
        y1 = np.array([10.0, 5.0, 2.5])
        y2 = np.array([8.0, 4.0, 2.0])
        fig, ax = plt.subplots()
        plot_limit("Model A", x, y1, minus_one_sigma=y1*0.8, plus_one_sigma=y1*1.2, observed_label="Obs A", observed=y1*1.1, color="paper:blue", ax=ax)
        plot_limit("Model B", x, y2, minus_one_sigma=y2*0.8, plus_one_sigma=y2*1.2, observed_label="Obs B", observed=y2*1.1, color="paper:red", ax=ax)
        draw_legend(ax=ax)
        self.assertIsNotNone(ax.get_legend())
        plt.close(fig)

    def test_draw_legend_empty_axes(self):
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1], label="Line")
        draw_legend(ax=ax)
        self.assertIsNotNone(ax.get_legend())
        plt.close(fig)

    def test_default_axes_calls(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([10, 20, 30])
        fig = plt.figure()
        # All of these should use plt.gca()
        plot_data(bins, hist)
        plot_1d("1DDef", bins, hist)
        draw_tag("DefaultTag")
        plt.close(fig)

        # plot_cutflow with resize_ax
        fig2 = plt.figure()
        plot_cutflow(["Cut1", "Cut2"], [10, 5], horizontal=True)
        plt.close(fig2)

        fig3 = plt.figure()
        plot_cutflow(["Cut1", "Cut2"], [10, 5], horizontal=False)
        plt.close(fig3)

        # plot_2d default ax
        fig4 = plt.figure()
        plot_2d(np.array([0, 1]), np.array([0, 1]), np.array([[1]]))
        plt.close(fig4)

    def test_background_string_stat_errs(self):
        hist = np.array([10.0, 20.0, 30.0])
        bkg_pois = Background("BkgPois", hist, stat_errs="pois")
        np.testing.assert_array_equal(bkg_pois.stat_errs, np.sqrt(hist))

        bkg_ignore = Background("BkgIgnore", hist, stat_errs="ignore")
        np.testing.assert_array_equal(bkg_ignore.stat_errs, np.zeros_like(hist))

    def test_format_sci_notation(self):
        from atlas_mpl_style.plot import _formatSciNotation
        self.assertEqual(_formatSciNotation(10), "10")
        self.assertEqual(_formatSciNotation(100000), r"$10^{5}$")
        self.assertEqual(_formatSciNotation(250000), r"$2.5{\times}10^{5}$")
        self.assertEqual(_formatSciNotation(1e-5), r"$10^{-5}$")
        self.assertEqual(_formatSciNotation(2.5e-5), r"$2.5{\times}10^{-5}$")

    def test_ratio_axes_multiple(self):
        # Multiple ratio axes
        fig, ax1, axs = ampl.ratio_axes(extra_axes=2)
        self.assertEqual(len(axs), 2)
        self.assertIs(ax1._amplaxesinfo.low_ax, axs[1])
        self.assertIs(axs[0]._amplaxesinfo.main_ax, ax1)
        self.assertIs(axs[1]._amplaxesinfo.main_ax, ax1)
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
