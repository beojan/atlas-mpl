"""
Plot histograms, ratios, and limits given as arrays.

For histogram objects that follow the UHI PlottableHistogram protocol, use the functions
in :mod:`atlas_mpl_style.uhi`. Draw the legend with :func:`draw_legend` to order and group
the entries.
"""

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

class LabeledBinsError(Exception):
    """Raised when bins have labels where numeric edges are needed, or the reverse."""


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
    """Raised when a histogram has the wrong number of dimensions."""


class ViolatesPlottableHistogramError(Exception):
    """Raised when an object does not follow the UHI PlottableHistogram protocol."""


class BinningMismatchError(Exception):
    """Raised when arrays that describe the same bins have different lengths."""


import atlas_mpl_style._uhi_validation as _uhi_val

FlowNotSupportedError = _uhi_val.FlowNotSupportedError
UnsupportedKindError = _uhi_val.UnsupportedKindError


class Background:
    """A background histogram and its uncertainties, for :func:`plot_backgrounds`."""

    __slots__ = ["bins", "label", "hist", "stat_errs", "syst_errs", "color"]

    def __init__(self, label, hist, stat_errs=None, syst_errs=None, color=None):
        """
        Store a background histogram for :func:`plot_backgrounds`.

        Parameters
        ----------
        label : str
            Legend label.
        hist : array_like or PlottableHistogram
            Bin contents. A PlottableHistogram also supplies the bin edges, and the square root
            of its variances as the statistical uncertainties.
        stat_errs : array_like or {"sqrt", "ignore"}, optional
            Statistical uncertainty in each bin, zero by default. ``"sqrt"`` uses the square root
            of the bin contents and ``"ignore"`` uses zero. An array is ignored when ``hist`` is a
            PlottableHistogram.
        syst_errs : array_like or PlottableHistogram, optional
            Systematic uncertainty in each bin. For a PlottableHistogram, its bin values are used.
        color : color-like, optional
            Fill color (defaults to the next color in the color cycle).
        """
        if hasattr(hist, "axes"):  # Object should meet the PlottableHistogram protocol
            _uhi_val.validate_plottable_histogram(
                hist, name="hist", ndim=1, check_kind=True, func_name="Background"
            )
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
            if hasattr(syst_errs, "axes"):
                _uhi_val.validate_plottable_histogram(
                    syst_errs,
                    name="syst_errs",
                    ndim=1,
                    check_kind=True,
                    func_name="Background",
                )
                if len(syst_errs.axes[0]) != len(hist):
                    raise BinningMismatchError("Syst errors have incorrect binning")
                syst_errs = syst_errs.values()
            elif len(hist) != len(syst_errs):
                raise BinningMismatchError("Syst errors have incorrect binning")

        self.bins = bins
        self.hist = hist
        self.stat_errs = stat_errs
        self.color = color
        self.label = label
        if syst_errs is None:
            self.syst_errs = _np.zeros_like(stat_errs)
        else:
            self.syst_errs = syst_errs


def plot_band(bins, low, high, label=None, ax=None, **kwargs):
    """
    Draw a shaded band over histogram bins, such as an uncertainty band.

    Parameters
    ----------
    bins : array_like
        Bin edges.
    low, high : array_like
        Lower and upper edge of the band in each bin.
    label : str, optional
        Legend label. If it matches the label of a line, :func:`draw_legend` draws the band
        behind that line in the legend.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    **kwargs
        Passed to ``ax.fill_between``.

    Returns
    -------
    matplotlib.collections.FillBetweenPolyCollection
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
    Show a band you drew yourself behind its line in the legend.

    Parameters
    ----------
    label : str
        Label of the line the band belongs to.
    artist : matplotlib.artist.Artist
        The band, for example the collection returned by ``fill_between``.
    ax : matplotlib.axes.Axes, optional
        Axes holding the line (defaults to current axes).
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    ax._ampllegend.bands[label].append(artist)


def plot_backgrounds(
        backgrounds, bins=None, *, show_errs=False, total_err=None, empty_stat_legend=False, ax=None
):
    """
    Plot backgrounds as a stacked histogram.

    Parameters
    ----------
    backgrounds : list of Background
        Backgrounds in stacking order, from bottom to top.
    bins : array_like, optional
        Bin edges. Required unless the backgrounds were built from PlottableHistograms. For
        backward compatibility, ``backgrounds`` and ``bins`` may be given in either order.
    show_errs : bool, optional
        Draw the uncertainty bands of the total background. Defaults to False, following the
        PubCom recommendation.
    total_err : array_like, optional
        Total uncertainty in each bin, replacing the combined systematic uncertainties of the
        backgrounds. Use it for post-fit uncertainties.
    empty_stat_legend : bool, optional
        Add a statistical uncertainty entry to the legend even when no such band is drawn.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).

    Returns
    -------
    total_hist : numpy.ndarray
        Sum of the backgrounds.
    total_err : numpy.ndarray
        Total uncertainty on the sum. Pass ``(total_hist, total_err)`` to
        :func:`atlas_mpl_style.uhi.plot_ratio`, or the two arrays to :func:`plot_ratio`.
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

    total_stat_err = _np.zeros_like(backgrounds[0].hist, dtype=_np.float64)
    total_syst_err = _np.zeros_like(backgrounds[0].hist, dtype=_np.float64)
    total_hist = _np.zeros_like(backgrounds[0].hist, dtype=_np.float64)

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
        # total_err is an uncertainty, total_stat_err is still a variance here
        total_syst_err = _np.sqrt(
            _np.clip(_np.square(total_err) - total_stat_err, 0, None)
        )
    total_stat_err = _np.sqrt(total_stat_err)

    bin_centers = (bins[1:] + bins[:-1]) / 2
    _u.fit_x_to_bins(ax, bins)
    if show_errs:
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
                ax=ax,
                color="grey",
                alpha=0.5,
                label="Stat. $\\oplus$ Syst. Unc.",
                zorder=5,
            )
    elif empty_stat_legend:
        ax._ampllegend.has_stat = True

    # Resolve colors for backgrounds that do not specify an explicit color
    colors = []
    for b in backgrounds:
        if b.color is not None:
            colors.append(b.color)
        else:
            c = ax._get_lines.get_next_color()
            b.color = c
            colors.append(c)

    _, _, ps = ax.hist(
        _np.vstack([bin_centers] * n_bkgs).transpose(),
        bins=bins,
        weights=_np.vstack([b.hist for b in backgrounds]).transpose(),
        stacked=True,
        histtype="stepfilled",
        color=colors,
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
    Plot a signal as an unfilled histogram over the stacked backgrounds.

    A fitted signal belongs in the stack as a :class:`Background`.

    .. note:: :func:`atlas_mpl_style.uhi.plot_signal` takes a ``PlottableHistogram`` instead.

    Parameters
    ----------
    label : str
        Legend label.
    bins : array_like
        Bin edges.
    hist : array_like
        Bin contents.
    stat_errs : array_like or "sqrt", optional
        Statistical uncertainty in each bin, drawn as a hatched band. ``"sqrt"`` uses the
        square root of the bin contents.
    syst_errs : array_like, optional
        Systematic uncertainty in each bin. A shaded band shows the statistical and
        systematic uncertainties added in quadrature.
    color : color-like, optional
        Line and band color (defaults to the next color in the color cycle).
    attach_bands : bool, optional
        Draw the bands behind the signal's line in the legend. Defaults to False.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
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
    _u.fit_x_to_bins(ax, bins)
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
    Plot data as points with error bars.

    .. note:: :func:`atlas_mpl_style.uhi.plot_data` takes a ``PlottableHistogram`` instead.

    Parameters
    ----------
    bins : array_like
        Bin edges.
    hist : array_like
        Bin contents.
    stat_errs : array_like or "sqrt", optional
        Statistical uncertainty in each bin. ``"sqrt"`` uses the square root of the bin
        contents. If omitted, the points have no error bars.
    color : color-like, optional
        Point color (defaults to black).
    label : str, optional
        Legend label (defaults to "Data").
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).

    Returns
    -------
    hist : array_like
        The bin contents.
    stat_errs : numpy.ndarray
        The statistical uncertainties. Pass these and ``hist`` to :func:`plot_ratio`.
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
    _u.fit_x_to_bins(ax, bins)
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
    Draw a ratio plot comparing data with the total background.

    The background uncertainty is drawn as a grey band, except for ``"significances"``. Points
    outside the y range are marked with red arrows at its edge.

    .. note:: :func:`atlas_mpl_style.uhi.plot_ratio` takes ``PlottableHistogram`` objects instead.

    Parameters
    ----------
    bins : array_like
        Bin edges.
    data, data_errs : array_like
        Data bin contents and statistical uncertainties, as returned by :func:`plot_data`.
    bkg, bkg_errs : array_like
        Total background and its uncertainty, as returned by :func:`plot_backgrounds`.
    ratio_ax : matplotlib.axes.Axes
        Ratio panel from :func:`atlas_mpl_style.ratio_axes`.
    max_ratio : float, optional
        Top of the y range: 0.25 for ``"diff"``, 1.25 for ``"raw"``, and 3.5 for
        ``"significances"`` by default. The range is symmetric about the reference line (1
        for ``"raw"``, otherwise 0). It is then widened by 10%, so that tick labels at the ends
        of the range do not clash with those of the panel above or below.
    plottype : {"diff", "raw", "significances"}, optional
        ``"diff"`` plots (data - bkg) / bkg, ``"raw"`` plots data / bkg, and
        ``"significances"`` plots the significance in each bin, as defined in
        https://cds.cern.ch/record/2643488 (see :func:`atlas_mpl_style.utils.significance`).
        Defaults to ``"diff"``.
    offscale_errs : bool, optional
        Also draw the error bars of points outside the y range. Defaults to False.
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
        min_ratio = 2 - max_ratio
    elif plottype == "significances":
        ratio = _significance(data, data_errs, bkg, bkg_errs)
        if max_ratio is None:
            max_ratio = 3.5
        min_ratio = -max_ratio
    else:
        raise TypeError("Invalid plottype")
    # Widen limits by 10% about the reference line to avoid tick labels clashing
    centre = 1 if plottype == "raw" else 0
    max_ratio = centre + 1.1 * (max_ratio - centre)
    min_ratio = centre + 1.1 * (min_ratio - centre)

    ratio_ax.axhline(centre, color="paper:red", lw=1)
    ratio_ax.set_ylim(min_ratio, max_ratio)
    if plottype == "raw":
        # ratio_axes places ticks symmetrically about 0. Centre them on 1 instead.
        offsets = _mpl.ticker.MaxNLocator(
            symmetric=True, prune="both", min_n_ticks=5, nbins=4
        ).tick_values(min_ratio - 1, max_ratio - 1)
        ratio_ax.yaxis.set_major_locator(_mpl.ticker.FixedLocator(offsets + 1))
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
    _u.decorate_axes(ratio_ax)
    _u.fit_x_to_bins(ratio_ax, bins)
    out_of_range_up = _np.where(ratio > max_ratio, max_ratio, _np.nan)
    out_of_range_down = _np.where(ratio < min_ratio, min_ratio, _np.nan)
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
        ratio[~_np.isnan(out_of_range_up)] = _np.nan
        ratio[~_np.isnan(out_of_range_down)] = _np.nan
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
    Draw small text just above the top-right corner of the axes.

    Parameters
    ----------
    text : str
        Text to draw.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
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
    Plot a 1D histogram as an unfilled line.

    .. note:: :func:`atlas_mpl_style.uhi.plot_1d` takes a ``PlottableHistogram`` instead.

    Parameters
    ----------
    label : str
        Legend label.
    bins : array_like
        Bin edges.
    hist : array_like
        Bin contents.
    stat_errs : array_like or "sqrt", optional
        Statistical uncertainty in each bin, drawn as a hatched band. ``"sqrt"`` uses the
        square root of the bin contents.
    color : color-like, optional
        Line color (defaults to the next color in the color cycle).
    attach_bands : bool, optional
        Draw the band behind the line in the legend. Defaults to False.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    **kwargs
        Passed to ``ax.hist``.
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
    _u.fit_x_to_bins(ax, bins)
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
        [0],
        [0],
        color=color,
        linestyle=p[0].get_linestyle(),
        linewidth=p[0].get_linewidth(),
        alpha=p[0].get_alpha(),
    )
    if stat_errs is not None:
        ax._ampllegend.has_stat = True
        a = plot_band(
            bins,
            hist - stat_errs,
            hist + stat_errs,
            ax=ax,
            fc="transparent",
            ec=color,
            hatch=r"////",
            zorder=5,
        )
        if attach_bands:
            ax._ampllegend.bands[label].append(a)


def plot_2d(xbins, ybins, hist, ax=None, pad=0.05, **kwargs):
    """
    Plot a 2D histogram as a color map with a colorbar on the right.

    The x and y axes get the same scale, which suits related quantities such as two masses,
    and their limits are set to the bin edges. For unrelated quantities, call
    ``ax.set_aspect("auto")`` afterwards to let the axes fill their usual space.

    .. note:: :func:`atlas_mpl_style.uhi.plot_2d` takes a ``PlottableHistogram`` instead.

    Parameters
    ----------
    xbins, ybins : array_like
        Bin edges along x and y.
    hist : numpy.ndarray
        Bin contents, indexed as ``hist[x, y]``.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    pad : float, optional
        Gap between the axes and the colorbar, in inches. Defaults to 0.05.
    **kwargs
        Passed to ``ax.pcolormesh``.

    Returns
    -------
    mesh : matplotlib.collections.QuadMesh
    cbar : matplotlib.colorbar.Colorbar
        Use :func:`set_zlabel` to label it.
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
    ax.figure.sca(ax)
    return mesh, cbar


def plot_cutflow(
    labels, hist, ax=None, text=True, textcolor="w", horizontal=True, **kwargs
):
    """
    Plot a cutflow as a bar chart with the yield on each bar.

    .. note:: :func:`atlas_mpl_style.uhi.plot_cutflow` takes a ``PlottableHistogram`` with
       labelled bins instead.

    Parameters
    ----------
    labels : list of str
        Name of each cut.
    hist : array_like
        Yield after each cut.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on. If omitted, the current axes are used and their limits are set to
        fit the bars.
    text : bool, optional
        Write the yield on each bar. Defaults to True.
    textcolor : color-like, optional
        Color of the yields (defaults to white).
    horizontal : bool, optional
        Draw horizontal bars, with the first cut at the top. Defaults to True.
    **kwargs
        Passed to ``ax.barh`` or ``ax.bar``.
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
    Plot an expected limit with optional ±1σ and ±2σ bands and an observed limit.

    Parameters
    ----------
    expected_label : str
        Legend label for the expected limit.
    x : array_like
        x values.
    expected : array_like
        Expected limit, drawn as a dashed line.
    minus_one_sigma, plus_one_sigma : array_like, optional
        Lower and upper edges of the ±1σ band. Give both or neither.
    minus_two_sigma, plus_two_sigma : array_like, optional
        Lower and upper edges of the ±2σ band. Give both or neither.
    observed_label : str, optional
        Legend label for the observed limit. Required with ``observed``.
    observed : array_like, optional
        Observed limit, drawn as a solid line.
    color : color-like, optional
        Color of the lines and bands, to tell several limits apart. Without it, the lines are
        black and the bands green and yellow.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
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
    # Left as None when no color is given, so the legend uses the default band colors
    conf.color = color
    line_color = "black" if color is None else color
    conf.exp_label = expected_label
    ax.plot(
        x,
        expected,
        "--",
        label=expected_label,
        color=line_color,
    )
    if observed is not None:
        conf.has_obs = True
        conf.obs_label = observed_label
        ax.plot(
            x,
            observed,
            "-",
            label=observed_label,
            color=line_color,
        )
    ax._ampllegend.limits[expected_label] = conf


def set_xlabel(label, ax=None, *args, **kwargs):
    """
    Set the x-axis label, aligned to the right end of the axis.

    If ``ax`` is the main panel from :func:`atlas_mpl_style.ratio_axes`, the label goes on the
    lowest ratio panel.

    Parameters
    ----------
    label : str
        Label text.
    ax : matplotlib.axes.Axes, optional
        Axes to label (defaults to current axes).
    *args, **kwargs
        Passed to ``ax.set_xlabel``.

    Returns
    -------
    matplotlib.text.Text
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    kwargs.setdefault("x", 1.0)
    kwargs.setdefault("ha", "right")
    if ax._amplaxesinfo.low_ax is None:
        return ax.set_xlabel(label, *args, **kwargs)
    else:
        return ax._amplaxesinfo.low_ax.set_xlabel(label, *args, **kwargs)


def set_ylabel(label, ax=None, *args, **kwargs):
    """
    Set the y-axis label, aligned to the top of the axis.

    Parameters
    ----------
    label : str
        Label text.
    ax : matplotlib.axes.Axes, optional
        Axes to label (defaults to current axes).
    *args, **kwargs
        Passed to ``ax.set_ylabel``.

    Returns
    -------
    matplotlib.text.Text
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    kwargs.setdefault("y", 1.0)
    kwargs.setdefault("ha", "right")
    ret = ax.set_ylabel(label, *args, **kwargs)
    if hasattr(ax, "_amplaxesinfo"):
        axs = []
        if ax._amplaxesinfo.main_ax is not None:
            axs.append(ax._amplaxesinfo.main_ax)
        axs.append(ax)
        if ax._amplaxesinfo.low_ax is not None:
            if isinstance(ax._amplaxesinfo.low_ax, list):
                axs.extend(ax._amplaxesinfo.low_ax)
            else:
                axs.append(ax._amplaxesinfo.low_ax)
        if len(axs) > 1:
            ax.figure.align_ylabels(axs)
    return ret


def set_zlabel(label, cbar=None, ax=None, **kwargs):
    """
    Set the colorbar label, aligned to the top of the colorbar.

    Parameters
    ----------
    label : str
        Label text.
    cbar : matplotlib.colorbar.Colorbar, optional
        Colorbar to label.
    ax : matplotlib.axes.Axes, optional
        Axes passed to :func:`plot_2d`, whose colorbar is labelled when ``cbar`` is not given
        (defaults to current axes).
    **kwargs
        Text properties for the label.

    Raises
    ------
    ValueError
        If ``cbar`` is not given and ``ax`` has no colorbar from :func:`plot_2d`.
    """
    kwargs.setdefault("y", 1.0)
    kwargs.setdefault("ha", "right")
    if cbar is not None:
        cbar.set_label(label, **kwargs)
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
            ax._amplaxesinfo.cbar.set_ylabel(label, **kwargs)


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
    Draw the ATLAS label.

    Parameters
    ----------
    x, y : float
        Position of the top-left corner of the label, in axes coordinates.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    status : {'int', 'wip', 'prelim', 'final', 'opendata', 'opendata-res'} or str, optional
        ``'int'`` draws "Internal", ``'wip'`` "Work In Progress", ``'prelim'`` "Preliminary",
        and ``'opendata'`` and ``'opendata-res'`` "Open Data". ``'opendata'`` also adds the line
        "for education only". ``'final'`` and None draw no status, and any other string is
        drawn as given. Defaults to ``'int'``.
    simulation : bool, optional
        Add "Simulation" to the label. Defaults to False.
    energy : str, optional
        Centre-of-mass energy with units, such as ``"13 TeV"``.
    lumi : float or str, optional
        Integrated luminosity. A number is in fb⁻¹. A string is drawn as given and must
        include its units.
    desc : str, optional
        Further lines of text below the label.
    lumi_lt : bool, optional
        Prefix a numeric luminosity with "<". Defaults to False.
    *args, **kwargs
        Passed to ``ax.text``.
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
        status_str = "Work In Progress"
    elif status == "prelim":
        status_str = "Preliminary"
    elif status == "opendata" or status == "opendata-res":
        status_str = "Open Data"
    elif status is None:
        status_str = ""
    else:
        status_str = status

    show_e_nl = False
    if energy is not None:
        show_e_nl = True
        energy_str = rf"$\sqrt{{\mathit{{s}}}} = $ {energy}"
    else:
        energy_str = ""

    if lumi is not None:
        show_e_nl = True
        sep = ", " if energy is not None else ""
        if isinstance(lumi, str):
            lumi_str = f"{sep}{lumi}"
        else:
            lt_str = "< " if lumi_lt else ""
            if _usetex:
                lumi_str = (
                    rf'{sep}${lt_str}{lumi:.4g} \ '
                    rf"\textsf{{fb}}^{{-1}}$"
                )
            else:
                lumi_str = (
                    rf'{sep}${lt_str}{lumi:.4g} \ ' rf"{{fb}}^{{-1}}$"
                )
    else:
        lumi_str = ""

    if _usetex:
        nl = r"\\"
        first_line = rf"\textbf{{\textit{{{_atlas_label}}}}}"
    else:
        nl = "\n"
        first_line = rf"$\mathbfit{{{_atlas_label}}}$"
    if sim_str or status_str:
        first_line += f" {sim_str}{status_str}".rstrip()

    lines = [first_line]
    if status == "opendata":
        lines.append("for education only")
    if show_e_nl:
        lines.append(f"{energy_str}{lumi_str}")
    if desc:
        if _usetex:
            lines.append(desc.replace("\n", r"\\"))
        else:
            lines.append(desc)
    label = nl.join(lines)

    kwargs.setdefault("ha", "left")
    kwargs.setdefault("va", "top")
    kwargs.setdefault("multialignment", "left")
    kwargs.setdefault("transform", ax.transAxes)
    ax.text(
        x,
        y,
        label,
        *args,
        **kwargs,
    )


def draw_legend(*, ax=None, **kwargs):
    """
    Draw a legend with entries in the standard order.

    Histogram legends list the data first, then stacked backgrounds, uncertainties, and lines.
    Limit legends list the observed and expected limits with their bands. Entries drawn with
    plain Matplotlib calls come last. A band from :func:`plot_band` or :func:`register_band`
    is drawn behind the line it belongs to in the legend.

    Parameters
    ----------
    ax : matplotlib.axes.Axes, optional
        Axes to draw the legend on (defaults to current axes).
    **kwargs
        Passed to ``ax.legend``.
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    _u.decorate_axes(ax)
    ptype = _u.plot_type(ax)
    if ptype is None:
        ax.legend(**kwargs)
    elif ptype == "limits":
        _u.draw_limit_legend(ax, kwargs)
    elif ptype == "hists":
        _u.draw_hists_legend(ax, kwargs)
