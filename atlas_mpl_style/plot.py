import matplotlib as _mpl
import numpy as _np
from atlas_mpl_style.utils import significance as _significance


class BinningMismatchError(Exception):
    "Error due to histogram binning mismatch"

    def __init__(self, msg):
        "Histogram binning mismatch error"
        super().__init__(self, msg)


class Background:
    """Histogram and errors corresponding to a single background"""

    __slots__ = ["label", "hist", "stat_errs", "syst_errs", "color"]

    def __init__(self, label, hist, stat_errs, syst_errs=None, color=None):
        """
        Histogram and errors corresponding to a single background

        Parameters
        -----------
        label : str
            Background label for legend
        hist : array_like
            Bin contents
        stat_errs : array_like
            Statistical errors on hist
        syst_errs : array_like
            Systematic errors on hist
        color : color
            Background color for histogram
        """
        if len(hist) != len(stat_errs):
            raise BinningMismatchError("Stat errors may have incorrect binning")
        if syst_errs is not None:
            if len(hist) != len(syst_errs):
                raise BinningMismatchError("Syst errors have incorrect binning")

        self.hist = hist
        self.stat_errs = stat_errs
        self.color = color
        self.label = label
        if syst_errs is None:
            syst_errs = _np.zeros_like(stat_errs)
        else:
            self.syst_errs = syst_errs


def plot_band(bins, low, high, ax=None, **kwargs):
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
    ax : mpl.axes.Axes, optional
        Axes to draw band on (defaults to current axes)
    **kwargs
        Keyword arguments passed to `fill_between`
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    # duplicate each edge except first and last
    x = _np.stack((bins, bins), axis=-1).ravel()[1:-1]
    # duplicate each value (once for start, once for end)
    new_low = _np.stack((low, low), axis=-1).ravel()
    new_high = _np.stack((high, high), axis=-1).ravel()
    ax.fill_between(x, new_low, new_high, **kwargs)


def plot_backgrounds(bins, backgrounds, ax=None):
    """
    Plot stacked backgrounds

    Parameters
    ----------

    bins : array_like
        Bin edges
    backgrounds : [Background]
        List of backgrounds to be plotted, in order (bottom to top)
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)

    Returns
    --------
    total_hist : array_like
        Sum of all bin contents
    total_err : array_like
        The total sum in quadrature of all uncertainties
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    if len(backgrounds) < 1:
        return
    if len(backgrounds[0].hist) != len(bins) - 1:
        raise BinningMismatchError("Invalid binning supplied")
    n_bkgs = len(backgrounds)

    total_stat_err = _np.zeros_like(backgrounds[0].hist)
    total_syst_err = _np.zeros_like(backgrounds[0].hist)
    total_hist = _np.zeros_like(backgrounds[0].hist)

    for i, bkg in enumerate(backgrounds):
        if len(bkg.hist) != len(total_stat_err):
            raise BinningMismatchError(f"Invalid binning for background {i}")
        total_stat_err += _np.square(bkg.stat_errs)
        total_syst_err += _np.square(bkg.syst_errs)
        total_hist += bkg.hist
    # components still variances at this point
    total_err = _np.sqrt(total_stat_err + total_syst_err)
    total_stat_err = _np.sqrt(total_stat_err)
    total_syst_err = _np.sqrt(total_syst_err)
    bin_centers = (bins[1:] + bins[:-1]) / 2
    _, _, ps = ax.hist(
        _np.vstack([bin_centers] * n_bkgs).transpose(),
        bins=bins,
        weights=_np.vstack([b.hist for b in backgrounds]).transpose(),
        stacked=True,
        histtype="stepfilled",
        color=[b.color for b in backgrounds],
        label=[b.label for b in backgrounds],
    )
    for p in ps:
        _mpl.pyplot.setp(p, edgecolor="k", lw=1)
    plot_band(
        bins,
        total_hist - total_err,
        total_hist + total_err,
        color="grey",
        alpha=0.5,
        label="Stat. $\\bigoplus$ Syst. Unc.",
        zorder=5,
    )
    plot_band(
        bins,
        total_hist - total_stat_err,
        total_hist + total_stat_err,
        fc="transparent",
        hatch=r"////",
        label="Stat. Unc.",
        zorder=5,
    )
    return total_hist, total_err


def plot_signal(label, bins, hist, stat_errs, syst_errs=None, color=None, ax=None):
    """
    Plot signal histogram

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
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    if len(bins) - 1 != len(hist) != len(stat_errs):
        raise BinningMismatchError("Invalid binning")
    if syst_errs is None:
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
    plot_band(
        bins, hist - total_err, hist + total_err, color=color, alpha=0.25, zorder=5
    )
    plot_band(
        bins,
        hist - stat_errs,
        hist + stat_errs,
        ec=color,
        fc="transparent",
        hatch=r"////",
        zorder=5,
    )


def plot_data(bins, hist, stat_errs=None, color="k", label="Data", ax=None):
    """
    Plot data

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
    color : color
        Line color
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
    if len(bins) - 1 != len(hist):
        raise BinningMismatchError("Invalid binning")
    if stat_errs is None:
        stat_errs = _np.sqrt(hist)
    if len(bins) - 1 != len(stat_errs):
        raise BinningMismatchError("Incorrect binning for stat errors")
    bin_centers = (bins[1:] + bins[:-1]) / 2
    ax.errorbar(
        bin_centers,
        hist,
        yerr=stat_errs,
        label=label,
        color=color,
        fmt="o",
        zorder=7,
        ms=5,
    )
    return hist, stat_errs


def plot_ratio(
    bins, data, data_errs, bkg, bkg_errs, ratio_ax, max_ratio=None, plottype="diff"
):
    """
    Plot ratio plot

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
        Ratio axes (produced using `ampl.ratio_axes()`)
    max_ratio : float, optional
        Maximum ratio (defaults to 0.2 for "diff", 1.2 for "raw",
                       3 for "significances")
    plottype : {"diff", "raw", "significances"}
        Type of ratio to plot.
        "diff" : (data - bkg) / bkg
        "raw" : data / bkg
        "significances" : Significances (from `ampl.utils.significance()`)
    """
    # divide by zero is common -- ignore errors
    olderr = _np.seterr(all="ignore")
    if plottype == "diff":
        ratio = (data - bkg) / bkg
        if max_ratio is None:
            max_ratio = 0.2
        min_ratio = -max_ratio
    elif plottype == "raw":
        ratio = data / bkg
        if max_ratio is None:
            max_ratio = 1.2
        min_ratio = 1 - max_ratio
    elif plottype == "significances":
        ratio = _significance(data, data_errs, bkg, bkg_errs)
        if max_ratio is None:
            max_ratio = 3
        min_ratio = -max_ratio
    else:
        raise TypeError("Invalid plottype")
    # Increase limits by 30% to avoid tick labels clashing
    max_ratio *= 1.3
    min_ratio *= 1.3

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
    # set out of range to NaN so it doesn't get drawn
    ratio[~_np.isnan(out_of_range_up)] = _np.NaN
    ratio[~_np.isnan(out_of_range_down)] = _np.NaN
    if plottype == "significances":
        ratio_ax.plot(bin_centers, ratio, fmt="ko", ms=3)
    else:
        ratio_ax.errorbar(bin_centers, ratio, yerr=(data_errs / bkg), fmt="ko", ms=3)
    # re-enable errors
    _np.seterr(**olderr)


def draw_tag(text, ax=None):
    if ax is None:
        ax = _mpl.pyplot.gca()
    ax.text(
        1, 1.0005, text, ha="right", va="bottom", fontsize=8, transform=ax.transAxes
    )
