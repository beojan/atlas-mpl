"""This module contains versions of the histogram plotting functions that take PlottableHistograms.

These are in a separate module to preserve backward compatibility since the array versions of these
functions take the array of bins before the histogram.

:class:`atlas_mpl_style.plot.Background` can be constructed using a ``PlottableHistogram``, and therefore
no atlas_mpl_style.uhi.plot_backgrounds function is provided.
"""

import matplotlib as _mpl
import numpy as _np
import atlas_mpl_style.plot as _amplplt
import atlas_mpl_style._uhi_validation as _uhi_val

FlowNotSupportedError = _uhi_val.FlowNotSupportedError
from atlas_mpl_style.plot import LabeledBinsError


def _bins(axis):
    a = list(axis)
    if isinstance(a[0], str):
        raise LabeledBinsError("Bins are labeled. Perhaps you may want plot_cutflow.")
    return _np.array([i for (i, _) in a] + [a[-1][1]])


def plot_data(hist, ignore_variances=False, color="k", label="Data", ax=None):
    """
    Plot data from a PlottableHistogram.

    Parameters
    ----------
    hist : PlottableHistogram
        Data histogram.
    ignore_variances : bool, optional
        Ignore stored variances and calculate Poisson errors from bin counts (sqrt(hist)). Defaults to False.
    color : str or color-like, optional
        Point color, defaults to black.
    label : str, optional
        Label for legend (default: "Data").
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes).

    Returns
    -------
    hist : array_like
        Data histogram.
    stat_errs : array_like
        Statistical errors.
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
    Plot a signal histogram from a PlottableHistogram.

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram.
    label : str
        Label for legend.
    ignore_variances : bool, optional
        Ignore stored variances and calculate Poisson errors from bin counts (sqrt(hist)). Defaults to False.
    syst_errs : array_like or PlottableHistogram, optional
        Systematic errors.
    color : str or color-like, optional
        Line color.
    attach_bands : bool, optional
        Attach bands to line in legend. Defaults to False.
    ax : mpl.axes.Axes, optional
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
    Draw a ratio plot from PlottableHistogram objects.

    Parameters
    ----------
    data : PlottableHistogram
        Data histogram.
    total_bkg : PlottableHistogram or tuple of (array_like, array_like)
        Total background as a PlottableHistogram or tuple returned from :func:`atlas_mpl_style.plot.plot_backgrounds`.
    ratio_ax : mpl.axes.Axes
        Ratio axis (produced using :func:`atlas_mpl_style.ratio_axes()`).
    max_ratio : float, optional
        Maximum ratio (defaults to 0.25 for "diff", 1.25 for "raw", 3.5 for "significances").
    plottype : {"diff", "raw", "significances"}
        | Type of ratio to plot.
        | "diff" : (data - bkg) / bkg
        | "raw" : data / bkg
        | "significances" : Significances (using :func:`~atlas_mpl_style.utils.significance`)
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
    Plot a single 1D histogram from a PlottableHistogram.

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram.
    label : str
        Label for legend.
    ignore_variances : bool, optional
        Ignore stored variances and calculate Poisson errors from bin counts (sqrt(hist)). Defaults to False.
    stat_err : bool, optional
        Draw statistical errors. Defaults to True.
    color : str or color-like, optional
        Line color.
    attach_bands : bool, optional
        Attach bands to line in legend. Defaults to False.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    flow : bool, optional
        Include and plot underflow and overflow bins if supported (defaults to False).
    **kwargs
        Extra parameters passed to ``plt.hist``.
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
    Plot a 2D histogram from a PlottableHistogram.

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    pad : float, optional
        Padding for colorbar in inches (defaults to 0.05).
    **kwargs
        Extra parameters passed to ``pcolormesh``.

    Returns
    -------
    mesh : QuadMesh
    cbar : mpl.colorbar.Colorbar
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
    Plot a cutflow from a PlottableHistogram.

    Parameters
    ----------
    hist : PlottableHistogram
        Cutflow histogram.
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    text : bool, optional
        Whether to label bars (default: True).
    textcolor : str, optional
        Text color.
    horizontal : bool, optional
        Whether to draw horizontal bars (default: True).
    **kwargs
        Extra parameters passed to ``bar`` or ``barh``
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
