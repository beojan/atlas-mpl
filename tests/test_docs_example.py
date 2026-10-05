"""Test verifying the example from the documentation (docs/examples.rst)."""

import unittest
import io
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats.distributions as dist
import boost_histogram as bh
import atlas_mpl_style as ampl


class TestDocumentationExample(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_documentation_example_end_to_end(self):
        # 1. Setup style
        ampl.use_atlas_style()

        # 2. Setup histograms as in documentation
        rng = np.random.default_rng(42)
        bkg1_dist = dist.expon(0, 3)
        bkg2_dist = dist.expon(1, 3)
        part1_dist = dist.norm(2, 0.2)
        part2_dist = dist.norm(3, 0.4)

        bkg1_data = 100 * bkg1_dist.rvs(20000, rng)
        bkg2_data = 100 * bkg2_dist.rvs(5000, rng)
        part1_data = 100 * part1_dist.rvs(1500, rng)
        part2_data = 100 * part2_dist.rvs(500, rng)

        x_axis = bh.axis.Regular(30, 0, 1000)
        bkg1_h = bh.Histogram(x_axis).fill(bkg1_data)
        bkg2_h = bh.Histogram(x_axis).fill(bkg2_data)
        part1_h = bh.Histogram(x_axis).fill(part1_data)
        part2_h = bh.Histogram(x_axis).fill(part2_data)

        data_h = (
            bh.Histogram(x_axis)
            .fill(100 * bkg1_dist.rvs(20000, rng))
            .fill(100 * bkg2_dist.rvs(5000, rng))
            .fill(100 * part1_dist.rvs(1500, rng))
            .fill(100 * part2_dist.rvs(500, rng))
        )

        # 3. Setup axes
        fig, ax, rax = ampl.ratio_axes()
        ax.set_xlim(0, 1000)
        ax.set_ylim(0, 4000)

        # 4. Plot backgrounds
        bkg = ampl.plot.plot_backgrounds(
            [
                ampl.plot.Background(label="Background 1", hist=bkg1_h),
                ampl.plot.Background(label="Background 2", hist=bkg2_h),
                ampl.plot.Background(label="Particle 1", hist=part1_h),
                ampl.plot.Background(label="Particle 2", hist=part2_h),
            ],
            ax=ax,
        )

        # 5. Plot data, signal, and ratio
        ampl.uhi.plot_data(hist=data_h, label="Data 18", ax=ax)
        ampl.uhi.plot_signal(label="Signal", hist=part1_h, color="paper:red")
        ampl.uhi.plot_ratio(data_h, bkg, ratio_ax=rax, plottype="diff")

        # 6. Set labels
        ampl.set_xlabel("Mass [GeV]", ax=ax)
        ampl.set_ylabel("Count", ax=ax)
        rax.set_ylabel(r"$\frac{{Data} - {Bkg}}{{Bkg}}$")

        # 7. Draw ATLAS label and legend
        ampl.draw_atlas_label(
            0.05,
            0.95,
            ax=ax,
            status="int",
            simulation=False,
            energy="13 TeV",
            lumi=140,
            desc="My example plot",
        )
        ampl.draw_legend(ax=ax)

        # 8. Layout and save to buffer
        fig.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        self.assertGreater(buf.tell(), 0)

        # 9. Verifications
        self.assertEqual(ax.get_xlim(), (0, 1000))
        self.assertEqual(ax.get_ylim(), (0, 4000))
        self.assertEqual(ax.get_ylabel(), "Count")
        self.assertEqual(rax.get_xlabel(), "Mass [GeV]")
        self.assertEqual(rax.get_ylabel(), r"$\frac{{Data} - {Bkg}}{{Bkg}}$")

        # Check legend labels
        leg = ax.get_legend()
        self.assertIsNotNone(leg)
        leg_texts = [t.get_text() for t in leg.get_texts()]
        self.assertIn("Data 18", leg_texts)
        self.assertIn("Signal", leg_texts)
        self.assertIn("Background 1", leg_texts)
        self.assertIn("Background 2", leg_texts)
        self.assertIn("Particle 1", leg_texts)
        self.assertIn("Particle 2", leg_texts)

        # Check ATLAS label content
        self.assertEqual(len(ax.texts), 1)
        atlas_txt = ax.texts[0].get_text()
        self.assertIn("ATLAS", atlas_txt)
        self.assertIn("Internal", atlas_txt)
        self.assertIn("13 TeV", atlas_txt)
        self.assertIn("140", atlas_txt)
        self.assertIn("My example plot", atlas_txt)

        # Check alignment of ylabels (Issue #4)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bb_main = ax.yaxis.label.get_window_extent(renderer)
        bb_ratio = rax.yaxis.label.get_window_extent(renderer)
        self.assertAlmostEqual(bb_main.x1, bb_ratio.x1, places=2)


if __name__ == "__main__":
    unittest.main()
