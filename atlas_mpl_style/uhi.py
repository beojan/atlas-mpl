"""
Histogram plotting functions that take UHI PlottableHistogram objects.

They match the functions of the same name in :mod:`atlas_mpl_style.plot`, which take bin
edges and arrays. :class:`atlas_mpl_style.plot.Background` accepts a PlottableHistogram
directly, so this module has no ``plot_backgrounds``.
"""

import matplotlib as _mpl
import numpy as _np
import atlas_mpl_style.plot as _amplplt
import atlas_mpl_style._uhi_validation as _uhi_val

FlowNotSupportedError = _uhi_val.FlowNotSupportedError
UnsupportedKindError = _uhi_val.UnsupportedKindError
from atlas_mpl_style.plot import LabeledBinsError


def _bins(axis):
    a = list(axis)
    if isinstance(a[0], str):
        raise LabeledBinsError("Bins are labeled. Perhaps you may want plot_cutflow.")
    return _np.array([i for (i, _) in a] + [a[-1][1]])


def plot_data(hist, ignore_variances=False, color="k", label="Data", ax=None):
    """
    Plot data from a PlottableHistogram as points with error bars.

    Parameters
    ----------
    hist : PlottableHistogram
        Data histogram. The error bars are the square root of its variances.
    ignore_variances : bool, optional
        Use the square root of the bin contents for the error bars instead. Defaults to False.
    color : color-like, optional
        Point color (defaults to black).
    label : str, optional
        Legend label (defaults to "Data").
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).

    Returns
    -------
    hist : numpy.ndarray
        The bin contents.
    stat_errs : numpy.ndarray
        The statistical uncertainties.
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=1, check_kind=True, func_name="plot_data"
    )
    hist_obj = hist
    bins = _bins(hist.axes[0])
    hist = hist_obj.values()
    if ignore_variances:
        stat_errs = _np.sqrt(hist)
    else:
        stat_errs = (
            None if hist_obj.variances() is None else _np.sqrt(hist_obj.variances())
        )
    return _amplplt.plot_data(bins, hist, stat_errs, color, label, ax)


def plot_signal(
    hist,
    label,
    ignore_variances=False,
    syst_errs=None,
    color=None,
    attach_bands=False,
    ax=None,
):
    """
    Plot a signal from a PlottableHistogram as an unfilled histogram over the backgrounds.

    A fitted signal belongs in the stack as a :class:`atlas_mpl_style.plot.Background`.

    Parameters
    ----------
    hist : PlottableHistogram
        Signal histogram. The hatched band is the square root of its variances.
    label : str
        Legend label.
    ignore_variances : bool, optional
        Use the square root of the bin contents for the band instead. Defaults to False.
    syst_errs : array_like or PlottableHistogram, optional
        Systematic uncertainty in each bin. For a PlottableHistogram, its bin values are used.
    color : color-like, optional
        Line and band color (defaults to the next color in the color cycle).
    attach_bands : bool, optional
        Draw the bands behind the signal's line in the legend. Defaults to False.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=1, check_kind=True, func_name="plot_signal"
    )
    hist_obj = hist
    bins = _bins(hist_obj.axes[0])
    hist = hist_obj.values()
    if ignore_variances:
        stat_errs = _np.sqrt(hist)
    else:
        stat_errs = (
            None if hist_obj.variances() is None else _np.sqrt(hist_obj.variances())
        )
    if syst_errs is not None and hasattr(syst_errs, "axes"):
        _uhi_val.validate_plottable_histogram(
            syst_errs,
            name="syst_errs",
            ndim=1,
            check_kind=True,
            func_name="plot_signal",
        )
        syst_errs_obj = syst_errs
        if len(syst_errs_obj.axes[0]) != len(hist_obj.axes[0]):
            raise _amplplt.BinningMismatchError(
                "Binning mismatch between syst_errs and hist"
            )
        syst_errs = syst_errs_obj.values()
    _amplplt.plot_signal(
        label, bins, hist, stat_errs, syst_errs, color, attach_bands, ax
    )


def plot_ratio(data, total_bkg, ratio_ax, max_ratio=None, plottype="diff"):
    """
    Draw a ratio plot comparing data from a PlottableHistogram with the total background.

    See :func:`atlas_mpl_style.plot.plot_ratio` for what the panel shows.

    Parameters
    ----------
    data : PlottableHistogram
        Data histogram. Its uncertainties are the square root of its variances, or of its bin
        contents if it has no variances.
    total_bkg : PlottableHistogram or tuple of (array_like, array_like)
        Total background, as a histogram whose variances give its uncertainty, or as the
        ``(total_hist, total_err)`` tuple from :func:`atlas_mpl_style.plot.plot_backgrounds`.
    ratio_ax : matplotlib.axes.Axes
        Ratio panel from :func:`atlas_mpl_style.ratio_axes`.
    max_ratio : float, optional
        Top of the y range. See :func:`atlas_mpl_style.plot.plot_ratio`.
    plottype : {"diff", "raw", "significances"}, optional
        What to plot. See :func:`atlas_mpl_style.plot.plot_ratio`. Defaults to ``"diff"``.
    """
    _uhi_val.validate_plottable_histogram(
        data, name="data", ndim=1, check_kind=True, func_name="plot_ratio"
    )
    data_obj = data
    bins = _bins(data_obj.axes[0])
    data = data_obj.values()
    if data_obj.variances() is None:
        data_errs = _np.sqrt(data)
    else:
        data_errs = _np.sqrt(data_obj.variances())

    if hasattr(total_bkg, "axes"):
        # total_bkg is a UHI histogram
        _uhi_val.validate_plottable_histogram(
            total_bkg,
            name="total_bkg",
            ndim=1,
            check_kind=True,
            func_name="plot_ratio",
        )
        bkg = total_bkg.values()
        bkg_errs = (
            _np.zeros_like(bkg)
            if total_bkg.variances() is None
            else _np.sqrt(total_bkg.variances())
        )
    elif isinstance(total_bkg, tuple) and len(total_bkg) == 2:
        bkg = total_bkg[0]
        bkg_errs = total_bkg[1]
    else:
        raise TypeError(
            "total_bkg should be a two element tuple of arrays, as returned by plot_backgrounds"
        )
    _amplplt.plot_ratio(
        bins, data, data_errs, bkg, bkg_errs, ratio_ax, max_ratio, plottype
    )


def plot_1d(
    hist,
    label,
    ignore_variances=False,
    stat_err=True,
    color=None,
    attach_bands=False,
    ax=None,
    flow=False,
    **kwargs,
):
    """
    Plot a 1D histogram from a PlottableHistogram as an unfilled line.

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram. The hatched band is the square root of its variances.
    label : str
        Legend label.
    ignore_variances : bool, optional
        Use the square root of the bin contents for the band instead. Defaults to False.
    stat_err : bool, optional
        Draw the statistical uncertainty as a hatched band. Defaults to True.
    color : color-like, optional
        Line color (defaults to the next color in the color cycle).
    attach_bands : bool, optional
        Draw the band behind the line in the legend. Defaults to False.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    flow : bool, optional
        Draw the underflow and overflow as an extra bin at each end, labelled "<low" and
        ">high". Defaults to False.
    **kwargs
        Passed to ``ax.hist``.

    Raises
    ------
    FlowNotSupportedError
        If ``flow`` is True and ``hist`` has no flow bins.
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=1, check_kind=True, func_name="plot_1d"
    )
    if ax is None:
        ax = _mpl.pyplot.gca()

    bins = _bins(hist.axes[0])
    if flow:
        h_vals, h_vars = _uhi_val.extract_flow(hist)
        base_bins = bins
        bins = _np.concatenate(([bins[0] - (bins[1] - bins[0])], bins, [bins[-1] + (bins[-1] - bins[-2])]))
    else:
        h_vals, h_vars = hist.values(), hist.variances()

    stat_errs = _np.sqrt(h_vals) if (stat_err and ignore_variances) else (_np.sqrt(h_vars) if (stat_err and h_vars is not None) else None)
    _amplplt.plot_1d(label, bins, h_vals, stat_errs, color, attach_bands, ax, **kwargs)

    if flow:
        ax.set_xlim(bins[0], bins[-1])
        ticks = [t for t in ax.get_xticks() if base_bins[0] <= t <= base_bins[-1]]
        fmt = lambda x: f"{int(x) if float(x).is_integer() else x:g}"
        ax.set_xticks(
            [(bins[0] + bins[1]) / 2, *ticks, (bins[-2] + bins[-1]) / 2],
            labels=[f"<{fmt(base_bins[0])}", *[fmt(t) for t in ticks], f">{fmt(base_bins[-1])}"],
        )


def plot_2d(hist, ax=None, pad=0.05, **kwargs):
    """
    Plot a 2D PlottableHistogram as a color map with a colorbar on the right.

    The x and y axes get the same scale, which suits related quantities such as two masses,
    and their limits are set to the bin edges. For unrelated quantities, call
    ``ax.set_aspect("auto")`` afterwards to let the axes fill their usual space.

    Parameters
    ----------
    hist : PlottableHistogram
        2D histogram.
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
        Use :func:`atlas_mpl_style.set_zlabel` to label it.
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=2, check_kind=False, func_name="plot_2d"
    )
    xbins = _bins(hist.axes[0])
    ybins = _bins(hist.axes[1])
    h = hist.values()
    return _amplplt.plot_2d(xbins, ybins, h, ax, pad, **kwargs)


def plot_cutflow(hist, ax=None, text=True, textcolor="w", horizontal=True, **kwargs):
    """
    Plot a cutflow from a PlottableHistogram as a bar chart with the yield on each bar.

    Parameters
    ----------
    hist : PlottableHistogram
        Cutflow histogram with one string-labelled bin per cut, such as one with a
        ``StrCategory`` axis.
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
    _uhi_val.validate_plottable_histogram(
        hist,
        name="hist",
        ndim=1,
        check_kind=True,
        func_name="plot_cutflow",
        dim_msg="Cutflow histogram must be 1D",
    )
    labels = list(hist.axes[0])
    if not isinstance(labels[0], str):
        raise LabeledBinsError(
            "Bins are not labeled. Cutflow requires discrete string-labeled bins (e.g. StrCategory axis)."
        )
    _amplplt.plot_cutflow(
        labels,
        hist.values(),
        ax=ax,
        text=text,
        textcolor=textcolor,
        horizontal=horizontal,
        **kwargs,
    )
