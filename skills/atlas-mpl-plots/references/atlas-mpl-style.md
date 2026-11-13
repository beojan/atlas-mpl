# atlas_mpl_style 0.28.0 reference

This reference was written from the 0.28.0 source and checked by running the calls it describes with Matplotlib 3.11. Check the installed version with `importlib.metadata.version("atlas-mpl-style")`. If it differs, check the signatures and docstrings there.

Upstream documentation: <https://atlas-mpl.readthedocs.io/en/latest/>

## Contents

- [Style and figure setup](#style-and-figure-setup)
- [Labels, tags, and legends](#labels-tags-and-legends)
- [Histograms from UHI objects: `ampl.uhi`](#histograms-from-uhi-objects-ampluhi)
- [Histograms from arrays: `ampl.plot`](#histograms-from-arrays-amplplot)
- [Where uncertainties come from](#where-uncertainties-come-from)
- [Ratio panels](#ratio-panels)
- [2D histograms](#2d-histograms)
- [Cutflows](#cutflows)
- [Limits](#limits)
- [Pulls and impacts: `ampl.stats`](#pulls-and-impacts-amplstats)
- [Palettes and named colors](#palettes-and-named-colors)
- [Errors the package raises](#errors-the-package-raises)
- [Verification checklist](#verification-checklist)

## Style and figure setup

`ampl.use_atlas_style(atlas_label="ATLAS", fancy_legend=False, usetex=False)` applies the `atlas` stylesheet, resets the color cycle to the ATLAS palette, turns on minor ticks, and removes the legend frame. Call it before creating figures. The settings that most often matter:

| Setting | Value |
| --- | --- |
| Figure size | 11.111 in by 8.333 in at 72 dpi (800 by 600 px) |
| Text size | 18 pt, with 20 pt axis labels and titles |
| Font | TeX Gyre Heros, then Helvetica, Nimbus Sans, FreeSans, Arial |
| Ticks | Inward, on all four sides, with minor ticks |
| Axis limits | Rounded outwards to tick values (`axes.autolimit_mode: round_numbers`). The histogram helpers set the x limits to the bin range, unless the x limits were already set by the caller. |
| Saved background | Transparent. Pass `facecolor="white"` to `savefig` for an opaque image. |

- `atlas_label` replaces the word "ATLAS" in `draw_atlas_label`, for example for another experiment.
- `fancy_legend=True` keeps Matplotlib's framed legend box.
- `usetex=True` typesets text with LaTeX and needs `pdflatex`, `dvipng`, Ghostscript, TeX Gyre Heros, `mathastext`, `physics`, and `siunitx`. If the executables are missing it warns and falls back to `usetex=False`. It does not check the TeX packages.
- With `usetex=False`, math text is upright by default (`mathtext.default: regular`). Use `\mathit{...}` for italic symbols.

The package also registers a `print` stylesheet for `plt.style.use`, for plots outside ATLAS publications: white figure and axes backgrounds (the saved background is still transparent unless `facecolor="white"` is passed to `savefig`), 8 in by 6 in figures at 200 dpi, 16 pt TeX Gyre Heros text, the Paper color cycle, no ticks on the top and right, and `stixsans` math text without LaTeX. Prefer `use_atlas_style()` unless the user asks for it, and do not draw the ATLAS label on a `print` plot. The `paper` and `slides` stylesheets exist only so that old code keeps working. Do not use them. To combine the styles, call `use_atlas_style()` first and `plt.style.use("print")` second. The result keeps the minor ticks, the four-sided ticks, the rounded axis limits, and the frameless legend of the ATLAS style, and takes the font, `stixsans` math text, sizes, figure size, and color cycle from `print`.

`ampl.set_font(family=None, size=None)` changes the font and the base text size of the active style, after `use_atlas_style()` or `plt.style.use("print")`. `family` is a font name or a list of them, placed ahead of the style's fonts. `size` is the base size in points, and every other text size the style sets in points scales with it. With `usetex=True` it warns and changes only the size.

`ampl.ratio_axes(extra_axes=None)` creates a figure with a main panel above a ratio panel that shares its x axis, with no gap between them. It returns `(fig, main_ax, ratio_ax)`. With `extra_axes=n` it creates `n` lower panels and returns them as a list in third place. The figure is square, `6 + 2n` inches on a side (8 in for one ratio panel), whatever `figure.figsize` says. The lower panels use symmetric y ticks with the end ticks removed, so their labels do not collide with the panel above.

## Labels, tags, and legends

- `ampl.set_xlabel(label, ax=None, **kwargs)` right-aligns the x label. Given the main axes from `ratio_axes`, it puts the label on the lowest panel.
- `ampl.set_ylabel(label, ax=None, **kwargs)` aligns the y label with the top of the axis and lines up the y labels of the panels made by `ratio_axes`. For a centered label, as is usual on a ratio panel, call `rax.set_ylabel(...)` directly.
- `ampl.set_zlabel(label, cbar=None, ax=None, **kwargs)` labels a colorbar. Pass the `cbar` you created. For a colorbar made by `plot_2d`, no `cbar` is needed, because `plot_2d` leaves its axes current. Extra keyword arguments set text properties on the label. It raises `ValueError` for axes without such a colorbar.
- `ampl.draw_tag(text, ax=None)` writes a small 8 pt tag just above the top right corner of the axes.

### Legend

`ampl.draw_legend(*, ax=None, **kwargs)` builds the legend from what the package helpers registered on the axes, in this order:

1. Data (`plot_data`).
2. Stack components (`plot_backgrounds`), from the top of the stack down, which matches how they appear.
3. "Stat. Uncertainty" (hatched), when any helper drew a statistical band.
4. "Total Uncertainty" (grey), or "Uncertainty" when there is no statistical entry.
5. Line histograms (`plot_signal`, `plot_1d`).
6. Every other labelled Matplotlib artist on the axes.

Keyword arguments go to `ax.legend`. Every argument is keyword-only and no positional handles or labels are accepted, so to control the entries, set or remove the labels on the artists. For axes that contain limits it builds the limit legend described under [Limits](#limits). On axes without any package helper it lists the labelled artists, like `ax.legend()`.

A band can share the legend entry of a line. `plot_1d` and `plot_signal` do this for their own bands with `attach_bands=True` (while still keeping the separate uncertainty entries in the legend). For a line you drew yourself, call `ampl.plot.plot_band(bins, low, high, label=<the line's label>, ax=ax)`, or draw the band with `fill_between` and call `ampl.plot.register_band(label, artist, ax=ax)`.

`ampl.plot.plot_band(bins, low, high, label=None, ax=None, **kwargs)` draws a stepped band between per-bin `low` and `high` values and returns the artist. Extra arguments go to `fill_between`.

### ATLAS label

```python
ampl.draw_atlas_label(
    0.05, 0.95,          # top left corner of the text, in axes coordinates
    ax=ax,
    status="int",
    simulation=False,
    energy="13.6 TeV",   # string with units
    lumi=140,            # number in fb^-1, or a string with its own units
    lumi_lt=False,
    desc="Signal region",
)
```

The label has up to four lines: "ATLAS" with the status, the line "for education only" (only for `status="opendata"`), the energy and luminosity, and the description. `desc` may contain newlines. Extra keyword arguments go to `ax.text`.

| `status` | Text after "ATLAS" |
| --- | --- |
| `"int"` (default) | Internal |
| `"wip"` | Work In Progress |
| `"prelim"` | Preliminary |
| `"final"` | nothing |
| `"opendata"` | Open Data, plus the "for education only" line |
| `"opendata-res"` | Open Data |
| any other string | that string, unchanged |

- `simulation=True` inserts "Simulation" before the status.
- `status="final"` and `status=None` both give a label with no status text.
- A numeric `lumi` is printed with four significant figures and "fb⁻¹". `lumi_lt=True` puts "<" in front of it, for a plot that uses part of the dataset. `lumi_lt` has no effect on a string `lumi`.
- Use only metadata that the user supplied or that you verified.

## Histograms from UHI objects: `ampl.uhi`

These take histogram objects that follow the UHI `PlottableHistogram` protocol: Hist, boost-histogram, and histograms read with Uproot. All of them are for 1D histograms except `plot_2d`, which takes a 2D histogram. `plot_1d` and `plot_2d` accept both count and profile (mean storage) histograms. Every other helper, along with `Background` and any histogram passed as `stat_errs` or `syst_errs`, requires a count histogram and raises `UnsupportedKindError` for a profile.

- `plot_data(hist, *, stat_errs=None, color="k", label="Data", ax=None)` draws black points with error bars and returns `(values, stat_errs)`. Every argument after `hist` is keyword-only.
- `plot_1d(hist, label, *, stat_errs=None, color=None, attach_bands=False, ax=None, flow=False, **kwargs)` draws an unfilled step histogram, with a hatched statistical band unless `stat_errs=False`. For a count histogram, the extra arguments go to `ax.hist`, and the legend line copies the drawn line's style, width, and transparency. A profile (mean) histogram is drawn as points with the error on the mean (ordered with data points in `draw_legend`), rejects string `stat_errs` with `ValueError`, and takes no `**kwargs`.
- `plot_signal(hist, label, *, stat_errs=None, syst_errs=None, color=None, attach_bands=False, ax=None, **kwargs)` draws an unfilled step histogram that is overlaid on the stack rather than added to it, with a hatched statistical band and, when `syst_errs` is given, a translucent total band. `syst_errs` is an array or a histogram of absolute per-bin uncertainties (or a `(down, up)` pair). Scale the histogram only when requested, and say so in the label. A fitted signal whose normalization is meaningful relative to the backgrounds belongs in the stack as a `Background`.
- `plot_ratio(data, total_bkg, ratio_ax, *, stat_errs=None, max_ratio=None, plottype="diff", offscale_errs=False)`. Every argument after `ratio_ax` is keyword-only. See [Ratio panels](#ratio-panels).
- `plot_2d(hist, ax=None, pad=0.05, **kwargs)`. Accepts a 2D count or profile histogram. See [2D histograms](#2d-histograms).
- `plot_cutflow(hist, ax=None, text=True, textcolor="w", horizontal=True, **kwargs)`. See [Cutflows](#cutflows).

There is no `ampl.uhi.plot_backgrounds`. Build `ampl.plot.Background` objects from the histograms and pass them to `ampl.plot.plot_backgrounds` without `bins`.

`plot_1d(..., flow=True)` adds the underflow and overflow as extra bins at each end, as wide as the first and last bin, and labels them `<low` and `>high` on the x axis. It raises `FlowNotSupportedError` when the histogram has no flow bins. Only `plot_1d` has this option. For the other helpers, fold the overflow into the last bin before plotting if it should be shown.

When no `color` is given, lines and stack components take the next color of the axes' color cycle.

## Histograms from arrays: `ampl.plot`

Use these for pre-binned NumPy arrays. `bins` holds the bin edges, so it is one longer than `hist`. Note that `label` and `bins` come before `hist` here, unlike in `ampl.uhi`.

- `plot_data(bins, hist, stat_errs=None, color="k", label="Data", ax=None)` returns `(hist, stat_errs)`.
- `plot_1d(label, bins, hist, stat_errs=None, color=None, attach_bands=False, ax=None, **kwargs)`.
- `plot_signal(label, bins, hist, stat_errs=None, syst_errs=None, color=None, attach_bands=False, ax=None, **kwargs)`.
- `Background(label, hist, stat_errs=None, syst_errs=None, color=None)` describes one stack component, from an array or a UHI histogram.
- `plot_backgrounds(backgrounds, bins=None, *, show_errs=False, total_err=None, empty_stat_legend=False, ax=None)` draws the stack in list order from the bottom up, with black outlines, and returns `(total_hist, total_err)`. `bins` is required when the backgrounds were built from arrays. The options after `bins` are keyword-only.
  - `show_errs=True` draws a hatched band for the combined statistical uncertainty and a grey band for the total. They are off by default, following the ATLAS publication committee's recommendation.
  - `total_err` replaces the total uncertainty computed from the components, for example with a post-fit uncertainty. It is an array of absolute per-bin uncertainties. Give values at least as large as the statistical uncertainty of the stack, because the grey band is drawn only when the total exceeds the statistical part.
  - `empty_stat_legend=True` adds the "Stat. Uncertainty" legend entry even when no band is drawn.
- `plot_ratio(bins, data, data_errs, bkg, bkg_errs, ratio_ax, max_ratio=None, plottype="diff", offscale_errs=False)`.
- `plot_2d(xbins, ybins, hist, ax=None, pad=0.05, **kwargs)`, `plot_cutflow(labels, hist, ...)`, and `plot_limit(...)` are described in their own sections.

## Where uncertainties come from

The helpers decide what to draw from the histogram's variances, and a wrong assumption here gives wrong or missing error bars without any warning.

| Helper | Variances present | No variances | Override |
| --- | --- | --- | --- |
| `uhi.plot_data` | Error bars of `sqrt(variance)` | Error bars of `sqrt(count)` | `stat_errs="sqrt"` uses `sqrt(count)`. `stat_errs="poisson"` or `"poisson2"` uses a Poisson interval. |
| `uhi.plot_1d` | Hatched band | No band | `stat_errs=False` removes the band. Otherwise `stat_errs` works as for `uhi.plot_data`. |
| `uhi.plot_signal` | Hatched band | No band | `stat_errs` (an array, a histogram, or `"sqrt"`) replaces the variances. |
| `Background(hist=<UHI>)` | `sqrt(variance)` | Zero | `stat_errs="sqrt"` uses `sqrt(count)`. `stat_errs="ignore"` uses zero. An explicit `stat_errs` array replaces the variances. |
| `uhi.plot_ratio`, data | `sqrt(variance)` | `sqrt(count)` | `stat_errs` works as for `uhi.plot_data`. Pass the same value to both so the panels agree. |
| `uhi.plot_ratio`, background histogram | `sqrt(variance)` | Zero | Pass the tuple from `plot_backgrounds` instead |

- boost-histogram and Hist report variances equal to the counts for an unweighted histogram with the default storage, so such histograms get Poisson uncertainties. Fill weighted histograms with `Weight` storage so that the variances are the sum of squared weights.
- The array functions take `stat_errs` as an array of absolute uncertainties, or the string `"sqrt"` for `sqrt(hist)`. `plot_data` and `plot_1d` (and `uhi.plot_ratio`) also take `"poisson"` and `"poisson2"`: the asymmetric 68.27% and 95% central Poisson intervals of ROOT's `TH1::kPoisson` and `kPoisson2`, computed by `ampl.utils.poisson_errors(counts, interval="poisson")`, which needs SciPy. Pass `"poisson"` or `"poisson2"` only when the user explicitly requests Poisson intervals rather than choosing them yourself. They apply only to unweighted counts, so negative or non-integer bin contents raise `ValueError`. `Background` and `plot_signal` do not offer them. An empty bin gets an up error only. With `stat_errs=None`, `plot_data` draws points without error bars and `plot_1d` and `plot_signal` draw no band. `Background` also accepts `"ignore"`.
- `plot_data` draws plain points whenever all the uncertainties are zero.
- Every uncertainty argument (`stat_errs`, `syst_errs`, `total_err`, `data_errs`, `bkg_errs`) also takes a pair `(down, up)` for asymmetric uncertainties, for example up and down systematic variations. Each element is an array, or a histogram in `syst_errs` and in the `stat_errs` of the `uhi` helpers, and signs are ignored. Compute the sizes from varied templates first, as `(nominal - down, up - nominal)`. An array with one row per bin, shape `(N, 2)`, raises `BinningMismatchError`. `plot_data` and `plot_backgrounds` return a `(2, N)` array when the uncertainties are asymmetric, ready for `plot_ratio`. By default, the `uhi` helpers take statistical uncertainties from the variances, which are symmetric.
- `syst_errs` holds absolute per-bin uncertainties, and it is combined in quadrature with the statistical uncertainty, separately for the down and up sides. `plot_backgrounds` adds the systematic uncertainties of different components in quadrature too, so it treats them as uncorrelated. Pass `total_err` when that is not right.

## Ratio panels

`plot_ratio` draws the comparison of data with the total background into the lower panel from `ratio_axes`. In `ampl.uhi.plot_ratio`, `total_bkg` is either a histogram or the `(total_hist, total_err)` tuple returned by `plot_backgrounds`.

| `plottype` | Quantity | Reference line | Default `max_ratio` | Resulting y range |
| --- | --- | --- | --- | --- |
| `"diff"` | `(data - bkg) / bkg` | 0 | 0.25 | -0.275 to 0.275 |
| `"raw"` | `data / bkg` | 1 | 1.25 | 0.725 to 1.275 |
| `"significances"` | signed significance per bin | 0 | 3.5 | -3.85 to 3.85 |

- The y range is symmetric about the reference line. For `"diff"` and `"significances"` it runs from `-max_ratio` to `max_ratio`, and for `"raw"` from `2 - max_ratio` to `max_ratio`. It is then widened by 10% about the reference line so that tick labels do not touch the main panel.
- `"diff"` and `"raw"` draw the data points with error bars of `data_errs / bkg` and a grey band for the relative background uncertainty. `"significances"` draws points without error bars and dashed lines at ±1 and ±2.
- Points outside the range are replaced by red carets at the edge of the panel. `offscale_errs=True` also draws their error bars.
- Significances use the definition of <https://cds.cern.ch/record/2643488>, which is also available as `ampl.utils.significance(data, data_errs, bkg, bkg_errs)`.
- The function does not set a y label. Add one with `rax.set_ylabel(...)`.

For several lower panels, use `fig, ax, raxs = ampl.ratio_axes(extra_axes=2)` and call `plot_ratio` once for each entry of `raxs`.

## 2D histograms

```python
fig, ax = plt.subplots()
mesh, cbar = ampl.uhi.plot_2d(h2, ax=ax, cmap="bird")
ax.set_aspect("auto")
ampl.set_xlabel(r"$\mathit{m}_{1}$ [GeV]", ax=ax)
ampl.set_ylabel(r"$\mathit{m}_{2}$ [GeV]", ax=ax)
ampl.set_zlabel("Events", ax=ax)
```

- `plot_2d` draws with `pcolormesh`, adds a colorbar on the right, and returns `(mesh, cbar)`. Extra arguments go to `pcolormesh`, for example `cmap=`, `norm=matplotlib.colors.LogNorm()`, `vmin=`, and `vmax=`.
- It sets an equal aspect ratio, so one data unit is as long on x as on y. This is right when both axes show the same quantity. Otherwise call `ax.set_aspect("auto")` afterwards, or the plot can become a thin strip.
- The package registers ROOT's `bird` colormap (`cmap="bird"`). The default is Matplotlib's `viridis`.
- The array version takes `hist` with shape `(len(xbins) - 1, len(ybins) - 1)`, x first.
- The mesh is rasterized inside vector output, which keeps SVG and PDF files small.

## Cutflows

```python
fig, ax = plt.subplots()
ampl.plot.plot_cutflow(["All", "Trigger", "2 jets", "b-tag"], counts, ax=ax)
ax.set_xscale("log")
ampl.set_xlabel("Events", ax=ax)
```

- The first label is drawn at the top. Bars are horizontal by default, and `horizontal=False` gives vertical bars. Extra arguments go to `barh` or `bar`.
- Each bar carries its value, written inside the end of the bar in white 16 pt text. On a linear axis the short bars cannot hold the text, which then runs over the category labels. Large counts also make the axis show a `×10ⁿ` multiplier that collides with the right-aligned x label. A log axis avoids both problems. Otherwise pass `text=False` and annotate the bars yourself.
- When `ax` is omitted, the function sets the axis limits to fit the bars, and for horizontal bars it adds space above them for a label and legend. With an explicit `ax`, set the limits yourself.
- `ampl.uhi.plot_cutflow(hist, ...)` needs a histogram with a string category axis and raises `LabeledBinsError` otherwise. The other UHI helpers raise the same error when they get a category axis.

## Limits

```python
fig, ax = plt.subplots()
ampl.plot.plot_limit(
    "Expected", mass, expected,
    minus_one_sigma=lo1, plus_one_sigma=hi1,
    minus_two_sigma=lo2, plus_two_sigma=hi2,
    observed_label="Observed", observed=observed,
    ax=ax,
)
ax.set_yscale("log")
ampl.set_xlabel(r"$\mathit{m}_{X}$ [GeV]", ax=ax)
ampl.set_ylabel("95% CL upper limit on cross-section [fb]", ax=ax)
ampl.draw_legend(ax=ax)
```

- The expected limit is a dashed line and the observed limit is a solid line. The band arguments are the values of the band edges, not offsets from the expected limit.
- Give both edges of a band or neither, and give `observed` together with `observed_label`. Otherwise the function raises `ValueError`.
- Without `color`, the lines are black and the bands are the usual green (±1σ) and yellow (±2σ). With `color`, the bands are translucent versions of that color. Use this to draw several limits on the same axes, one call for each.
- `ampl.draw_legend` recognises the limits. For one limit it lists the observed line, the expected line, and an "Expected ±1σ" and "Expected ±2σ" entry for each band that was drawn. For several limits (each with its own distinct `expected_label`) it lists each limit's observed line, when given, and its expected line with its bands behind it.

## Pulls and impacts: `ampl.stats`

These functions take a table with one row for each nuisance parameter: a pandas or Polars DataFrame, a PyArrow table, or a dict of arrays. They only read columns by name.

| Column | Meaning | Needed by |
| --- | --- | --- |
| `name` | Parameter name | all |
| `value`, `err_low`, `err_high` | Post-fit value and its uncertainties | `plot_pulls` |
| `impact_postfit_up`, `impact_postfit_down` | Impact on the parameter of interest with the nuisance parameter fixed at ±1 post-fit σ | `sorted_impacts`, `plot_impacts` |
| `impact_prefit_up`, `impact_prefit_down` | The same with the pre-fit σ | `plot_impacts(draw_prefit=True)` |

```python
df = ampl.stats.sorted_impacts(df)               # sorted copy, largest impact first
top = df.head(10)
fig = ampl.stats.make_impact_figure(len(top))
ax, _ = ampl.stats.plot_pulls(top)
impact_ax = ampl.stats.plot_impacts(top, draw_prefit=True, ax=ax)
ampl.stats.draw_pull_impact_legend(ax=ax)
fig.tight_layout()
```

- `sorted_impacts(data)` returns a copy of the table, of the same type, sorted by the larger of the two post-fit impacts in absolute value, largest first. It does not change `data` or add columns. `sort_impacts` is the deprecated in-place version: it works only for pandas, issues a `DeprecationWarning`, and adds a `max_impact` column.
- `make_impact_figure(num_parameters)` creates a 10 in by 6 in figure and sets the y limits so that the first row is at the top, with empty space above it for the legend. The size does not grow with the number of parameters, and about 10 parameter names fit at the default text size. For more, make the figure taller with `fig.set_size_inches`, by roughly 0.4 in for each extra parameter.
- `plot_pulls(data, ax=None, **kwargs)` draws the pulls on the bottom x axis, fixed to the range -2 to 2 and labelled θ̂, with guide lines at 0 and ±1. It returns `(ax, errorbar_container)`. Extra arguments go to `errorbar`.
- `plot_impacts(data, draw_prefit=False, up_color="paper:blue", down_color="paper:red", ax=None)` draws the impacts as bars on a second x axis at the top and returns that axis. Post-fit impacts are filled and pre-fit impacts are outlines. Pass the pull axes as `ax`.
- `draw_pull_impact_legend(*, ax=None, **kwargs)` draws the combined legend at the upper left (`ax` is keyword-only). Extra arguments go to `ax.legend` and override its defaults for `loc`, `fontsize`, `ncols`, `frameon`, `facecolor`, `handlelength`, and `handler_map`. It raises `IncorrectAxesError` for axes without pulls or impacts.
- Pulls and impacts can each be drawn alone.

## Palettes and named colors

`ampl.set_color_cycle(pal=None, n=None)` sets the color cycle for axes created afterwards. `n` is the number of series.

| `pal` | Colors |
| --- | --- |
| `None` or `"ATLAS"` | The 7 Okabe-Ito colors, starting with vermilion, for `n <= 7` or no `n`. The 8-color Petroff sequence for `n = 8`. The 10-color Petroff sequence for larger `n`. |
| `"Petroff"` | The 6-, 8-, or 10-color Petroff sequence, chosen by `n`. Without `n`, the 10-color sequence. |
| `"Paper"` | 8 dark colors from the Paper theme |
| `"Oceanic"` | 7 colors from Oceanic Next |
| `"MPL"`, `"Tab"` | Matplotlib's default 10 colors |
| `"HDBS"` | 5 colors |
| `"HH"` | 4 colors |
| `"Series"` | 7 pastel colors |

Any other name raises `ValueError`. Names are not case-sensitive. `use_atlas_style` resets the cycle to `"ATLAS"`. More series than the palette has colors reuse the colors from the start, so pass the real `n` and, for many series, vary the line style or the marker as well.

The package registers these names as Matplotlib colors:

- ATLAS palette: `atlas:vermilion` (or `atlas:red`), `atlas:skyBlue` (or `atlas:lightBlue`), `atlas:orange`, `atlas:yellow`, `atlas:bluishGreen` (or `atlas:green`), `atlas:reddishPurple` (or `atlas:purple`), and `atlas:blue`.
- Petroff 10-color sequence: `petroff:blue`, `petroff:orange`, `petroff:red`, `petroff:gray`, `petroff:purple`, `petroff:brown`, `petroff:orange2`, `petroff:tan`, `petroff:gray2`, `petroff:lightBlue`.
- Paper theme: `paper:bg`, `paper:bgAlt`, `paper:fg`, `paper:red`, `paper:green`, `paper:blue`, `paper:yellow`, `paper:orange`, `paper:pink`, `paper:purple`, `paper:lightBlue`, `paper:olive`.
- Oceanic Next: `on:bg`, `on:bgAlt`, `on:fg`, `on:fgAlt`, `on:red`, `on:orange`, `on:yellow`, `on:green`, `on:cyan`, `on:blue`, `on:pink`, `on:brown`.
- Limit bands: `atlas:onesigma`, `atlas:twosigma`.
- Other palettes: `series:*`, `series2:*`, `hdbs:*`, and `hh:*`.
- `transparent`, a fully transparent color.

Prefer the active color cycle over hard-coding many colors. Use named colors only when the color has a deliberate meaning, such as one process having the same color in every plot.

## Errors the package raises

| Error | Cause |
| --- | --- |
| `ampl.plot.BinningMismatchError` | The lengths of the bin edges, contents, and uncertainties do not agree. |
| `ampl.plot.LabeledBinsError` | A category axis was given where bin edges are needed, or a cutflow got a numeric axis. |
| `ampl.plot.DimensionError` | The histogram has the wrong number of dimensions. |
| `ampl.plot.ViolatesPlottableHistogramError` | The object does not follow the UHI `PlottableHistogram` protocol. |
| `ampl.uhi.UnsupportedKindError` (also `ampl.plot.UnsupportedKindError`) | A profile (or other non-count) histogram was passed where counts are required. |
| `ampl.uhi.FlowNotSupportedError` (also `ampl.plot.FlowNotSupportedError`) | `flow=True` was given for a histogram without flow bins. |
| `ampl.stats.IncorrectAxesError` | `draw_pull_impact_legend` got axes without pulls or impacts. |
| `TypeError` | `bins` missing for non-empty array backgrounds, an invalid `total_bkg` in `uhi.plot_ratio`, `**kwargs` passed with a profile histogram in `uhi.plot_1d`, or positional arguments where keyword-only arguments are required (such as `draw_legend`, `draw_pull_impact_legend`, and optional `uhi` arguments). |
| `ValueError` | An unknown `plottype`, `stat_errs`, or palette name, `stat_errs` as a string on a profile in `uhi.plot_1d`, negative or non-integer counts with `"poisson"` or `"poisson2"`, an empty `backgrounds` list without `bins`, only one edge of a limit band, `observed` without `observed_label`, or `set_zlabel` on axes without a colorbar. |

## Verification checklist

1. Confirm the script ran in the project's own Python environment.
2. Confirm `ampl.use_atlas_style()` ran before the figure was created.
3. Confirm units, axis scaling, category order, and what the error bars and bands mean.
4. Confirm the ATLAS label metadata is accurate, or omit the label.
5. Save and look at a rendered image.
