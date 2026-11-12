"""Tests for atlas_mpl_style.stats module."""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import atlas_mpl_style as ampl
import atlas_mpl_style.stats as stats
from atlas_mpl_style.stats import IncorrectAxesError


def _import_or_skip(name):
    """Import ``name``, or skip the test if it is not installed."""
    try:
        return __import__(name)
    except ImportError:
        raise unittest.SkipTest(f"{name} is not installed")


class TestStatsModule(unittest.TestCase):
    def setUp(self):
        ampl.use_atlas_style()

    def tearDown(self):
        plt.close("all")

    def test_sort_impacts(self):
        df = pd.DataFrame({
            "name": ["paramA", "paramB", "paramC"],
            "impact_postfit_up": [0.1, 0.5, 0.2],
            "impact_postfit_down": [-0.3, -0.2, -0.6],
        })
        with self.assertWarns(DeprecationWarning):
            stats.sort_impacts(df)
        # paramC has max_impact 0.6, paramB has 0.5, paramA has 0.3
        self.assertEqual(list(df["name"]), ["paramC", "paramB", "paramA"])
        self.assertAlmostEqual(df.iloc[0]["max_impact"], 0.6)

    def _impact_columns(self):
        return {
            "name": ["paramA", "paramB", "paramC"],
            "value": [0.1, -0.2, 0.3],
            "err_low": [-0.9, -0.8, -0.7],
            "err_high": [0.9, 0.8, 0.7],
            "impact_postfit_up": [0.1, 0.5, 0.2],
            "impact_postfit_down": [-0.3, -0.2, -0.6],
        }

    def _check_sorted_and_plotted(self, data, names):
        sorted_data = stats.sorted_impacts(data)
        self.assertIs(type(sorted_data), type(data))
        self.assertEqual(names(sorted_data), ["paramC", "paramB", "paramA"])
        self.assertEqual(names(data), ["paramA", "paramB", "paramC"])  # input unchanged
        fig = stats.make_impact_figure(3)
        ax, _ = stats.plot_pulls(sorted_data)
        stats.plot_impacts(sorted_data, ax=ax)
        stats.draw_pull_impact_legend(ax=ax)
        fig.canvas.draw()
        plt.close(fig)

    def test_sorted_impacts_pandas(self):
        self._check_sorted_and_plotted(pd.DataFrame(self._impact_columns()), lambda d: list(d["name"]))

    def test_sorted_impacts_dict(self):
        self._check_sorted_and_plotted(self._impact_columns(), lambda d: list(d["name"]))

    def test_sorted_impacts_polars(self):
        pl = _import_or_skip("polars")
        self._check_sorted_and_plotted(pl.DataFrame(self._impact_columns()), lambda d: d["name"].to_list())

    def test_sorted_impacts_pyarrow(self):
        pa = _import_or_skip("pyarrow")
        self._check_sorted_and_plotted(pa.table(self._impact_columns()), lambda d: d["name"].to_pylist())

    def test_make_impact_figure(self):
        fig = stats.make_impact_figure(5)
        self.assertIsNotNone(fig)
        ax = fig.gca()
        ymin, ymax = ax.get_ylim()
        # ylim is (num_parameters + 0.1, -2 - (num_parameters // 5)) -> inverted y axis
        self.assertAlmostEqual(ymin, 5.1)
        self.assertAlmostEqual(ymax, -3.0)
        plt.close(fig)

    def test_plot_pulls_only(self):
        df = pd.DataFrame({
            "name": ["Syst 1", "Syst 2"],
            "value": [0.2, -0.3],
            "err_low": [0.8, 0.7],
            "err_high": [0.9, 0.6],
        })
        fig = stats.make_impact_figure(2)
        ax, pulls = stats.plot_pulls(df)
        self.assertIsNotNone(pulls)
        self.assertEqual(ax.get_xlim(), (-2, 2))

        # Legend with pulls only
        stats.draw_pull_impact_legend(ax=ax)
        self.assertIsNotNone(ax.get_legend())
        plt.close(fig)

    def test_plot_pulls_and_impacts_with_prefit(self):
        df = pd.DataFrame({
            "name": ["NP 1", "NP 2"],
            "value": [0.1, -0.1],
            "err_low": [0.9, 0.8],
            "err_high": [0.9, 0.8],
            "impact_postfit_up": [0.4, 0.2],
            "impact_postfit_down": [-0.3, -0.1],
            "impact_prefit_up": [0.5, 0.3],
            "impact_prefit_down": [-0.4, -0.2],
        })
        fig = stats.make_impact_figure(2)
        ax, _ = stats.plot_pulls(df)
        impact_ax = stats.plot_impacts(df, draw_prefit=True, ax=ax)
        self.assertIsNotNone(impact_ax)

        # Legend on ax
        stats.draw_pull_impact_legend(ax=ax)
        self.assertIsNotNone(impact_ax.get_legend())
        plt.close(fig)

    def test_plot_impacts_only_without_prefit(self):
        df = pd.DataFrame({
            "name": ["NP 1", "NP 2"],
            "impact_postfit_up": [0.4, 0.2],
            "impact_postfit_down": [-0.3, -0.1],
        })
        fig, ax = plt.subplots()
        impact_ax = stats.plot_impacts(df, draw_prefit=False, up_color="paper:green", down_color="paper:orange", ax=ax)
        self.assertIsNotNone(impact_ax)

        # Passing impact_ax directly to draw_pull_impact_legend
        stats.draw_pull_impact_legend(ax=impact_ax)
        self.assertIsNotNone(impact_ax.get_legend())
        plt.close(fig)

    def test_plot_impacts_with_prefit_no_pulls(self):
        df = pd.DataFrame({
            "name": ["NP 1", "NP 2"],
            "impact_postfit_up": [0.4, 0.2],
            "impact_postfit_down": [-0.3, -0.1],
            "impact_prefit_up": [0.5, 0.3],
            "impact_prefit_down": [-0.4, -0.2],
        })
        fig, ax = plt.subplots()
        impact_ax = stats.plot_impacts(df, draw_prefit=True, ax=ax)
        stats.draw_pull_impact_legend(ax=impact_ax)
        self.assertIsNotNone(impact_ax.get_legend())
        plt.close(fig)

    def test_plot_impacts_without_prefit_with_pulls(self):
        df = pd.DataFrame({
            "name": ["NP 1", "NP 2"],
            "value": [0.1, -0.1],
            "err_low": [0.9, 0.8],
            "err_high": [0.9, 0.8],
            "impact_postfit_up": [0.4, 0.2],
            "impact_postfit_down": [-0.3, -0.1],
        })
        fig, ax = plt.subplots()
        stats.plot_pulls(df, ax=ax)
        impact_ax = stats.plot_impacts(df, draw_prefit=False, ax=ax)
        stats.draw_pull_impact_legend(ax=ax)
        self.assertIsNotNone(impact_ax.get_legend())
        plt.close(fig)

    def test_default_ax_calls(self):
        df = pd.DataFrame({
            "name": ["NP 1"],
            "value": [0.1],
            "err_low": [0.9],
            "err_high": [0.9],
            "impact_postfit_up": [0.4],
            "impact_postfit_down": [-0.3],
        })
        fig = stats.make_impact_figure(1)
        stats.plot_pulls(df)  # ax=None
        stats.plot_impacts(df, draw_prefit=False)  # ax=None
        stats.draw_pull_impact_legend()  # ax=None
        plt.close(fig)

    def test_incorrect_axes_error(self):
        fig, ax = plt.subplots()
        with self.assertRaises(IncorrectAxesError):
            stats.draw_pull_impact_legend(ax=ax)
        plt.close(fig)


    def test_exception_message(self):
        self.assertEqual(str(stats.IncorrectAxesError("no plot")), "no plot")

    def test_legend_kwargs_override_defaults(self):
        df = pd.DataFrame({
            "name": ["NP 1", "NP 2"],
            "value": [0.1, -0.1],
            "err_low": [0.9, 0.8],
            "err_high": [0.9, 0.8],
            "impact_postfit_up": [0.4, 0.2],
            "impact_postfit_down": [-0.3, -0.1],
        })
        fig = stats.make_impact_figure(2)
        ax, _ = stats.plot_pulls(df)
        stats.draw_pull_impact_legend(ax=ax, loc="lower right", title="Pulls only")
        self.assertEqual(ax.get_legend().get_title().get_text(), "Pulls only")
        impact_ax = stats.plot_impacts(df, ax=ax)
        stats.draw_pull_impact_legend(ax=ax, loc="lower right", ncols=1)
        self.assertEqual(impact_ax.get_legend()._loc, 4)
        plt.close(fig)

if __name__ == "__main__":
    unittest.main()
