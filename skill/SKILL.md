---
name: atlas-mpl-plots
description: >-
  Create and revise Python data visualizations with atlas_mpl_style. Use whenever
  producing or modifying plots, charts, histograms, ECDFs, ratio plots, cutflows,
  limits, 2D histograms, pull or impact plots, box, violin, or distribution plots,
  or ATLAS-branded figures, including general data-analysis plots that should
  inherit the ATLAS Matplotlib style.
---

# ATLAS Matplotlib plots

Use `atlas_mpl_style` for every plot. Keep ordinary Matplotlib available for plot types the package does not wrap. Activating the style is still required for those.

## Workflow

1. Run Python in the environment the project already uses, with whatever tool the project uses to run it. Confirm the package is there with `python -c "import atlas_mpl_style"`. If it is missing, ask before adding it. It is published on PyPI as `atlas-mpl-style` and needs Matplotlib 3.11 or later. Do not create a separate environment or install packages globally unless the user asks.

2. Activate the style before creating any figure or axes:

   ```python
   import matplotlib.pyplot as plt
   import atlas_mpl_style as ampl

   ampl.use_atlas_style()
   ```

   The style and the color cycle are read when axes are created, so axes that already exist keep their old settings. `usetex=False` is the default and needs no TeX installation. Pass `usetex=True` only when the user explicitly needs full LaTeX.

   Without LaTeX, text in `$...$` is set upright, like the surrounding text. Write `$\mathit{m}_{jj}$` or `$\mathit{p}_{T}$` when a symbol should be italic. Only Matplotlib mathtext is available, so macros from `siunitx` or `physics` do not work.

3. Choose the API:

   - Prefer `atlas_mpl_style` wherever it provides the functionality. The table below lists what it covers. Use it for these even when the figure also contains seaborn or Matplotlib parts.
   - Use seaborn, when it is installed, for statistical plots the package does not cover (see "Seaborn for statistical plots"), and plain `matplotlib.axes.Axes` methods for scatter, line, bar, and other remaining plots. The active ATLAS style and color cycle apply to all of them.

   | Plot | Function |
   | --- | --- |
   | Data points with error bars | `ampl.uhi.plot_data`, `ampl.plot.plot_data` |
   | Stacked filled histograms | `ampl.plot.plot_backgrounds` with `ampl.plot.Background` |
   | Unfilled overlaid histogram | `ampl.uhi.plot_1d`, `ampl.plot.plot_1d` |
   | Overlaid signal with uncertainty bands | `ampl.uhi.plot_signal`, `ampl.plot.plot_signal` |
   | Ratio, relative difference, or significance panel | `ampl.ratio_axes` with `ampl.uhi.plot_ratio` or `ampl.plot.plot_ratio` |
   | 2D histogram with colorbar | `ampl.uhi.plot_2d`, `ampl.plot.plot_2d` |
   | Cutflow | `ampl.uhi.plot_cutflow`, `ampl.plot.plot_cutflow` |
   | Expected and observed limits with bands | `ampl.plot.plot_limit` |
   | Stepped uncertainty band | `ampl.plot.plot_band` |
   | Nuisance parameter pulls and impacts | `ampl.stats` |

   The `ampl.uhi` functions take histogram objects from Hist, boost-histogram, or Uproot. The `ampl.plot` functions take NumPy arrays of bin edges and contents. `plot_backgrounds` and `plot_limit` exist only in `ampl.plot`, and `Background` accepts either kind of input.

4. Match the color cycle to the number of series when helpful, before creating the axes:

   ```python
   ampl.set_color_cycle("ATLAS", n=4)
   ```

   Prefer the package's accessible ATLAS palette (Okabe-Ito colors, switching to Petroff for more than 7 series). Avoid replacing the package style with hand-built `rcParams` or unrelated themes. Use the package's named colors, such as `"atlas:blue"`, when a fixed semantic color is needed.

5. Use ATLAS-aligned labels and package-aware legends:

   ```python
   ampl.set_xlabel("Request time [ms]", ax=ax)
   ampl.set_ylabel("Events", ax=ax)
   ampl.draw_legend(ax=ax)
   ```

   `ampl.draw_legend` orders the entries of plots made with the package helpers (data first, uncertainties after the stack) and also lists ordinary Matplotlib artists that have labels. It forwards keyword arguments such as `loc=` and `ncols=` to `ax.legend`, but it ignores positional handles and labels. Do not use it on seaborn distribution plots (see below).

   Use `ampl.draw_atlas_label(...)` only when ATLAS branding or approval status is appropriate. Never invent status, luminosity, energy, simulation state, or descriptive text.

6. Make the result legible and truthful: include units, state logarithmic axes, separate startup or warm-up populations when they distort steady-state behavior, show uncertainty or sample counts where useful, and avoid misleading truncated axes.

7. Save the figure in the format its destination needs, and apply layout before saving:

   - PDF is the default for everything that is not a web page: papers, notes, LaTeX or ConTeXt documents, slides, and print.
   - SVG is for web pages.
   - PNG is for destinations that only take raster images, at 200 dpi or more. Also save a PNG next to every PDF or SVG for inspection, from the same figure and with the same `savefig` options, so that it shows the same layout.

   Follow an explicit format request from the user. The ATLAS style saves figures with a transparent background in every format, so pass `facecolor="white"` to `savefig` when the figure needs an opaque background, for example on a dark slide or page.

8. Look at every figure you produce before reporting the plot as done. View the inspection PNG as an image, with whatever file or image viewing tool you have. Reading the plotting code is not a substitute. The deliverable can differ from the inspection PNG when the two were saved with different options (`bbox_inches`, figure size, `facecolor`) or when fonts are embedded differently, so open the PDF itself at least once after the layout has settled. Look for:

   - overlapping or clipped text (titles, tick labels, axis labels, annotations, ATLAS label, legend)
   - a legend covering data or running outside the axes
   - misaligned panels, such as a ratio panel whose x range or axis labels differ from the main panel
   - an x axis that extends past the histogram range, leaving empty bins at the sides
   - crowded, rotated, or unreadable category labels
   - colors that are hard to tell apart, or marks hidden behind other marks
   - axis ranges, log scales, or units that do not match the data

   Fix each problem, save every format again, and look again. Repeat until the figure is clean. Say in the summary if a problem remains.

   Also judge the figure at the size it will be shown. A figure placed in a document column or on a slide is scaled down, and its text shrinks with it. Text that is clear in a full-size PNG can be too small there, so set the figure size for the destination with `figsize=` or `fig.set_size_inches(...)` and do not rely on scaling.

   Make room instead of accepting overlap. Position the ATLAS label with the `x` and `y` arguments of `ampl.draw_atlas_label` and place the legend with `loc=`, `bbox_to_anchor=`, and `ncols=`. If the label and legend still cover data, add unused space: raise the upper y limit (on a log axis, by a factor of several), widen the x range, enlarge the figure, or shrink the axes with `fig.subplots_adjust` so the legend can sit outside them. Empty space is better than hidden data.

## Histogram pattern

For data, stacked components, an overlaid signal, and a ratio panel:

```python
fig, ax, rax = ampl.ratio_axes()

total = ampl.plot.plot_backgrounds(
    [
        ampl.plot.Background(label="Background A", hist=bkg_a),  # bottom of the stack
        ampl.plot.Background(label="Background B", hist=bkg_b),
    ],
    show_errs=True,
    ax=ax,
)
ampl.uhi.plot_signal(signal, "Signal", color="atlas:blue", ax=ax)
ampl.uhi.plot_data(data, label="Data", ax=ax)
ampl.uhi.plot_ratio(data, total, ratio_ax=rax, plottype="diff")

edges = data.axes[0].edges
ax.set_xlim(edges[0], edges[-1])
ax.set_ylim(0, 1.5 * ax.get_ylim()[1])  # headroom for the label and legend

ampl.set_xlabel(r"$\mathit{m}$ [GeV]", ax=ax)  # goes below the ratio panel
ampl.set_ylabel("Events / 20 GeV", ax=ax)
rax.set_ylabel("(Data - Bkg) / Bkg")  # centered, so set it directly
ampl.draw_atlas_label(0.05, 0.95, ax=ax, status="int", energy="13.6 TeV", lumi=140)
ampl.draw_legend(ax=ax, loc="upper right")
fig.tight_layout()
fig.savefig("plot.pdf")
fig.savefig("plot.png", dpi=180)  # for inspection
```

The details that are easy to get wrong:

- `plot_backgrounds` stacks the list from bottom to top and returns `(total_hist, total_err)`, which `ampl.uhi.plot_ratio` accepts as the denominator. It draws the uncertainty bands only with `show_errs=True`. The returned `total_err` includes the uncertainties either way, so the ratio panel shows its grey band regardless.
- Set the x limits explicitly. The uncertainty bands add margins, and the style then rounds the limits outwards, so a histogram from 0 to 500 can end up on an axis from -100 to 600.
- The ratio panel has no y label until you set one. `plot_ratio` draws `"diff"` as `(data - bkg) / bkg` around 0, `"raw"` as `data / bkg` around 1, and `"significances"` as per-bin significance.
- The ratio axis is symmetric about its reference line. Pass `max_ratio` to change the range. With `plottype="raw"`, `max_ratio=1.5` gives an axis from 0.5 to 1.5 before a 10% margin is added.
- Uncertainties come from the histogram's variances. Read "Where uncertainties come from" in the reference when histograms are weighted, have no variances, or the error bars look wrong.
- `ratio_axes()` always creates an 8 in square figure. Call `fig.set_size_inches(...)` afterwards for another size.

## Figures placed in documents and web pages

A figure that is scaled to fit a text column or a slide has its text scaled with it. The ATLAS style's 800 by 600 px figure with 18 pt text suits a figure shown on its own. When the figure sits beside body text, size it for its place:

- Set the figure size to the size at which it will be shown, in inches, with `figsize=` or `fig.set_size_inches(...)`. Then call `ampl.set_font(size=...)` after `ampl.use_atlas_style()`, so that the text matches the surrounding text. It sets the base size and scales the axis labels, titles, tick labels, and legend with it. Do not pass `fontsize=` to individual elements, so all the text stays consistent.
- If text collides at that size, make the figure taller or simplify it. Do not shrink the text below the size of the surrounding text.
- `ampl.ratio_axes()` and `ampl.stats.make_impact_figure()` set their own figure sizes, 8 in square and 10 in by 6 in, and ignore `figure.figsize`. Resize those figures with `fig.set_size_inches(...)`.
- The bar labels of `plot_cutflow`, `draw_tag`, and `ampl.stats.draw_pull_impact_legend` use their own sizes, scaled with `font.size` (16 pt, 8 pt, and 14 pt in the ATLAS style). Pass `fontsize=` to `draw_pull_impact_legend` to change its size.
- For a set of figures in one document, save them all at the same width and avoid `bbox_inches="tight"`, which crops each figure to a different size and so gives each a different scale on the page.

## Seaborn for statistical plots

Seaborn supplements `atlas_mpl_style`. It does not replace it: keep using the package's histogram helpers for HEP histograms, and its labels, legends, and ATLAS label on seaborn figures where they apply. Use seaborn for the statistical plots the package does not provide, so exploit its full range rather than falling back to bare Matplotlib. Draw seaborn plots onto axes created after `ampl.use_atlas_style`, and do not call `sns.set_theme`, `sns.set_style`, or `sns.set_context`, because they overwrite the ATLAS style. Pass `ax=ax`. Seaborn's default palette follows the active ATLAS color cycle, so omit `palette=` unless a fixed mapping is needed.

Seaborn is not a dependency of `atlas_mpl_style`, so the environment may not have it. Check with `import seaborn` before planning a plot around it. If it is missing, do not install it unless the user asks. Draw the plot with Matplotlib under the ATLAS style instead, and say in the summary that seaborn was not available:

| Seaborn | Matplotlib replacement |
| --- | --- |
| `sns.boxplot` | `ax.boxplot` |
| `sns.violinplot` | `ax.violinplot` with `showmedians=True` or `quantiles=` |
| `sns.ecdfplot` | `ax.ecdf` |
| `sns.histplot` | `ax.hist` with `histtype="step"`, or the package's `plot_1d` on binned counts |
| `sns.kdeplot` | `scipy.stats.gaussian_kde` evaluated on a grid and drawn with `ax.plot`, or a histogram if SciPy is missing too |
| `sns.stripplot` | `ax.scatter` with a small random offset on the category axis |
| `sns.heatmap` | `ax.pcolormesh` or `ax.imshow` with `fig.colorbar`, and `ax.text` for cell values |
| `sns.pointplot`, `sns.barplot` | `ax.errorbar` or `ax.bar` with `yerr=`, with the interval computed explicitly |

The guidance below on which plot to choose applies to the Matplotlib replacements as well. With Matplotlib, group the data and label the series yourself, and `ax.legend()` or `ampl.draw_legend(ax=ax)` then works normally.

Checked with seaborn 0.14 and atlas_mpl_style 0.28.0:

- `ampl.set_xlabel` and `ampl.set_ylabel` work on seaborn axes. Seaborn labels axes with the column name, so always set labelled units this way.
- `ampl.draw_atlas_label` works, but it can overlap the legend or data. Choose its `x` and `y` deliberately, and add headroom to the axes if needed, as described in step 8.
- `ampl.draw_legend` and `ax.legend()` both replace the legend of a seaborn distribution plot (`ecdfplot`, `kdeplot`, `histplot`) with an empty one, because seaborn gives those artists private labels. Keep seaborn's own legend there and use `sns.move_legend(ax, ...)` to reposition it. The legends of `scatterplot`, `lineplot`, and `boxplot` survive `ampl.draw_legend`.

Pick the plot that shows the distribution, not just a summary:

- Comparing a quantity across categories, ranks, configurations, or runs: `sns.boxplot` for quartiles and outliers, `sns.violinplot` for shape, with its own `inner=` marks supplying the summary so it is not combined with a separate box plot (use `cut=0` for bounded quantities such as times, `inner="quart"` or `inner="box"`, and `density_norm="width"` when sample counts differ), `sns.boxenplot` for large samples with heavy tails. Overlay `sns.stripplot` or `sns.swarmplot` for small samples, and put sample counts in the category labels.
- Non-HEP one-dimensional distributions such as timings, latencies, memory, or throughput: `sns.histplot` (with `kde=True` or `element="step"`), `sns.kdeplot` (with `common_norm=False` when comparing groups), and `sns.ecdfplot`. Use `log_scale=True` for heavy-tailed data and state it on the axis. Use `multiple="layer"` or `"dodge"` for grouped comparison, not `"stack"` unless the parts sum to a meaningful total.
- Relationships: `sns.scatterplot`, `sns.regplot` or `sns.lmplot` for trends, `sns.jointplot` and `sns.pairplot` for exploration, `sns.heatmap` for matrices (annotate cells and center diverging maps).
- Estimates with uncertainty: `sns.pointplot`, `sns.barplot` with confidence intervals, and `sns.lineplot` with the `errorbar=` option. State what the interval means.

Use long-form data frames with `hue=`, `x=`, `y=`, and `order=` so categories have a stable, meaningful order. Use `sns.FacetGrid` or the figure-level functions (`displot`, `catplot`, `relplot`) for many groups, then check the ATLAS style still applied to them.

## Reference routing

Read [references/atlas-mpl-style.md](./references/atlas-mpl-style.md) before using anything beyond the histogram pattern above: uncertainty handling, overflow bins, ratio modes, the ATLAS label options, limits, cutflows, 2D plots, palettes and named colors, the `print` style and `set_font`, or pull and impact plots. It records the 0.28.0 API with worked examples.
