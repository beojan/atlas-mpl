"""This module contains versions of the histogram plotting functions that take PlottableHistograms

These are in a separate module to preserve backward compatibility since the array versions of these
functions take the array of bins before the histogram.

:class:`atlas_mpl_style.plot.Background` can be constructed using a ``PlottableHistogram`` and therefore
there is no ``atlas_mpl_style.uhi.plot_backgrounds`` function.
"""

import numpy as _np
import atlas_mpl_style.plot as _amplplt


def plot_data(hist, ignore_variances=False, color="k", label="Data", ax=None):
    """
    Plot data from PlottableHistogram

    Parameters
    ----------
    label : str, optional
        Label for legend (default: "Data")
    hist : PlottableHistogram
        Histogram
    ignore_variances : bool
        Ignore variances and substitute ``hist``. Defaults to False.
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
    if (
        not hasattr(hist, "axes")
        or not hasattr(hist, "values")
        or not hasattr(hist, "variances")
    ):
        raise _amplplt.ViolatesPlottableHistogramError(
            "hist violates PlottableHistogram protocol"
        )
    if len(hist.axes) != 1:
        raise _amplplt.DimensionError("Only 1D histograms are supported here")
    hist_obj = hist
    bins = hist.axes[0].edges()
    hist = hist_obj.values()
    if ignore_variances:
        stat_errs = _np.sqrt(hist)
    else:
        stat_errs = (
            none if hist_obj.variances() is None else _np.sqrt(hist_obj.variances())
        )
    return _amplplt.plot_data(bins, hist, stat_errs, color, label, ax)


def plot_signal(
    hist, label, ignore_variances=False, syst_errs=None, color=None, ax=None
):
    """
    Plot signal histogram from PlottableHistogram

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram
    label : str
        Label for legend
    ignore_variances : bool
        Ignore variances and substitute ``hist``. Defaults to False.
    syst_errs : array_like or PlottableHistogram, optional
        Systematic errors
    color : color
        Line color
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    """
    if (
        not hasattr(hist, "axes")
        or not hasattr(hist, "values")
        or not hasattr(hist, "variances")
    ):
        raise _amplplt.ViolatesPlottableHistogramError(
            "hist violates PlottableHistogram protocol"
        )
    if len(hist.axes) != 1:
        raise _amplplt.DimensionError("Only 1D histograms are supported here")
    hist_obj = hist
    bins = hist_obj.axes[0].edges()
    hist = hist_obj.values()
    if ignore_variances:
        stat_errs = _np.sqrt(hist)
    else:
        stat_errs = (
            none if hist_obj.variances() is None else _np.sqrt(hist_obj.variances())
        )
    if syst_errs is not None and hasattr(syst_errs, "axes"):
        if not hasattr(syst_errs, "values") or not hasattr(syst_errs, "variances"):
            raise _amplplt.ViolatesPlottableHistogramError(
                "syst_errs violates PlottableHistogram protocol"
            )
        if len(syst_errs.axes) != 1:
            raise _amplplt.DimensionError("Only 1D histograms are supported here")
        syst_errs_obj = syst_errs
        if len(syst_errs_obj.axes[0]) != len(hist_obj.axes[0]):
            raise _amplplt.BinningMismatchError(
                "Binning mismatch between syst_errs and hist"
            )
        syst_errs = syst_errs_obj.values()
    _amplplt.plot_signal(label, bins, hist, stat_errs, syst_errs, color, ax)


def plot_ratio(data, total_bkg, ratio_ax, max_ratio=None, plottype="diff"):
    """
    Plot ratio plot from PlottableHistogram

    Parameters
    ----------
    data : PlottableHistogram
        Data histogram
    total_bkg : (array_like, array_like)
        Tuple returned from :func:`atlas_mpl_style.plot.plot_backgrounds`
    ratio_ax : mpl.axes.Axes
        Ratio axes (produced using :func:`atlas_mpl_style.ratio_axes()`)
    max_ratio : float, optional
        Maximum ratio (defaults to 0.2 for "diff", 1.2 for "raw", 3 for "significances")
    plottype : {"diff", "raw", "significances"}
        | Type of ratio to plot.
        | "diff" : (data - bkg) / bkg
        | "raw" : data / bkg
        | "significances" : Significances (from `ampl.utils.significance()`)
    """
    if (
        not hasattr(data, "axes")
        or not hasattr(data, "values")
        or not hasattr(data, "variances")
    ):
        raise _amplplt.ViolatesPlottableHistogramError(
            "data violates PlottableHistogram protocol"
        )
    if len(data.axes) != 1:
        raise _amplplt.DimensionError("Only 1D histograms are supported here")
    data_obj = data
    bins = data_obj.axes[0].edges()
    data = data_obj.values()
    if data_obj.variances() is None:
        data_errs = _np.sqrt(data)
    else:
        data_errs = _np.sqrt(data_obj.variances())
    if not isinstance(total_bkg, tuple) or len(total_bkg) != 2:
        raise TypeError(
            "total_bkg should be a two element tuple of arrays, as returned by plot_backgrounds"
        )
    bkg = total_bkg[0]
    bkg_errs = total_bkg[1]
    _amplplt.plot_ratio(
        bins, data, data_errs, bkg, bkg_errs, ratio_ax, max_ratio, plottype
    )


def plot_1d(hist, label, ignore_variances=False, color=None, ax=None, **kwargs):
    """
    Plot single 1D histogram from PlottableHistogram

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram
    label : str
        Label for legend
    ignore_variances : bool
        Ignore variances and substitute ``hist``. Defaults to False.
    color : color, optional
        Line color
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    **kwargs
        Extra parameters passed to ``plt.hist``
    """
    if (
        not hasattr(hist, "axes")
        or not hasattr(hist, "values")
        or not hasattr(hist, "variances")
    ):
        raise _amplplt.ViolatesPlottableHistogramError(
            "hist violates PlottableHistogram protocol"
        )
    if len(hist.axes) != 1:
        raise _amplplt.DimensionError("Only 1D histograms are supported here")
    hist_obj = hist
    bins = hist.axes[0].edges()
    hist = hist_obj.values()
    if ignore_variances:
        stat_errs = _np.sqrt(hist)
    else:
        stat_errs = (
            none if hist_obj.variances() is None else _np.sqrt(hist_obj.variances())
        )
    _amplplt.plot_1d(label, bins, hist, stat_errs, color, ax, **kwargs)


def plot_2d(hist, ax=None, pad=0.005, **kwargs):
    """
    Plot 2D histogram from PlottableHistogram

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram
    ax : mpl.axes.Axes, optional
        Axes to draw on (defaults to current axes)
    pad : float (0. - 1.), optional
        Padding for colorbar (defaults to 0.005)
    **kwargs
        Extra parameters passed to ``pcolormesh``

    Returns
    -------
    mesh : QuadMesh
    cbar : mpl.colorbar.Colorbar
    """
    if (
        not hasattr(hist, "axes")
        or not hasattr(hist, "values")
        or not hasattr(hist, "variances")
    ):
        raise _amplplt.ViolatesPlottableHistogramError(
            "hist violates PlottableHistogram protocol"
        )
    if len(hist.axes) != 2:
        raise _amplplt.DimensionError("Only 2D histograms are supported here")
    xbins = hist.axes[0].edges()
    ybins = hist.axes[1].edges()
    return _amplplt.plot_2d(xbins, ybins, hist, ax, pad, **kwargs)
