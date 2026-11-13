"""Tests for atlas_mpl_style.uhi module."""

import unittest
import numpy as np
import matplotlib.pyplot as plt
import boost_histogram as bh
import atlas_mpl_style as ampl
import atlas_mpl_style.uhi as uhi
from atlas_mpl_style.plot import (
    ViolatesPlottableHistogramError,
    DimensionError,
)
from atlas_mpl_style.uhi import LabeledBinsError
from atlas_mpl_style._uhi_validation import (
    UnsupportedKindError,
    ProfileHistogramError,
    FlowNotSupportedError,
)


class TestUHIModule(unittest.TestCase):
    def setUp(self):
        ampl.use_atlas_style()

    def tearDown(self):
        plt.close("all")

    def test_uhi_background(self):
        axis = bh.axis.Regular(10, 0, 100)
        h = bh.Histogram(axis, storage=bh.storage.Weight())
        h.fill(np.array([10, 20, 30]), weight=np.array([1.0, 2.0, 1.5]))

        bkg = ampl.plot.Background(label="BkgUHI", hist=h, color="paper:blue")
        self.assertEqual(bkg.label, "BkgUHI")
        self.assertEqual(bkg.color, "paper:blue")
        self.assertEqual(len(bkg.hist), 10)
        self.assertIsNotNone(bkg.stat_errs)

        # Plot backgrounds without passing bins
        fig, ax = plt.subplots()
        total_hist, total_err = ampl.plot.plot_backgrounds([bkg], ax=ax)
        self.assertEqual(len(total_hist), 10)
        plt.close(fig)

        # Profile histogram rejected for hist
        h_prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([10, 20], sample=[1, 2])
        with self.assertRaises(UnsupportedKindError) as cm:
            ampl.plot.Background(label="BkgProf", hist=h_prof)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Profile histogram rejected for syst_errs
        with self.assertRaises(UnsupportedKindError) as cm:
            ampl.plot.Background(label="BkgProfSyst", hist=h, syst_errs=h_prof)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Syst_errs as valid PlottableHistogram
        syst_h = bh.Histogram(axis).fill([10, 20, 30])
        bkg_with_syst = ampl.plot.Background(label="BkgSyst", hist=h, syst_errs=syst_h)
        self.assertEqual(len(bkg_with_syst.syst_errs), 10)

        # Syst_errs with dimension error
        h2d = bh.Histogram(axis, axis)
        with self.assertRaises(DimensionError):
            ampl.plot.Background(label="BkgSyst2D", hist=h, syst_errs=h2d)

        # Syst_errs with binning mismatch
        axis_other = bh.axis.Regular(5, 0, 50)
        h_mismatch = bh.Histogram(axis_other)
        with self.assertRaises(ampl.plot.BinningMismatchError):
            ampl.plot.Background(label="BkgSystMismatch", hist=h, syst_errs=h_mismatch)

        # Syst_errs violating protocol
        class FakeHistogram:
            axes = [axis]
        with self.assertRaises(ViolatesPlottableHistogramError):
            ampl.plot.Background(label="BkgSystProto", hist=h, syst_errs=FakeHistogram())

        # Labeled bins raise LabeledBinsError
        cat_axis = bh.axis.StrCategory(["A", "B"])
        h_cat = bh.Histogram(cat_axis).fill(["A", "B"])
        with self.assertRaises(LabeledBinsError):
            ampl.plot.Background(label="BkgCat", hist=h_cat)

    def test_uhi_plot_data(self):
        axis = bh.axis.Regular(10, 0, 100)
        h = bh.Histogram(axis).fill([15, 25, 35, 45])

        fig, ax = plt.subplots()
        uhi.plot_data(h, ax=ax, label="DataUHI")
        self.assertIn("DataUHI", ax._ampllegend.data_hists)

        # Deprecated ignore_variances still works, with a warning.
        with self.assertWarns(DeprecationWarning):
            uhi.plot_data(h, ignore_variances=True, ax=ax)

        # Profile histogram rejected
        h_prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([15, 25], sample=[1, 2])
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_data(h_prof, ax=ax)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Dimension error with 2D
        h2d = bh.Histogram(axis, axis)
        with self.assertRaises(DimensionError):
            uhi.plot_data(h2d, ax=ax)

        # Protocol error with non-histogram
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_data([1, 2, 3], ax=ax)

        plt.close(fig)

    def test_uhi_plot_signal(self):
        axis = bh.axis.Regular(10, 0, 100)
        h = bh.Histogram(axis, storage=bh.storage.Weight())
        h.fill([10, 20, 30], weight=[2, 3, 4])

        fig, ax = plt.subplots()
        uhi.plot_signal(h, label="SigUHI", attach_bands=True, ax=ax)
        self.assertIn("SigUHI", ax._ampllegend.line_hists)

        # With ignore_variances and syst_errs as histogram
        syst_h = bh.Histogram(axis).fill([10, 20, 30])
        with self.assertWarns(DeprecationWarning):
            uhi.plot_signal(h, label="SigUHI2", ignore_variances=True, syst_errs=syst_h, ax=ax)

        # Syst_errs with dimension error
        h2d = bh.Histogram(axis, axis)
        with self.assertRaises(DimensionError):
            uhi.plot_signal(h, label="BadSystDim", syst_errs=h2d, ax=ax)

        # Syst_errs with binning mismatch
        axis_other = bh.axis.Regular(5, 0, 50)
        h_mismatch = bh.Histogram(axis_other)
        with self.assertRaises(ampl.plot.BinningMismatchError):
            uhi.plot_signal(h, label="BadSystBins", syst_errs=h_mismatch, ax=ax)

        # Syst_errs violating protocol
        class FakeHistogram:
            axes = [axis]
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_signal(h, label="BadSystProto", syst_errs=FakeHistogram(), ax=ax)

        # Hist violating protocol
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_signal("not_a_hist", label="BadProto", ax=ax)

        # Profile histogram rejected for hist
        h_prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([10, 20], sample=[1, 2])
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_signal(h_prof, label="ProfSig", ax=ax)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Profile histogram rejected for syst_errs
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_signal(h, label="ProfSyst", syst_errs=h_prof, ax=ax)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # PlottableHistogram with variances() is None
        h_no_var = bh.Histogram(axis, storage=bh.storage.Double()).fill([10, 20])
        uhi.plot_signal(h_no_var, label="NoVarSig", ax=ax)

        plt.close(fig)

    def test_uhi_plot_ratio(self):
        axis = bh.axis.Regular(10, 0, 100)
        data_h = bh.Histogram(axis, storage=bh.storage.Weight()).fill([10, 20, 30, 40], weight=[10, 20, 30, 40])
        bkg_h = bh.Histogram(axis, storage=bh.storage.Weight()).fill([10, 20, 30, 40], weight=[8, 18, 32, 38])

        fig, ax, rax = ampl.ratio_axes()
        # plottype="diff" with UHI histogram as total_bkg
        uhi.plot_ratio(data_h, bkg_h, ratio_ax=rax, plottype="diff")

        # plottype="raw" with tuple as total_bkg
        bkg_tuple = (bkg_h.values(), np.sqrt(bkg_h.variances()))
        uhi.plot_ratio(data_h, bkg_tuple, ratio_ax=rax, plottype="raw")

        # plottype="significances"
        uhi.plot_ratio(data_h, bkg_tuple, ratio_ax=rax, plottype="significances")

        # With data having variances() is None
        data_no_var = bh.Histogram(axis, storage=bh.storage.Double()).fill([10, 20])
        uhi.plot_ratio(data_no_var, bkg_tuple, ratio_ax=rax)

        # Profile histogram rejected for data
        h_prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([10, 20], sample=[1, 2])
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_ratio(h_prof, bkg_tuple, ratio_ax=rax)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Profile histogram rejected for total_bkg
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_ratio(data_h, h_prof, ratio_ax=rax)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Invalid total_bkg type
        with self.assertRaises(TypeError):
            uhi.plot_ratio(data_h, "invalid_bkg", ratio_ax=rax)

        # 2D data error
        h2d = bh.Histogram(axis, axis)
        with self.assertRaises(DimensionError):
            uhi.plot_ratio(h2d, bkg_tuple, ratio_ax=rax)

        # Protocol error
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_ratio("not_a_hist", bkg_tuple, ratio_ax=rax)

        plt.close(fig)

    def test_uhi_plot_1d(self):
        axis = bh.axis.Regular(10, 0, 100)
        h = bh.Histogram(axis, storage=bh.storage.Weight()).fill([10, 20, 30], weight=[1, 2, 3])

        fig, ax = plt.subplots()
        uhi.plot_1d(h, label="1DUHI", attach_bands=True, ax=ax)
        self.assertIn("1DUHI", ax._ampllegend.line_hists)

        # Deprecated ignore_variances and stat_err still work, with a warning.
        with self.assertWarns(DeprecationWarning):
            uhi.plot_1d(h, label="1DUHI_no_var", ignore_variances=True, ax=ax)
        with self.assertWarns(DeprecationWarning):
            uhi.plot_1d(h, label="1DUHI_no_band", stat_err=False, ax=ax)
        uhi.plot_1d(h, label="1DUHI_false", stat_errs=False, ax=ax)

        h_double = bh.Histogram(axis, storage=bh.storage.Double()).fill([10, 20])
        uhi.plot_1d(h_double, label="1DUHI_double", ax=ax)

        # Protocol error
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_1d("not_a_hist", label="BadProto", ax=ax)

        # Dimension error
        h2d = bh.Histogram(axis, axis)
        with self.assertRaises(DimensionError):
            uhi.plot_1d(h2d, label="Bad1D", ax=ax)

        plt.close(fig)

    def test_uhi_plot_1d_flow(self):
        axis = bh.axis.Regular(10, 0, 100)
        h = bh.Histogram(axis, storage=bh.storage.Weight())
        h.fill([-10, 15, 25, 120], weight=[2, 1, 1, 3])

        fig, ax = plt.subplots()
        uhi.plot_1d(h, label="FlowHist", flow=True, stat_err=True, attach_bands=True, ax=ax)
        self.assertAlmostEqual(ax.get_xlim()[0], -10.0)
        self.assertAlmostEqual(ax.get_xlim()[1], 110.0)
        labels = [t.get_text() for t in ax.get_xticklabels()]
        self.assertTrue(labels[0].startswith("<"))
        self.assertTrue(labels[-1].startswith(">"))
        self.assertEqual(labels[0], "<0")
        self.assertEqual(labels[-1], ">100")
        plt.close(fig)

        # Flow with ignore_variances
        fig, ax = plt.subplots()
        uhi.plot_1d(h, label="FlowIgnoreVar", flow=True, ignore_variances=True, ax=ax)
        plt.close(fig)

        # Flow with ROOT TH1-like histogram implementing UHI values(flow=True)
        class RootTH1Like:
            kind = "COUNT"
            axes = [axis]

            def values(self, flow=False):
                return np.ones(12) if flow else np.ones(10)

            def variances(self, flow=False):
                return np.ones(12) if flow else np.ones(10)

            def counts(self):
                return np.ones(10)

        fig, ax = plt.subplots()
        uhi.plot_1d(RootTH1Like(), label="RootTH1", flow=True, ax=ax)
        labels = [t.get_text() for t in ax.get_xticklabels()]
        self.assertEqual(labels[0], "<0")
        self.assertEqual(labels[-1], ">100")
        plt.close(fig)

        # Flow not supported raises FlowNotSupportedError (inheriting from TypeError)
        class NoFlowSupport:
            kind = "COUNT"
            axes = [axis]

            def values(self):
                return np.ones(10)

            def variances(self):
                return np.ones(10)

            def counts(self):
                return np.ones(10)

        with self.assertRaises((FlowNotSupportedError, TypeError)):
            uhi.plot_1d(NoFlowSupport(), label="NoFlow", flow=True)

        # Flow=False default doesn't add flow labels
        fig, ax = plt.subplots()
        uhi.plot_1d(h, label="NoFlowDefault", flow=False, ax=ax)
        labels_noflow = [t.get_text() for t in ax.get_xticklabels()]
        self.assertNotIn("Underflow", labels_noflow)
        self.assertNotIn("Overflow", labels_noflow)
        plt.close(fig)

    def test_uhi_plot_2d(self):
        axis_x = bh.axis.Regular(5, 0, 50)
        axis_y = bh.axis.Regular(4, 0, 40)
        h2d = bh.Histogram(axis_x, axis_y).fill([10, 20], [15, 25])

        fig, ax = plt.subplots()
        mesh, cbar = uhi.plot_2d(h2d, ax=ax)
        self.assertIsNotNone(mesh)
        self.assertIsNotNone(cbar)

        # Profile histogram (kind == "MEAN") is accepted
        h2d_prof = bh.Histogram(axis_x, axis_y, storage=bh.storage.Mean()).fill([10, 20], [15, 25], sample=[1, 2])
        mesh_prof, cbar_prof = uhi.plot_2d(h2d_prof, ax=ax)
        self.assertIsNotNone(mesh_prof)
        self.assertIsNotNone(cbar_prof)

        # 1D histogram raises DimensionError
        h1d = bh.Histogram(axis_x)
        with self.assertRaises(DimensionError):
            uhi.plot_2d(h1d, ax=ax)

        plt.close(fig)

    def test_uhi_plot_cutflow(self):
        cat_axis = bh.axis.StrCategory(["Trigger", "Lepton", "Jets", "B-tag"], growth=True)
        h = bh.Histogram(cat_axis).fill(["Trigger", "Trigger", "Lepton", "Jets", "B-tag"])

        # Horizontal
        fig, ax = plt.subplots()
        uhi.plot_cutflow(h, ax=ax, horizontal=True, text=True)
        self.assertEqual(len(ax.patches), 4)
        plt.close(fig)

        # Vertical
        fig, ax = plt.subplots()
        uhi.plot_cutflow(h, ax=ax, horizontal=False, text=True, textcolor="black")
        self.assertEqual(len(ax.patches), 4)
        plt.close(fig)

        # Protocol error
        with self.assertRaises(ViolatesPlottableHistogramError):
            uhi.plot_cutflow("not_a_hist")

        # Profile histogram rejected
        h_prof_cat = bh.Histogram(cat_axis, storage=bh.storage.Mean()).fill(["Trigger", "Lepton"], sample=[1, 2])
        with self.assertRaises(UnsupportedKindError) as cm:
            uhi.plot_cutflow(h_prof_cat)
        self.assertIn("Profile histograms", str(cm.exception))
        self.assertIn("not appropriate", str(cm.exception))

        # Error if axis is regular (unlabeled)
        h_unlabeled = bh.Histogram(bh.axis.Regular(4, 0, 4)).fill([0, 1, 2, 3])
        with self.assertRaises(LabeledBinsError) as cm:
            uhi.plot_cutflow(h_unlabeled)
        self.assertIn("Cutflow requires discrete string-labeled bins", str(cm.exception))

        # Dimension error
        h2d = bh.Histogram(cat_axis, cat_axis)
        with self.assertRaises(DimensionError):
            uhi.plot_cutflow(h2d)

    def test_uhi_bins_labeled_error(self):
        cat_axis = bh.axis.StrCategory(["A", "B"])
        with self.assertRaises(LabeledBinsError):
            uhi._bins(cat_axis)

    def test_profile_histogram_error_alias(self):
        self.assertIs(ProfileHistogramError, UnsupportedKindError)


    def test_unsupported_kind_error_exported(self):
        self.assertIs(ampl.uhi.UnsupportedKindError, UnsupportedKindError)
        self.assertIs(ampl.plot.UnsupportedKindError, UnsupportedKindError)

    def test_uhi_plot_signal_asymmetric_syst(self):
        axis = bh.axis.Regular(4, 0, 4)
        h = bh.Histogram(axis).fill([0.5, 1.5, 1.5, 2.5])
        down = bh.Histogram(axis).fill([0.5, 1.5])
        up = bh.Histogram(axis).fill([0.5, 1.5, 2.5, 2.5])
        fig, ax = plt.subplots()
        uhi.plot_signal(h, "s", syst_errs=(down, up), ax=ax)
        plt.close(fig)

    def test_uhi_poisson_stat_errs(self):
        axis = bh.axis.Regular(3, 0, 3, underflow=True, overflow=True)
        h = bh.Histogram(axis).fill([0.5, 1.5, 1.5, 1.5, -1])
        expected = ampl.utils.poisson_errors(h.values())
        fig, ax = plt.subplots()
        _, errs = uhi.plot_data(h, stat_errs="poisson", ax=ax)
        np.testing.assert_allclose(errs, expected)
        with self.assertWarns(DeprecationWarning):
            _, errs = uhi.plot_data(h, ignore_variances=True, ax=ax)
        np.testing.assert_allclose(errs, np.sqrt(h.values()))
        uhi.plot_1d(h, "h", stat_errs="poisson2", flow=True, ax=ax)
        plt.close(fig)
        fig, ax, rax = ampl.ratio_axes()
        uhi.plot_ratio(h, (h.values() + 1.0, np.ones(3)), rax, plottype="raw", stat_errs="poisson")
        plt.close(fig)


    def test_background_explicit_stat_errs_replace_variances(self):
        axis = bh.axis.Regular(2, 0, 2)
        h = bh.Histogram(axis, storage=bh.storage.Weight()).fill([0.5, 1.5], weight=[2, 3])
        np.testing.assert_allclose(ampl.plot.Background("b", h).stat_errs, [2.0, 3.0])
        down, up = np.array([0.5, 1.0]), np.array([1.5, 2.0])
        bkg = ampl.plot.Background("b", h, stat_errs=(down, up))
        np.testing.assert_allclose(bkg.stat_errs, [down, up])

    def test_uhi_plot_signal_stat_errs(self):
        axis = bh.axis.Regular(2, 0, 2)
        h = bh.Histogram(axis).fill([0.5, 1.5, 1.5, 1.5, 1.5])
        fig, ax = plt.subplots()
        uhi.plot_signal(h, "s", stat_errs=(np.array([1.0, 1.0]), np.array([2.0, 3.0])), ax=ax)
        y = ax.collections[0].get_paths()[0].vertices[:, 1]
        self.assertEqual((y.min(), y.max()), (0.0, 7.0))
        uhi.plot_signal(h, "s2", stat_errs="sqrt", ax=ax)
        with self.assertRaises(ValueError):
            uhi.plot_signal(h, "s3", stat_errs="poisson", ax=ax)
        plt.close(fig)

    def test_uhi_plot_data_without_variances_uses_sqrt(self):
        filled = bh.Histogram(bh.axis.Regular(2, 0, 2)).fill([0.5, 1.5, 1.5, 1.5, 1.5])

        class NoVariances:
            """A PlottableHistogram that reports no variances."""

            axes = filled.axes
            kind = filled.kind

            def values(self):
                return filled.values()

            def variances(self):
                return None

            def counts(self):
                return filled.counts()

        h = NoVariances()
        fig, ax = plt.subplots()
        _, errs = uhi.plot_data(h, ax=ax)
        np.testing.assert_allclose(errs, [1.0, 2.0])
        plt.close(fig)

    def test_uhi_stat_errs_histograms(self):
        axis = bh.axis.Regular(2, 0, 2)
        h = bh.Histogram(axis).fill([-1, 0.5, 1.5, 1.5, 1.5, 1.5, 5])
        down = bh.Histogram(axis).fill([-1, 0.5, 1.5])
        up = bh.Histogram(axis).fill([-1, -1, 0.5, 0.5, 1.5, 5, 5])
        fig, ax = plt.subplots()
        _, errs = uhi.plot_data(h, stat_errs=(down, up), ax=ax)
        np.testing.assert_allclose(errs, [down.values(), up.values()])
        uhi.plot_signal(h, "s", stat_errs=up, ax=ax)
        # With flow bins, the uncertainty histograms supply their flow bins too.
        uhi.plot_1d(h, "f", stat_errs=(down, up), flow=True, ax=ax)
        flow_errs = uhi._with_flow((down, up))
        np.testing.assert_allclose(flow_errs, [down.values(flow=True), up.values(flow=True)])
        self.assertEqual(len(flow_errs[0]), 4)
        h_prof = bh.Histogram(axis, storage=bh.storage.Mean()).fill([0.5], sample=[1])
        with self.assertRaises(UnsupportedKindError):
            uhi.plot_data(h, stat_errs=h_prof, ax=ax)
        plt.close(fig)

    def test_uhi_optional_arguments_are_keyword_only(self):
        h = bh.Histogram(bh.axis.Regular(2, 0, 2)).fill([0.5, 1.5])
        fig, ax = plt.subplots()
        with self.assertRaises(TypeError):
            uhi.plot_data(h, True)
        with self.assertRaises(TypeError):
            uhi.plot_1d(h, "h", False)
        plt.close(fig)

    def test_uhi_plot_ratio_list_and_offscale_errs(self):
        h = bh.Histogram(bh.axis.Regular(2, 0, 2)).fill([0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
        fig, ax, rax = ampl.ratio_axes()
        uhi.plot_ratio(h, [np.array([1.0, 1.0]), np.array([0.1, 0.1])], rax, plottype="raw", offscale_errs=True)
        plt.close(fig)

    def test_uhi_plot_1d_profile(self):
        axis = bh.axis.Regular(3, 0, 3, underflow=True, overflow=True)
        prof = bh.Histogram(axis, storage=bh.storage.Mean())
        prof.fill([0.5, 0.5, 0.5, 1.5, -1, -1], sample=[1.0, 2.0, 3.0, 5.0, 4.0, 6.0])
        fig, ax = plt.subplots()
        uhi.plot_1d(prof, "p", ax=ax)
        points = ax._ampllegend.data_hists["p"]
        means = points.lines[0].get_ydata()
        np.testing.assert_allclose(means[:2], [2.0, 5.0])
        self.assertTrue(np.isnan(means[2]))  # empty bin
        # The error bar of the first bin is the error on the mean, sqrt(1 / 3) for samples 1, 2, 3.
        segments = points.lines[2][0].get_segments()
        low, high = segments[0][:, 1]
        self.assertAlmostEqual(high - low, 2 * np.sqrt(1.0 / 3))
        uhi.plot_1d(prof, "pf", flow=True, ax=ax)
        uhi.plot_1d(prof, "p0", stat_errs=False, ax=ax)
        with self.assertRaises(ValueError):
            uhi.plot_1d(prof, "ps", stat_errs="sqrt", ax=ax)
        with self.assertRaises(TypeError):
            uhi.plot_1d(prof, "pk", ax=ax, ls="--")
        plt.close(fig)

if __name__ == "__main__":
    unittest.main()
