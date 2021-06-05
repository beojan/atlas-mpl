import matplotlib as _mpl
import matplotlib.colors as _colors
import numpy as _np
import atlas_mpl_style._utils as _u
from atlas_mpl_style.utils import significance as _significance
from math import floor, ceil
from mpl_toolkits.axes_grid1 import make_axes_locatable as _make_axes_locatable

_atlas_label = "ATLAS"
_usetex = False

# For histograms with no color set
_hist_colors = _mpl.rcParams["axes.prop_cycle"]()


def _bins(axis):
    a = list(axis)
    if isinstance(a[0], str):
        raise LabeledBinsError("Bins are labeled. Perhaps you may want plot_cutflow.")
    return _np.array([i for (i, _) in a] + [a[-1][1]])


def _formatSciNotation(x):
    s = f"{x:.5g}"
    # From ScalarFormatter
    decimal_point = "."
    positive_sign = "+"
    tup = s.split("e")
    try:
        significand = tup[0].rstrip("0").rstrip(decimal_point)
        sign = tup[1][0].replace(positive_sign, "")
        exponent = tup[1][1:].lstrip("0")
        if significand == "1" and exponent != "":
            # reformat 1x10^y as 10^y
            significand = ""
        if exponent:
            exponent = "10^{%s%s}" % (sign, exponent)
        if significand and exponent:
            return r"$%s{\times}%s$" % (significand, exponent)
        else:
            return r"$%s%s$" % (significand, exponent)
    except IndexError:
        return s


class DimensionError(Exception):
    "Error due to incorrect / unsupported histogram dimension"

    def __init__(self, msg):
        "Histogram has incorrect / unsupported dimension"
        super().__init__(self, msg)


class ViolatesPlottableHistogramError(Exception):
    "Error due to histogram object violating the PlottableHistogram protocol"

    def __init__(self, msg):
        "Histogram violates PlottableHistogram protocol"
        super().__init__(self, msg)


class BinningMismatchError(Exception):
    "Error due to histogram binning mismatch"

    def __init__(self, msg):
        "Histogram binning mismatch error"
        super().__init__(self, msg)


class Background:
    """Histogram and errors corresponding to a single background"""

    __slots__ = ["bins", "label", "hist", "stat_errs", "syst_errs", "color"]

    def __init__(self, label, hist, stat_errs=None, syst_errs=None, color=None):
        """
        Histogram and errors corresponding to a single background

        Parameters
        -----------
        label : str
            Background label for legend
        hist : array_like or PlottableHistogram
            Bin contents. If hist is a ``PlottableHistogram`` stat_errs is ignored unless it is `sqrt` or `ignore`.
        stat_errs : array_like
            Statistical errors on hist
        syst_errs : array_like or PlottableHist
            Systematic errors on hist
        color : color
            Background color for histogram
        """
        if hasattr(hist, "axes"):  # Object should meet the PlottableHistogram protocol
            if not hasattr(hist, "values") or not hasattr(hist, "variances"):
                raise ViolatesPlottableHistogramError(
                    "hist violates PlottableHistogram protocol"
                )
            if len(hist.axes) != 1:
                raise DimensionError("Only 1D histograms are supported here")
            hist_obj = hist
            bins = _bins(hist.axes[0])
            hist = hist_obj.values()
            if not isinstance(stat_errs, str):
                stat_errs = (
                    None
                    if hist_obj.variances() is None
                    else _np.sqrt(hist_obj.variances())
                )
        else:
            bins = None
        if stat_errs is None:
            stat_errs = _np.zeros_like(hist)
        elif isinstance(stat_errs, str):
            stat_errs = stat_errs.lower()
            if "pois" in stat_errs or "sqrt" in stat_errs:
                stat_errs = _np.sqrt(hist)
            elif "ignore" in stat_errs:
                stat_errs = _np.zeros_like(hist)
            else:
                raise TypeError("Invalid stat_errs")
        else:
            if len(hist) != len(stat_errs):
                raise BinningMismatchError("Stat errors may have incorrect binning")
        if syst_errs is not None:
            if len(hist) != len(syst_errs):
                raise BinningMismatchError("Syst errors have incorrect binning")

        self.bins = bins
        self.hist = hist
        self.stat_errs = stat_errs
        if color is None:
            self.color = next(_hist_colors)["color"]
        else:
            self.color = color
        self.label = label
        if syst_errs is None:
            self.syst_errs = _np.zeros_like(stat_errs)
        else:
            self.syst_errs = syst_errs


def plot_band(bins, low, high, label=None, ax=None, **kwargs):
    """
    Draw a shaded band between high and low

    Use this for drawing error bands

    Parameters
    ----------
    bins : array_like
        Bin edges
    low : array_like
        Bin contents defining lower bound
    high : array_like
        Bin contents defining upper bound
    label : str, optional
        Label for legend. If label matches a line, the band will be attached to that line if ``draw_legend`` is used.
    ax : mpl.axes.Axes, optional
        Axes to draw band on (defaults to current axes)
    **kwargs
        Keyword arguments passed to `fill_between`
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    # duplicate each edge except first and last
    x = _np.stack((bins, bins), axis=-1).ravel()[1:-1]
    # duplicate each value (once for start, once for end)
    new_low = _np.stack((low, low), axis=-1).ravel()
    new_high = _np.stack((high, high), axis=-1).ravel()
    a = ax.fill_between(x, new_low, new_high, label=label, **kwargs)
    if label is not None:
        ax._ampllegend.bands[label].append(a)
    return a


def register_band(label, artist, ax=None):
    """
    Register a manually draw (e.g. with ``fill_between``) error band.

    Parameters
    ----------
    label : str
        Label of line to attach band to.
    artist : mpl.artist.Artist
        Band artist, e.g. ``PolyCollection`` returned by ``fill_between``.
    ax : mpl.axes.Axes, optional
        Axes to register band in (defaults to current axes).
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    ax._ampllegend.bands[label].append(artist)


def plot_backgrounds(
    backgrounds, bins=None, *, total_err=None, empty_stat_legend=False, ax=None
):
    """
    Plot stacked backgrounds

    Parameters
    ----------
    backgrounds : [Background]
        List of backgrounds to be plotted, in order (bottom to top)
    bins : array_like, optional
        Bin edges. To preserve backward compatibility, ``backgrounds`` and ``bins`` may be exchanged.
    total_err: array_like, optional
        Total uncertainty. If given, overrides per-background systematics. This is useful for showing post-fit uncertainties.
    empty_stat_legend: boolean, optional
        Add stat error band to legend even if empty. Defaults to False.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)

    Returns
    --------
    total_hist : array_like
        Total background histogram
    total_err : array_like
        Total error on background histogram
    """
    if bins is not None and isinstance(bins[0], Background):
        bins, backgrounds = backgrounds, bins
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    if len(backgrounds) < 1:
        return
    if bins is None:
        if backgrounds[0].bins is None:
            raise TypeError(
                "bins is required if backgrounds were not constructed from PlottableHists"
            )
        bins = backgrounds[0].bins
    if len(backgrounds[0].hist) != len(bins) - 1:
        raise BinningMismatchError("Invalid binning supplied")
    if total_err is not None:
        if len(total_err) != len(bins) - 1:
            raise BinningMismatchError("Total error may have incorrect binning")
    n_bkgs = len(backgrounds)

    total_stat_err = _np.zeros_like(backgrounds[0].hist, dtype=_np.float_)
    total_syst_err = _np.zeros_like(backgrounds[0].hist, dtype=_np.float_)
    total_hist = _np.zeros_like(backgrounds[0].hist, dtype=_np.float_)

    for i, bkg in enumerate(backgrounds):
        if len(bkg.hist) != len(total_stat_err):
            raise BinningMismatchError(f"Invalid binning for background {i}")
        total_stat_err += _np.square(bkg.stat_errs)
        if total_err is None:
            total_syst_err += _np.square(bkg.syst_errs)
        total_hist += bkg.hist
    # components still variances at this point
    if total_err is None:
        total_err = _np.sqrt(total_stat_err + total_syst_err)
        total_syst_err = _np.sqrt(total_syst_err)
    else:
        total_syst_err = _np.sqrt(total_err - total_stat_err)
    total_stat_err = _np.sqrt(total_stat_err)

    bin_centers = (bins[1:] + bins[:-1]) / 2
    if _np.sum(total_stat_err) != 0:
        ax._ampllegend.has_stat = True
        plot_band(
            bins,
            total_hist - total_stat_err,
            total_hist + total_stat_err,
            ax=ax,
            fc="transparent",
            ec="k",
            hatch=r"////",
            label="Stat. Uncertainty",
            zorder=6,
        )
    elif empty_stat_legend:
        ax._ampllegend.has_stat = True
    if _np.sum(total_syst_err) != 0.0:
        ax._ampllegend.has_syst = True
        plot_band(
            bins,
            total_hist - total_err,
            total_hist + total_err,
            color="grey",
            alpha=0.5,
            label="Stat. $\\oplus$ Syst. Unc.",
            zorder=5,
        )
    _, _, ps = ax.hist(
        _np.vstack([bin_centers] * n_bkgs).transpose(),
        bins=bins,
        weights=_np.vstack([b.hist for b in backgrounds]).transpose(),
        stacked=True,
        histtype="stepfilled",
        color=[b.color for b in backgrounds],
        label=[b.label for b in backgrounds],
    )
    for b, p in reversed(list(zip(backgrounds, ps))):
        _mpl.pyplot.setp(p, edgecolor="k", lw=1)
        if isinstance(p, list):
            ax._ampllegend.fill_hists[b.label] = p[0]
        else:
            ax._ampllegend.fill_hists[b.label] = p
    return total_hist, total_err


def plot_signal(
    label,
    bins,
    hist,
    stat_errs=None,
    syst_errs=None,
    color=None,
    attach_bands=False,
    ax=None,
):
    """
    Plot signal histogram

    NB: :func:`atlas_mpl_style.uhi.plot_signal` provides a version of this function that accepts a ``PlottableHistogram``.

    Parameters
    ----------
    label : str
        Label for legend
    bins : array_like
        Bin edges
    hist : array_like
        Bin contents
    stat_errs : array_like
        Statistical errors
    syst_errs : array_like
        Systematic errors
    color : color
        Line color
    attach_bands : boolean, optional
        Attach bands to line in legend. Defaults to False.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    have_syst = True
    have_stat = True
    if len(bins) - 1 != len(hist):
        raise BinningMismatchError("Invalid binning")
    if stat_errs is None:
        have_stat = False
        stat_errs = _np.zeros_like(hist)
    elif isinstance(stat_errs, str):
        stat_errs = stat_errs.lower()
        if "pois" in stat_errs or "sqrt" in stat_errs:
            stat_errs = _np.sqrt(hist)
        else:
            raise TypeError("Invalid stat_errs")
    else:
        if len(hist) != len(stat_errs):
            raise BinningMismatchError("Stat errors may have incorrect binning")
    if syst_errs is None:
        have_syst = False
        syst_errs = _np.zeros_like(hist)
    else:
        if len(hist) != len(syst_errs):
            raise BinningMismatchError("Incorrect binning for syst errors")
    bin_centers = (bins[1:] + bins[:-1]) / 2
    total_err = _np.sqrt(_np.square(stat_errs) + _np.square(syst_errs))
    _, _, p = ax.hist(
        bin_centers,
        bins=bins,
        weights=hist,
        histtype="step",
        label=label,
        lw=1,
        color=color,
    )
    if color is None:
        color = p[0].get_ec()
    # Use dummy artist to add to legend as straight line
    # Original patch won't appear due to the shared label
    ax._ampllegend.line_hists[label] = _mpl.lines.Line2D([0], [0], color=color, lw=1)
    if have_syst:
        ax._ampllegend.has_syst = True
        a_syst = plot_band(
            bins,
            hist - total_err,
            hist + total_err,
            color=color,
            ax=ax,
            alpha=0.25,
            zorder=5,
        )
    if have_stat:
        ax._ampllegend.has_stat = True
        a_stat = plot_band(
            bins,
            hist - stat_errs,
            hist + stat_errs,
            ax=ax,
            ec=color,
            fc="transparent",
            hatch=r"////",
            zorder=5,
        )
        if attach_bands:
            ax._ampllegend.bands[label].append(a_stat)
            if have_syst:
                # Has to be in this order
                ax._ampllegend.bands[label].append(a_syst)


def plot_data(bins, hist, stat_errs=None, color="k", label="Data", ax=None):
    """
    Plot data

    NB: :func:`atlas_mpl_style.uhi.plot_data` provides a version of this function that accepts a ``PlottableHistogram``.

    Parameters
    ----------
    label : str, optional
        Label for legend (default: "Data")
    bins : array_like
        Bin edges
    hist : array_like
        Bin contents
    stat_errs : array_like, optional
        Statistical errors
    color : color, optional
        Point color, defaults to black
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)

    Returns
    --------
    hist : array_like
        Data histogram
    stat_errs : array_like
        Statistical errors
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    if len(bins) - 1 != len(hist):
        raise BinningMismatchError("Invalid binning")

    if stat_errs is None:
        stat_errs = _np.zeros_like(hist)
    elif isinstance(stat_errs, str):
        stat_errs = stat_errs.lower()
        if "pois" in stat_errs or "sqrt" in stat_errs:
            stat_errs = _np.sqrt(hist)
        else:
            raise TypeError("Invalid stat_errs")
    else:
        if len(hist) != len(stat_errs):
            raise BinningMismatchError("Stat errors may have incorrect binning")
    bin_centers = (bins[1:] + bins[:-1]) / 2
    if _np.sum(stat_errs) == 0:
        a = ax.scatter(
            bin_centers,
            hist,
            s=25,
            c=color,
            marker="o",
            label=label,
            zorder=7,
        )
    else:
        a = ax.errorbar(
            bin_centers,
            hist,
            yerr=stat_errs,
            label=label,
            color=color,
            fmt="o",
            zorder=7,
            ms=5,
        )
    ax._ampllegend.data_hists[label] = a
    return hist, stat_errs


def plot_ratio(
    bins,
    data,
    data_errs,
    bkg,
    bkg_errs,
    ratio_ax,
    max_ratio=None,
    plottype="diff",
    offscale_errs=False,
):
    """
    Plot ratio plot

    NB: :func:`atlas_mpl_style.uhi.plot_ratio` provides a version of this function that accepts ``PlottableHistogram``s.

    Parameters
    ----------
    bins : array_like
        Bin edges
    data : array_like
        Data histogram bin contents
    data_errs : array_like
        Statistical errors on data
    bkg : array_like
        Total background histogram bin contents
    bkg_errs : array_like
        Total errors on total background
    ratio_ax : mpl.axes.Axes
        Ratio axes (produced using :func:`atlas_mpl_style.ratio_axes()`)
    max_ratio : float, optional
        Maximum ratio (defaults to 0.25 for "diff", 1.25 for "raw", 3.5 for "significances").
    plottype : {"diff", "raw", "significances"}
        | Type of ratio to plot.
        | "diff" : (data - bkg) / bkg
        | "raw" : data / bkg
        | "significances" : Significances (using :func:`atlas_mpl_style.utils.significance()`)
    offscale_err : boolean
        Draw error bars on off-scale points
    """
    # divide by zero is common -- ignore errors
    olderr = _np.seterr(all="ignore")
    if plottype == "diff":
        ratio = (data - bkg) / bkg
        if max_ratio is None:
            max_ratio = 0.25
        min_ratio = -max_ratio
    elif plottype == "raw":
        ratio = data / bkg
        if max_ratio is None:
            max_ratio = 1.25
        min_ratio = 1 - max_ratio
    elif plottype == "significances":
        ratio = _significance(data, data_errs, bkg, bkg_errs)
        if max_ratio is None:
            max_ratio = 3.5
        min_ratio = -max_ratio
    else:
        raise TypeError("Invalid plottype")
    # Increase limits by 10% to avoid tick labels clashing
    max_ratio *= 1.1
    min_ratio *= 1.1

    ratio_ax.axhline(1 if plottype == "raw" else 0, color="paper:red", lw=1)
    ratio_ax.set_ylim(min_ratio, max_ratio)
    if plottype == "diff":
        plot_band(
            bins, -bkg_errs / bkg, bkg_errs / bkg, color="grey", alpha=0.5, ax=ratio_ax
        )
    elif plottype == "raw":
        plot_band(
            bins,
            1 - (bkg_errs / bkg),
            1 + (bkg_errs / bkg),
            color="grey",
            alpha=0.5,
            ax=ratio_ax,
        )

    bin_centers = (bins[1:] + bins[:-1]) / 2
    out_of_range_up = _np.where(ratio > max_ratio, max_ratio, _np.NaN)
    out_of_range_down = _np.where(ratio < min_ratio, min_ratio, _np.NaN)
    ratio_ax.plot(
        bin_centers,
        out_of_range_up,
        marker=_mpl.markers.CARETUP,
        color="paper:red",
        lw=0,
    )
    ratio_ax.plot(
        bin_centers,
        out_of_range_down,
        marker=_mpl.markers.CARETDOWN,
        color="paper:red",
        lw=0,
    )
    if not offscale_errs:
        # set out of range to NaN so it doesn't get drawn
        ratio[~_np.isnan(out_of_range_up)] = _np.NaN
        ratio[~_np.isnan(out_of_range_down)] = _np.NaN
    if plottype == "significances":
        ratio_ax.plot(bin_centers, ratio, "ko", ms=3)
        ratio_ax.axhline(1, ls="--", color="paper:fg", alpha=0.5)
        ratio_ax.axhline(-1, ls="--", color="paper:fg", alpha=0.5)
        ratio_ax.axhline(2, ls="--", color="paper:fg", alpha=0.25)
        ratio_ax.axhline(-2, ls="--", color="paper:fg", alpha=0.25)
        ratio_ax.set_yticks(list(range(ceil(min_ratio), floor(max_ratio) + 1)))
    else:
        ratio_ax.errorbar(bin_centers, ratio, yerr=(data_errs / bkg), fmt="ko", ms=3)
    # re-enable errors
    _np.seterr(**olderr)


def draw_tag(text, ax=None):
    """
    Draw tag just outside plot region

    Parameters
    -------------
    text : str
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    ax.text(
        1, 1.0005, text, ha="right", va="bottom", fontsize=8, transform=ax.transAxes
    )


def plot_1d(
    label, bins, hist, stat_errs=None, color=None, attach_bands=False, ax=None, **kwargs
):
    """
    Plot single 1D histogram

    NB: :func:`atlas_mpl_style.uhi.plot_1d` provides a version of this function that accepts a ``PlottableHistogram``.

    Parameters
    ----------
    label : str
        Label for legend
    bins : array_like
        Bin edges
    hist : array_like
        Bin contents
    stat_errs : array_like, optional
        Statistical errors
    color : color, optional
        Line color
    attach_bands : boolean, optional
        Attach bands to line in legend. Defaults to False.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    **kwargs
        Extra parameters passed to ``plt.hist``
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    if len(bins) - 1 != len(hist):
        raise BinningMismatchError("Invalid binning")
    if isinstance(stat_errs, str):
        stat_errs = stat_errs.lower()
        if "pois" in stat_errs or "sqrt" in stat_errs:
            stat_errs = _np.sqrt(hist)
        else:
            raise TypeError("Invalid stat_errs")
    elif stat_errs is not None:
        if len(hist) != len(stat_errs):
            raise BinningMismatchError("Stat errors may have incorrect binning")
    bin_centers = (bins[1:] + bins[:-1]) / 2
    _, _, p = ax.hist(
        bin_centers,
        bins=bins,
        weights=hist,
        histtype="step",
        color=color,
        label=label,
        **kwargs,
    )
    if color is None:
        color = p[0].get_ec()
    # Use dummy artist to add to legend as straight line
    # Original patch won't appear due to the shared label
    ax._ampllegend.line_hists[label] = _mpl.lines.Line2D(
        [0], [0], color=color, **kwargs
    )
    if stat_errs is not None:
        ax._ampllegend.has_stat = True
        a = plot_band(
            bins,
            hist - stat_errs,
            hist + stat_errs,
            fc="transparent",
            ec=color,
            hatch=r"////",
            zorder=5,
        )
        if attach_bands:
            ax._ampllegend.bands[label].append(a)


def plot_2d(xbins, ybins, hist, ax=None, pad=0.05, **kwargs):
    """
    Plot 2D histogram

    NB: :func:`atlas_mpl_style.uhi.plot_2d` provides a version of this function that accepts a ``PlottableHistogram``.

    Parameters
    ----------
    xbins : array_like
        x bin edges
    bins : array_like
        y bin edges
    hist : array_like
        Bin contents
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    pad : float, optional
        Padding for colorbar in inches (defaults to 0.05)
    **kwargs
        Extra parameters passed to ``pcolormesh``

    Returns
    -------
    mesh : QuadMesh
    cbar : mpl.colorbar.Colorbar
    """
    if len(xbins) != hist.shape[0] + 1:
        raise BinningMismatchError("xbins does not match 1st axis of hist")
    if len(ybins) != hist.shape[1] + 1:
        raise BinningMismatchError("ybins does not match 2nd axis of hist")
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    X, Y = _np.meshgrid(xbins, ybins)
    mesh = ax.pcolormesh(X, Y, hist.transpose(), rasterized=True, **kwargs)
    ax.axis("scaled")
    ax.set_xlim(xbins[0], xbins[-1])
    ax.set_ylim(ybins[0], ybins[-1])
    cax = _make_axes_locatable(ax).append_axes("right", size="5%", pad=pad)
    _u.decorate_axes(cax)
    ax._amplaxesinfo.cbar = cax
    cax._amplaxesinfo.main_ax = ax
    cbar = ax.figure.colorbar(mesh, cax=cax)
    cax.yaxis.tick_right()
    return mesh, cbar


def plot_cutflow(
    labels, hist, ax=None, text=True, textcolor="w", horizontal=True, **kwargs
):
    """
    Plot cutflow from PlottableHistogram

    Parameters
    ----------
    labels : [str]
        Cutflow labels
    hist : PlottableHistogram
        Cutflow histogram
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    text : bool, optional
        Whether to label bars (default: True)
    textcolor: str, optional
        Text color
    horizontal : bool, optional
        Whether to draw horizontal bars (default: True)
    **kwargs
        Extra parameters passed to ``bar`` or ``barh``
    """
    resize_ax = False
    if ax is None:
        ax = _mpl.pyplot.gca()
        resize_ax = True  # only resize axes if they weren't provided
    _u.decorate_axes(ax)
    if len(labels) != len(hist):
        raise BinningMismatchError("Invalid binning")
    if horizontal:
        y = _np.arange(len(labels))[::-1]
        rects = ax.barh(
            y, hist, height=1, tick_label=labels, align="center", ec="k", **kwargs
        )
        if text:
            for rect in rects:
                w = rect.get_width()
                ax.annotate(
                    _formatSciNotation(w),
                    xy=(w, rect.get_y() + rect.get_height() / 2),
                    xytext=(-10, 0),
                    textcoords="offset points",
                    ha="right",
                    va="center",
                    fontsize=16,
                    color=textcolor,
                )
        if resize_ax:
            ax.set_ylim(-0.5, len(labels) + 2.5)
    else:
        x = _np.arange(len(labels))
        rects = ax.bar(x, hist, width=1, tick_label=labels, align="center", **kwargs)
        if text:
            for rect in rects:
                h = rect.get_height()
                ax.annotate(
                    _formatSciNotation(h),
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, -10),
                    textcoords="offset points",
                    ha="center",
                    va="top",
                    fontsize=16,
                    color=textcolor,
                )
        if resize_ax:
            ax.set_xlim(-0.5, len(labels) - 0.5)


def plot_limit(
    expected_label,
    x,
    expected,
    minus_one_sigma=None,
    plus_one_sigma=None,
    minus_two_sigma=None,
    plus_two_sigma=None,
    observed_label=None,
    observed=None,
    color=None,
    ax=None,
):
    """
    Plot a limit

    Parameters
    ----------
    expected_label : str
        Label for expected limit (for legend)
    x : array_like
        x values
    expected : array_like
        Expected limit
    minus_one_sigma : array_like, optional
        Lower edge of one sigma band
    plus_one_sigma : array_like, optional
        Upper edge of one sigma band
    minus_two_sigma : array_like, optional
        Lower edge of two sigma band
    plus_two_sigma : array_like, optional
        Upper edge of two sigma band
    observed_label : str, optional
        Label for observed limit
    observed : array_like, optional
        Observed limit
    color : color, optional
        Line color (if multiple limits are being drawn)
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    if len(x) != len(expected):
        raise BinningMismatchError("expected does not match x")
    if minus_one_sigma is not None and len(x) != len(minus_one_sigma):
        raise BinningMismatchError("minus_one_sigma does not match x")
    if plus_one_sigma is not None and len(x) != len(plus_one_sigma):
        raise BinningMismatchError("plus_one_sigma does not match x")
    if minus_two_sigma is not None and len(x) != len(minus_two_sigma):
        raise BinningMismatchError("minus_two_sigma does not match x")
    if plus_two_sigma is not None and len(x) != len(plus_two_sigma):
        raise BinningMismatchError("plus_two_sigma does not match x")
    if observed is not None and len(x) != len(observed):
        raise BinningMismatchError("observed does not match x")
    if (minus_one_sigma is None) != (plus_one_sigma is None):
        raise ValueError(
            "Either both minus_one_sigma and plus_one_sigma must be provided or neither"
        )
    if (minus_two_sigma is None) != (plus_two_sigma is None):
        raise ValueError(
            "Either both minus_two_sigma and plus_two_sigma must be provided or neither"
        )
    if (observed is None) != (observed_label is None):
        raise ValueError(
            "Either both observed and observed_label must be provided or neither"
        )
    conf = _u.LimitConfig()

    if minus_two_sigma is not None:
        conf.has_2sig = True
        ax.fill_between(
            x,
            minus_two_sigma,
            plus_two_sigma,
            color=("atlas:twosigma" if color is None else _colors.to_rgba(color, 0.25)),
        )
    if minus_one_sigma is not None:
        conf.has_1sig = True
        ax.fill_between(
            x,
            minus_one_sigma,
            plus_one_sigma,
            color=("atlas:onesigma" if color is None else _colors.to_rgba(color, 0.5)),
        )
    conf.color = "black" if color is None else color
    conf.exp_label = expected_label
    ax.plot(
        x,
        expected,
        "--",
        label=expected_label,
        color=conf.color,
    )
    if observed is not None:
        conf.has_obs = True
        conf.obs_label = observed_label
        ax.plot(
            x,
            observed,
            "-",
            label=observed_label,
            color=conf.color,
        )


def set_xlabel(label, ax=None, *args, **kwargs):
    """
    Set x label in ATLAS style (right aligned).
    If ``ratio_axes`` was used, the label will be set on the lowest ratio axes.

    Additional parameters are passed through to `ax.set_xlabel`.

    Parameters
    ----------
    label : str
        Label (LaTeX permitted)
    ax : mpl.axes.Axes, optional
        Axes to set x label on
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    if ax._amplaxesinfo.low_ax is None:
        ax.set_xlabel(label, x=1.0, ha="right", *args, **kwargs)
    else:
        ax._amplaxesinfo.low_ax.set_xlabel(label, x=1.0, ha="right", *args, **kwargs)


def set_ylabel(label, ax=None, *args, **kwargs):
    """
    Set y label in ATLAS style (top aligned).

    Additional parameters are passed through to ``ax.set_ylabel``.

    Parameters
    ----------
    label : str
        Label (LaTeX permitted)
    ax : mpl.axes.Axes, optional
        Axes to set y label on
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    ax.set_ylabel(label, y=1.0, ha="right", *args, **kwargs)


def set_zlabel(label, cbar=None, ax=None, **kwargs):
    """
    Set z label in ATLAS style (top aligned)

    The colorbar to add the label to is *required* unless ``plot_2d`` was used.

    Parameters
    ----------
    label : str
        Label (LaTeX permitted)
    cbar : mpl.colorbar.Colorbar, optional
        Colorbar to set label on. Not required if ``plot_2d`` was used.
    ax : mpl.axes.Axes, optional
        If ``plot_2d`` was used, the axes can optionally be provided here.
    """
    if cbar is not None:
        cbar.set_label(label, y=1.0, ha="right", **kwargs)
    else:
        if ax is None:
            ax = _mpl.pyplot.gca()
        if not hasattr(ax, "_amplaxesinfo"):
            raise ValueError(
                "Tried to set z label on inappropriate axes. Please provide cbar."
            )
        elif ax._amplaxesinfo.cbar is None:
            raise ValueError(
                "Tried to set z label on inappropriate axes. Please provide cbar."
            )
        else:
            ax._amplaxesinfo.cbar.set_ylabel(
                label, loc="right", y=1.0, ha="right", **kwargs
            )


def draw_atlas_label(
    x,
    y,
    ax=None,
    status="int",
    simulation=False,
    energy=None,
    lumi=None,
    desc=None,
    lumi_lt=False,
    *args,
    **kwargs,
):
    """
    Draw ATLAS label.

    Additional parameters are passed through to ``ax.text``.

    Parameters
    ----------
    x : float
        x position (top left)
    y : float
        y position (top left)
    ax : mpl.axes.Axes, optional
        Axes to draw label in
    status : [ *'int'* | 'wip' | 'prelim' | 'final' | 'opendata' ], optional
        Approval status
    simulation : bool (optional, default ``False``)
        Does the plot show only MC simulation results
    energy : str, optional
        Centre of mass energy, including units
    lumi : float or str, optional
        Integrated luminosity in /fb. If str, the units should be included.
    lumi_lt: bool, optional
        True if only a subset of data was processed
    desc : str, optional
        Additional description
    """
    global _atlas_label
    if ax is None:
        ax = _mpl.pyplot.gca()
    sim_str = "Simulation " if simulation else ""

    if status == "final":
        status_str = ""
    elif status == "int":
        status_str = "Internal"
    elif status == "wip":
        status_str = "Work in Progress"
    elif status == "prelim":
        status_str = "Preliminary"
    elif status == "opendata":
        status_str = "Open Data"
    else:
        status_str = status

    show_e_nl = False
    if energy is not None:
        show_e_nl = True
        energy_str = rf"$\sqrt{{s}} = $ {energy}"
    else:
        energy_str = ""

    if lumi is not None:
        show_e_nl = True
        if isinstance(lumi, str):
            lumi_str = f", {lumi}"
        else:
            if _usetex:
                lumi_str = (
                    fr', ${"< " if lumi_lt else ""}{lumi:.4g} \ '
                    fr"\textsf{{fb}}^{{-1}}$"
                )
            else:
                lumi_str = (
                    fr', ${"< " if lumi_lt else ""}{lumi:.4g} \ ' fr"{{fb}}^{{-1}}$"
                )
    else:
        lumi_str = ""

    desc_line = desc is not None
    if _usetex:
        nl = r"\\"
        label = (
            fr"\textbf{{\textit{{{_atlas_label}}}}} {sim_str}{status_str}"
            fr'{nl + "for education only" if status=="opendata" else ""}'
            fr'{nl if show_e_nl else ""}'
            fr'{energy_str}{lumi_str}{nl if desc_line else ""}'
            fr'{desc if desc_line else ""}'
        )
        ax.text(
            x,
            y,
            label,
            *args,
            ha="left",
            va="top",
            multialignment="left",
            transform=ax.transAxes,
            **kwargs,
        )
    else:
        nl = "\n"
        label = (
            fr'{"for education only" if status=="opendata" else ""}'
            fr'{nl if show_e_nl and status=="opendata" else ""}'
            fr'{energy_str}{lumi_str}{nl if desc_line else ""}'
            fr'{desc if desc_line else ""}'
        )
        # Based on the rainbox_text example in MPL
        prop = dict(
            ha="left",
            va="top",
            multialignment="left",
        )
        atl_txt = ax.text(
            x,
            y,
            f"{_atlas_label} ",
            *args,
            style="italic",
            weight="bold",
            transform=ax.transAxes,
            **prop,
            **kwargs,
        )
        atl_txt.draw(ax.figure.canvas.get_renderer())
        ex = atl_txt.get_window_extent()
        side_t = _mpl.transforms.offset_copy(
            atl_txt._transform, x=ex.width, units="dots"
        )
        under_t = _mpl.transforms.offset_copy(
            atl_txt._transform, y=-ex.height, units="dots"
        )
        ax.text(
            x,
            y,
            f"{sim_str}{status_str}",
            *args,
            transform=side_t,
            **prop,
            **kwargs,
        )
        ax.text(
            x,
            y,
            label,
            *args,
            transform=under_t,
            **prop,
            **kwargs,
        )


def draw_legend(*args, ax=None, **kwargs):
    """
    Add legend to axes with data first, and uncertainties last.

    Parameters
    ----------
    ax : mpl.axes.Axes, optional
       Axes to draw legend on (defaults to current axes)
    *args :
       Passed to ``ax.legend``
    **kwargs :
       Passed to ``ax.legend``
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    ptype = _u.plot_type(ax)
    if ptype is None:
        ax.legend(*args, **kwargs)
    elif ptype == "limits":
        _u.draw_limit_legend(ax, args, kwargs)
    elif ptype == "hists":
        _u.draw_hists_legend(ax, args, kwargs)
