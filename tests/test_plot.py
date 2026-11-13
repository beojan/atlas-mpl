"""Comprehensive tests for atlas_mpl_style.plot module."""

import unittest
import numpy as np
from matplotlib.colors import to_rgba
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
        with self.assertRaises(ValueError):
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
        with self.assertRaises(ValueError):
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
        with self.assertRaises(ValueError):
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

    def test_ratio_limits_are_symmetric(self):
        bins = np.array([0, 1, 2, 3])
        data = np.array([10, 20, 30])
        data_errs = np.array([3, 4, 5])
        bkg = np.array([10, 18, 32])
        bkg_errs = np.array([2, 3, 4])
        expected = {"diff": (-0.275, 0.275), "raw": (0.725, 1.275), "significances": (-3.85, 3.85)}
        for plottype, limits in expected.items():
            fig, rax = plt.subplots()
            plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax=rax, plottype=plottype)
            np.testing.assert_allclose(rax.get_ylim(), limits)
            plt.close(fig)

        # An explicit max_ratio for "raw" is mirrored about 1
        fig, rax = plt.subplots()
        plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax=rax, max_ratio=1.5, plottype="raw")
        np.testing.assert_allclose(rax.get_ylim(), (0.45, 1.55))
        plt.close(fig)

    def test_total_err_override_bands(self):
        bins = np.array([0, 1, 2, 3])
        hist = np.array([100.0, 200.0, 300.0])

        # Total error larger than the stat error leaves a systematic part
        fig, ax = plt.subplots()
        plot_backgrounds([Background("A", hist, stat_errs="sqrt")], bins, show_errs=True, total_err=np.full(3, 30.0), ax=ax)
        self.assertTrue(ax._ampllegend.has_syst)
        plt.close(fig)

        # Total error equal to the stat error leaves none, and must not produce NaN
        fig, ax = plt.subplots()
        with np.errstate(invalid="raise"):
            plot_backgrounds([Background("A", hist, stat_errs="sqrt")], bins, show_errs=True, total_err=np.sqrt(hist), ax=ax)
        self.assertFalse(ax._ampllegend.has_syst)
        plt.close(fig)

    def test_atlas_label_without_status(self):
        fig, ax = plt.subplots()
        draw_atlas_label(0.1, 0.9, ax=ax, status=None, simulation=True)
        self.assertEqual(ax.texts[0].get_text(), r"$\mathbfit{ATLAS}$ Simulation")
        plt.close(fig)

    def test_limit_legend_entries(self):
        x = np.array([100, 200, 300, 400])
        expected = np.array([10.0, 5.0, 2.5, 1.0])

        def legend_entries(ax):
            draw_legend(ax=ax)
            legend = ax.get_legend()
            return [t.get_text() for t in legend.get_texts()], legend.legend_handles

        # Default colors: the swatches match the green and yellow bands
        fig, ax = plt.subplots()
        plot_limit("Expected", x, expected, expected * 0.8, expected * 1.2, expected * 0.6, expected * 1.4, ax=ax)
        labels, handles = legend_entries(ax)
        self.assertEqual(labels, ["Expected", "Expected ±1σ", "Expected ±2σ"])
        self.assertEqual(handles[1].get_facecolor(), to_rgba("atlas:onesigma"))
        self.assertEqual(handles[2].get_facecolor(), to_rgba("atlas:twosigma"))
        plt.close(fig)

        # Bands that were not drawn get no legend entry
        fig, ax = plt.subplots()
        plot_limit("Expected", x, expected, ax=ax)
        self.assertEqual(legend_entries(ax)[0], ["Expected"])
        plt.close(fig)

        fig, ax = plt.subplots()
        plot_limit("Expected", x, expected, expected * 0.8, expected * 1.2, ax=ax)
        self.assertEqual(legend_entries(ax)[0], ["Expected", "Expected ±1σ"])
        plt.close(fig)

        # Several limits, one of them without bands
        fig, ax = plt.subplots()
        plot_limit("Exp A", x, expected, expected * 0.8, expected * 1.2, color="atlas:blue", ax=ax)
        plot_limit("Exp B", x, expected * 2, color="atlas:red", ax=ax)
        self.assertEqual(legend_entries(ax)[0], ["Exp A", "Exp B"])
        plt.close(fig)

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
        bkg_sqrt = Background("BkgSqrt", hist, stat_errs="sqrt")
        np.testing.assert_array_equal(bkg_sqrt.stat_errs, np.sqrt(hist))

        with self.assertRaises(ValueError):
            Background("BkgPois", hist, stat_errs="poisson")

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


    def test_exception_message(self):
        self.assertEqual(str(BinningMismatchError("bad bins")), "bad bins")

    def test_set_zlabel_after_plot_2d(self):
        fig, ax = plt.subplots()
        plot_2d(np.arange(4.0), np.arange(3.0), np.ones((3, 2)), ax=ax)
        self.assertIs(plt.gca(), ax)
        set_zlabel("Events")
        self.assertEqual(ax._amplaxesinfo.cbar.get_ylabel(), "Events")
        plt.close(fig)

    def test_plot_1d_histogram_kwargs(self):
        fig, ax = plt.subplots()
        plot_1d("h", np.arange(4.0), np.ones(3), ax=ax, density=True, lw=3, ls="--")
        line = ax._ampllegend.line_hists["h"]
        self.assertEqual(line.get_linewidth(), 3)
        self.assertEqual(line.get_linestyle(), "--")
        draw_legend(ax=ax)
        plt.close(fig)

    def test_draw_legend_rejects_positional_args(self):
        fig, ax = plt.subplots()
        with self.assertRaises(TypeError):
            draw_legend(["a"], ax=ax)
        plt.close(fig)

    def test_x_limits_fit_the_bins(self):
        fig, ax, rax = ampl.ratio_axes()
        bins = np.linspace(0, 1000, 31)
        plot_backgrounds([Background("b", np.ones(30))], bins, ax=ax)
        plot_signal("s", np.linspace(-100, 900, 31), np.ones(30), ax=ax)
        plot_ratio(bins, np.ones(30), np.ones(30), np.ones(30), np.ones(30), rax)
        fig.canvas.draw()
        self.assertEqual(ax.get_xlim(), (-100.0, 1000.0))
        self.assertEqual(rax.get_xlim(), (-100.0, 1000.0))
        plt.close(fig)

    def test_x_limits_set_by_caller_are_kept(self):
        fig, ax = plt.subplots()
        bins = np.linspace(0, 1000, 31)
        plot_data(bins, np.ones(30), ax=ax)
        ax.set_xlim(200, 600)
        plot_1d("h", bins, np.ones(30), ax=ax)
        self.assertEqual(ax.get_xlim(), (200.0, 600.0))
        plt.close(fig)

    def test_raw_ratio_ticks_centred_on_one(self):
        fig, ax, rax = ampl.ratio_axes()
        bins = np.linspace(0, 1, 5)
        plot_ratio(bins, np.ones(4), np.ones(4), np.ones(4), np.ones(4), rax, plottype="raw")
        fig.canvas.draw()
        lo, hi = rax.get_ylim()
        ticks = [t for t in rax.get_yticks() if lo <= t <= hi]
        self.assertIn(1.0, ticks)
        self.assertGreaterEqual(len(ticks), 3)
        plt.close(fig)

    def test_plot_1d_density_band_matches_line(self):
        fig, ax = plt.subplots()
        bins = np.array([0.0, 2, 4, 8, 10])
        hist = np.array([4.0, 8, 16, 4])
        plot_1d("h", bins, hist, stat_errs="sqrt", ax=ax, density=True)
        density = hist / (hist.sum() * np.diff(bins))
        band = ax.collections[0].get_paths()[0].vertices[:, 1]
        self.assertAlmostEqual(band.max(), (density + np.sqrt(hist) / (hist.sum() * np.diff(bins))).max())
        self.assertAlmostEqual(ax.patches[0].get_xy()[:, 1].max(), density.max())
        plt.close(fig)

    # Asymmetric uncertainties: a pair (down, up), with signs ignored.
    def _band_edges(self, collection):
        y = collection.get_paths()[0].vertices[:, 1]
        return y.min(), y.max()

    def test_asymmetric_errors_accepted_everywhere(self):
        bins = np.linspace(0, 4, 5)
        n = np.array([1.0, 4, 9, 16])
        down, up = 0.5 * np.sqrt(n), 1.5 * np.sqrt(n)
        for errs in [(down, up), np.vstack([down, up]), (-down, up)]:
            fig, ax = plt.subplots()
            _, returned = plot_data(bins, n, errs, ax=ax)
            np.testing.assert_allclose(returned, [down, up])
            plot_1d("h", bins, n, errs, ax=ax)
            plot_signal("s", bins, n, errs, errs, ax=ax)
            total_hist, total_err = plot_backgrounds(
                [Background("b", n, errs, errs)], bins, total_err=None, ax=ax, show_errs=True
            )
            self.assertEqual(total_err.shape, (2, 4))
            plt.close(fig)

    def test_asymmetric_band_edges(self):
        bins = np.linspace(0, 1, 2)
        fig, ax = plt.subplots()
        plot_1d("h", bins, np.array([10.0]), (np.array([1.0]), np.array([3.0])), ax=ax)
        self.assertEqual(self._band_edges(ax.collections[0]), (9.0, 13.0))
        plt.close(fig)

    def test_backgrounds_combine_each_side_in_quadrature(self):
        bins = np.linspace(0, 1, 2)
        fig, ax = plt.subplots()
        _, total_err = plot_backgrounds(
            [
                Background("a", np.array([5.0]), (np.array([3.0]), np.array([0.0]))),
                Background("b", np.array([5.0]), (np.array([4.0]), np.array([1.0]))),
            ],
            bins,
            ax=ax,
        )
        np.testing.assert_allclose(total_err, [[5.0], [1.0]])
        plt.close(fig)

    def test_symmetric_errors_stay_one_dimensional(self):
        bins = np.linspace(0, 2, 3)
        fig, ax = plt.subplots()
        _, total_err = plot_backgrounds([Background("b", np.ones(2), np.ones(2))], bins, ax=ax)
        self.assertEqual(total_err.shape, (2,))
        _, stat = plot_data(bins, np.ones(2), np.ones(2), ax=ax)
        self.assertEqual(stat.shape, (2,))
        plt.close(fig)

    def test_one_row_per_bin_is_rejected(self):
        bins = np.linspace(0, 3, 4)
        fig, ax = plt.subplots()
        with self.assertRaisesRegex(BinningMismatchError, r"\(down, up\)"):
            plot_data(bins, np.ones(3), np.ones((3, 2)), ax=ax)
        plt.close(fig)

    def test_ratio_with_asymmetric_errors(self):
        bins = np.linspace(0, 2, 3)
        data, bkg = np.array([12.0, 8.0]), np.array([10.0, 10.0])
        data_errs = (np.array([1.0, 2.0]), np.array([3.0, 4.0]))
        bkg_errs = (np.array([0.5, 1.5]), np.array([2.5, 3.5]))
        fig, ax, rax = ampl.ratio_axes()
        plot_ratio(bins, data, data_errs, bkg, bkg_errs, rax, plottype="raw")
        lo, hi = self._band_edges(rax.collections[0])
        self.assertAlmostEqual(lo, 1 - 1.5 / 10)
        self.assertAlmostEqual(hi, 1 + 3.5 / 10)
        plt.close(fig)
        fig, ax, rax = ampl.ratio_axes()
        plot_ratio(bins, data, data_errs, bkg, bkg_errs, rax, plottype="significances")
        points = [line for line in rax.lines if line.get_marker() == "o"][0].get_ydata()
        # Data above the background use the data's down and the background's up uncertainty.
        expected = ampl.utils.significance(data, np.array([1.0, 4.0]), bkg, np.array([2.5, 1.5]))
        np.testing.assert_allclose(points, expected)
        plt.close(fig)

    def test_poisson_errors(self):
        errs = ampl.utils.poisson_errors([0, 4])
        # Empty bin: no down error, up error to the 68.27% upper limit, -ln(1 - 0.8413).
        np.testing.assert_allclose(errs[:, 0], [0.0, 1.8410], atol=1e-3)
        np.testing.assert_allclose(errs[:, 1], [1.9137, 3.1627], atol=1e-3)
        errs95 = ampl.utils.poisson_errors([0], "poisson2")
        np.testing.assert_allclose(errs95[:, 0], [0.0, -np.log(0.025)], atol=1e-6)
        with self.assertRaises(ValueError):
            ampl.utils.poisson_errors([-1])
        with self.assertRaises(ValueError):
            ampl.utils.poisson_errors([1], "poisson3")
        with self.assertRaisesRegex(ValueError, "weighted"):
            ampl.utils.poisson_errors([1.5])

    def test_poisson_stat_errs_names(self):
        bins = np.linspace(0, 2, 3)
        n = np.array([0.0, 4.0])
        fig, ax = plt.subplots()
        _, errs = plot_data(bins, n, "poisson", ax=ax)
        np.testing.assert_allclose(errs, ampl.utils.poisson_errors(n))
        _, errs = plot_data(bins, n, "poisson2", ax=ax)
        np.testing.assert_allclose(errs, ampl.utils.poisson_errors(n, "poisson2"))
        plot_1d("h", bins, n, "poisson", ax=ax)
        with self.assertRaises(ValueError):
            plot_signal("s", bins, n, "poisson2", ax=ax)
        with self.assertRaises(ValueError):
            plot_data(bins, n, "pois", ax=ax)
        with self.assertRaisesRegex(ValueError, 'stat_errs="poisson"'):
            plot_data(bins, np.array([0.5, 4.0]), "poisson", ax=ax)
        plt.close(fig)


    def test_plot_signal_rejects_profile_syst_errs(self):
        import boost_histogram as bh
        from atlas_mpl_style.plot import UnsupportedKindError

        axis = bh.axis.Regular(2, 0, 2)
        prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([0.5], sample=[1])
        fig, ax = plt.subplots()
        with self.assertRaises(UnsupportedKindError):
            plot_signal("s", np.array([0.0, 1, 2]), np.array([4.0, 9]), syst_errs=prof, ax=ax)
        plt.close(fig)

    def test_lists_are_accepted(self):
        bins, hist = [0.0, 1, 2], [1.0, 4]
        fig, ax, rax = ampl.ratio_axes()
        plot_backgrounds([Background("b", hist, "sqrt")], bins, ax=ax, show_errs=True)
        plot_data(bins, hist, "sqrt", ax=ax)
        plot_1d("h", bins, hist, [1.0, 2], ax=ax)
        plot_signal("s", bins, hist, [1.0, 2], ax=ax)
        plot_ratio(bins, hist, [1.0, 2], hist, [1.0, 1], rax)
        plt.close(fig)
        fig, ax = plt.subplots()
        plot_2d(bins, bins, [[1.0, 2], [3, 4]], ax=ax)
        plt.close(fig)

    def test_empty_backgrounds_give_zero_totals(self):
        fig, ax = plt.subplots()
        total_hist, total_err = plot_backgrounds([], np.linspace(0, 3, 4), ax=ax)
        np.testing.assert_array_equal(total_hist, np.zeros(3))
        np.testing.assert_array_equal(total_err, np.zeros(3))
        with self.assertRaises(ValueError):
            plot_backgrounds([], ax=ax)
        plt.close(fig)

    def test_plot_signal_kwargs(self):
        fig, ax = plt.subplots()
        plot_signal("s", np.linspace(0, 2, 3), np.ones(2), ax=ax, ls="--", lw=3)
        line = ax._ampllegend.line_hists["s"]
        self.assertEqual((line.get_linestyle(), line.get_linewidth()), ("--", 3))
        plt.close(fig)

    def test_fixed_text_sizes_follow_font_size(self):
        ampl.set_font(size=9)
        fig, ax = plt.subplots()
        draw_tag("tag", ax=ax)
        self.assertAlmostEqual(ax.texts[-1].get_fontsize(), 4.0)
        plt.close(fig)

if __name__ == "__main__":
    unittest.main()
