import matplotlib as _mpl
import matplotlib.colors as _colors
import numpy as _np
from atlas_mpl_style.utils import significance as _significance
from math import floor, ceil

_atlas_label = "ATLAS"

# For histograms with no color set
_hist_colors = _mpl.rcParams["axes.prop_cycle"]()


class BinningMismatchError(Exception):
    "Error due to histogram binning mismatch"

    def __init__(self, msg):
        "Histogram binning mismatch error"
        super().__init__(self, msg)


class Background:
    """Histogram and errors corresponding to a single background"""

    __slots__ = ["label", "hist", "stat_errs", "syst_errs", "color"]

    def __init__(self, label, hist, stat_errs=None, syst_errs=None, color=None):
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
        if syst_errs is not None:
            if len(hist) != len(syst_errs):
                raise BinningMismatchError("Syst errors have incorrect binning")

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
        Total background histogram
    total_err : array_like
        Total error on background histogram
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
    if _np.sum(total_syst_err) != 0.0:
        plot_band(
            bins,
            total_hist - total_err,
            total_hist + total_err,
            color="grey",
            alpha=0.5,
            label="Stat. $\\bigoplus$ Syst. Unc.",
            zorder=5,
        )
    if _np.sum(total_stat_err) != 0:
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


def plot_signal(label, bins, hist, stat_errs=None, syst_errs=None, color=None, ax=None):
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
        ax.plot(
            bin_centers, hist, "o", label=label, color=color, zorder=7, ms=5,
        )
    else:
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
        Maximum ratio (defaults to 0.2 for "diff", 1.2 for "raw", 3 for "significances")
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


def plot_1d(label, bins, hist, stat_errs=None, color=None, ax=None, **kwargs):
    """
    Plot single 1D histogram

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
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    **kwargs
        Extra parameters passed to `plt.hist`
    """
    if ax is None:
        ax = _mpl.pyplot.gca()
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
    if stat_errs is not None:
        plot_band(
            bins, hist - stat_errs, hist + stat_errs, color=color, alpha=0.3, zorder=5
        )


def plot_2d(xbins, ybins, hist, ax=None, pad=0.005, **kwargs):
    """
    Plot 2D histogram

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
    pad : float (0. - 1.), optional
        Padding for colorbar (defaults to 0.005)
    **kwargs
        Extra parameters passed to `pcolormesh`

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
    X, Y = _np.meshgrid(xbins, ybins)
    mesh = ax.pcolormesh(X, Y, hist.transpose(), rasterized=True, **kwargs)
    ax.axis("scaled")
    ax.set_xlim(xbins[0], xbins[-1])
    ax.set_ylim(ybins[0], ybins[-1])
    cbar = ax.figure.colorbar(mesh, ax=ax, pad=pad)
    return mesh, cbar


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

    if minus_two_sigma is not None:
        ax.fill_between(
            x,
            minus_two_sigma,
            plus_two_sigma,
            color=("atlas:twosigma" if color is None else _colors.to_rgba(color, 0.25)),
            label=r"$2\sigma$ Band",
        )
    if minus_one_sigma is not None:
        ax.fill_between(
            x,
            minus_one_sigma,
            plus_one_sigma,
            color=("atlas:onesigma" if color is None else _colors.to_rgba(color, 0.5)),
            label=r"$1\sigma$ Band",
        )
    ax.plot(
        x,
        expected,
        "--",
        label=expected_label,
        color=("black" if color is None else color),
    )
    if observed is not None:
        ax.plot(
            x,
            observed,
            "-",
            label=observed_label,
            color=("black" if color is None else color),
        )


def set_xlabel(label, ax=None, *args, **kwargs):
    """
    Set x label in ATLAS style (right aligned).

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
    ax.set_xlabel(label, x=1.0, ha="right", *args, **kwargs)


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


def set_zlabel(label, cbar, *args, **kwargs):
    """
    Set z label in ATLAS style (top aligned)

    The colorbar to add the label to is *required*

    Parameters
    ----------
    label : str
        Label (LaTeX permitted)
    cbar : mpl.colorbar.Colorbar
        Colorbar to set label on
    """
    cbar.set_label(label, y=1.0, ha="right", *args, **kwargs)


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
        x position
    y : float
        y position
    ax : mpl.axes.Axes, optional
        Axes to draw label in
    status : [ *'int'* | 'wip' | 'prelim' | 'final' | 'opendata' ], optional
        Approval status
    simulation : bool (optional, default ``False``)
        Does the plot show only MC simulation results
    energy : str, optional
        Centre of mass energy, including units
    lumi : float, optional
        Integrated luminosity in /fb
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
        lumi_str = (
            fr', ${"< " if lumi_lt else ""}{lumi:.4g} \ ' fr"\textsf{{fb}}^{{-1}}$"
        )
    else:
        lumi_str = ""

    desc_line = desc is not None
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
        ha="left",
        va="top",
        multialignment="left",
        transform=ax.transAxes,
        size=14,
        *args,
        **kwargs,
    )
