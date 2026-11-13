"""
Histogram plotting functions that take UHI PlottableHistogram objects.

They match the functions of the same name in :mod:`atlas_mpl_style.plot`, which take bin
edges and arrays. :class:`atlas_mpl_style.plot.Background` accepts a PlottableHistogram
directly, so this module has no ``plot_backgrounds``.
"""

import inspect as _inspect
import warnings as _warn
import matplotlib as _mpl
import numpy as _np
import atlas_mpl_style.plot as _amplplt
import atlas_mpl_style._uhi_validation as _uhi_val

FlowNotSupportedError = _uhi_val.FlowNotSupportedError
UnsupportedKindError = _uhi_val.UnsupportedKindError
from atlas_mpl_style.plot import LabeledBinsError

_bins = _amplplt._bins
_validate_errs = _amplplt._validate_errs


def _with_flow(errs):
    """Replace each PlottableHistogram in ``errs`` with its values, including flow bins."""
    if hasattr(errs, "axes"):
        return _uhi_val.extract_flow(errs)[0]
    if isinstance(errs, (tuple, list)):
        return [_with_flow(part) for part in errs]
    return errs


def _deprecated_sqrt(stat_errs, ignore_variances):
    """Turn the deprecated ``ignore_variances=True`` into ``stat_errs="sqrt"``."""
    if ignore_variances is None:
        return stat_errs
    _warn.warn(
        'ignore_variances is deprecated. Use stat_errs="sqrt" instead.',
        DeprecationWarning,
        stacklevel=3,
    )
    return "sqrt" if ignore_variances and stat_errs is None else stat_errs


def _is_profile(hist):
    """Return True if ``hist`` is a profile (mean) histogram."""
    kind = getattr(hist.kind, "value", None)
    if not isinstance(kind, str):
        kind = getattr(hist.kind, "name", str(hist.kind))
    return kind.upper() == "MEAN"


def _counts(hist, flow):
    """Return the bin counts of ``hist``, including flow bins if ``flow`` is True."""
    if flow and "flow" in _inspect.signature(hist.counts).parameters:
        return _np.asarray(hist.counts(flow=True), dtype=float)
    return _np.asarray(hist.counts(), dtype=float)


def plot_data(hist, *, stat_errs=None, color="k", label="Data", ax=None, ignore_variances=None):
    """
    Plot data from a PlottableHistogram as points with error bars.

    Parameters
    ----------
    hist : PlottableHistogram
        Data histogram.
    stat_errs : array_like, PlottableHistogram, or str, optional
        Statistical uncertainty in each bin, replacing the variances:

        - shape (N,) or one histogram: symmetric uncertainties.
        - shape (2, N) or two histograms: down and up uncertainties, in that order.
        - ``"sqrt"``: the square root of the bin contents.
        - ``"poisson"``, ``"poisson2"``: ROOT's Poisson intervals (see
          :func:`atlas_mpl_style.utils.poisson_errors`).

        A histogram's values are used. If omitted, the square root of the variances, or of
        the bin contents if ``hist`` has no variances.
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
        The statistical uncertainties:

        - shape (N,): symmetric uncertainties.
        - shape (2, N): down and up uncertainties, in that order.
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=1, check_kind=True, func_name="plot_data"
    )
    stat_errs = _deprecated_sqrt(stat_errs, ignore_variances)
    _validate_errs(stat_errs, "stat_errs", "plot_data")
    bins = _bins(hist.axes[0])
    values = hist.values()
    if stat_errs is None:
        variances = hist.variances()
        stat_errs = "sqrt" if variances is None else _np.sqrt(variances)
    return _amplplt.plot_data(bins, values, stat_errs, color, label, ax)


def plot_signal(
    hist,
    label,
    *,
    stat_errs=None,
    syst_errs=None,
    color=None,
    attach_bands=False,
    ax=None,
    ignore_variances=None,
    **kwargs,
):
    """
    Plot a signal from a PlottableHistogram as an unfilled histogram over the backgrounds.

    A fitted signal belongs in the stack as a :class:`atlas_mpl_style.plot.Background`.

    Parameters
    ----------
    hist : PlottableHistogram
        Signal histogram.
    label : str
        Legend label.
    stat_errs : array_like, PlottableHistogram, or str, optional
        Statistical uncertainty in each bin, replacing the variances:

        - shape (N,) or one histogram: symmetric uncertainties.
        - shape (2, N) or two histograms: down and up uncertainties, in that order.
        - ``"sqrt"``: the square root of the bin contents.

        A histogram's values are used. If omitted, the square root of the variances.
    syst_errs : array_like or PlottableHistogram, optional
        Systematic uncertainty in each bin:

        - shape (N,) or one histogram: symmetric uncertainties.
        - shape (2, N) or two histograms: down and up uncertainties, in that order.

        A histogram's values are used.
    color : color-like, optional
        Line and band color (defaults to the next color in the color cycle).
    attach_bands : bool, optional
        Draw the bands behind the signal's line in the legend. Defaults to False.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    **kwargs
        Passed to ``ax.hist``.
    """
    _uhi_val.validate_plottable_histogram(
        hist, name="hist", ndim=1, check_kind=True, func_name="plot_signal"
    )
    stat_errs = _deprecated_sqrt(stat_errs, ignore_variances)
    _validate_errs(stat_errs, "stat_errs", "plot_signal")
    _validate_errs(syst_errs, "syst_errs", "plot_signal")
    bins = _bins(hist.axes[0])
    values = hist.values()
    if stat_errs is None and hist.variances() is not None:
        stat_errs = _np.sqrt(hist.variances())
    _amplplt.plot_signal(
        label,
        bins,
        values,
        stat_errs,
        syst_errs,
        color=color,
        attach_bands=attach_bands,
        ax=ax,
        **kwargs,
    )


def plot_ratio(
    data,
    total_bkg,
    ratio_ax,
    *,
    stat_errs=None,
    max_ratio=None,
    plottype="diff",
    offscale_errs=False,
):
    """
    Draw a ratio plot comparing data from a PlottableHistogram with the total background.

    See :func:`atlas_mpl_style.plot.plot_ratio` for what the panel shows.

    Parameters
    ----------
    data : PlottableHistogram
        Data histogram.
    total_bkg : PlottableHistogram or tuple of (array_like, array_like)
        Total background, as a histogram whose variances give its uncertainty, or as the
        ``(total_hist, total_err)`` pair from :func:`atlas_mpl_style.plot.plot_backgrounds`.
    ratio_ax : matplotlib.axes.Axes
        Ratio panel from :func:`atlas_mpl_style.ratio_axes`.
    stat_errs : array_like, PlottableHistogram, or str, optional
        Statistical uncertainty of the data, replacing the variances, as for
        :func:`plot_data`.
    max_ratio : float, optional
        Top of the y range. See :func:`atlas_mpl_style.plot.plot_ratio`.
    plottype : {"diff", "raw", "significances"}, optional
        What to plot. See :func:`atlas_mpl_style.plot.plot_ratio`. Defaults to ``"diff"``.
    offscale_errs : bool, optional
        Also draw the error bars of points outside the y range. Defaults to False.
    """
    _uhi_val.validate_plottable_histogram(
        data, name="data", ndim=1, check_kind=True, func_name="plot_ratio"
    )
    _validate_errs(stat_errs, "stat_errs", "plot_ratio")
    bins = _bins(data.axes[0])
    values = data.values()
    if isinstance(stat_errs, str):
        data_errs = _amplplt._stat_errs_from_name(stat_errs, values, allow_poisson=True)
    elif stat_errs is not None:
        data_errs = stat_errs
    elif data.variances() is None:
        data_errs = _np.sqrt(values)
    else:
        data_errs = _np.sqrt(data.variances())

    if hasattr(total_bkg, "axes"):
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
    elif isinstance(total_bkg, (tuple, list)) and len(total_bkg) == 2:
        bkg, bkg_errs = total_bkg
    else:
        raise TypeError(
            "total_bkg should be a histogram or the (total_hist, total_err) pair returned by "
            "plot_backgrounds"
        )
    _amplplt.plot_ratio(
        bins,
        values,
        data_errs,
        bkg,
        bkg_errs,
        ratio_ax,
        max_ratio=max_ratio,
        plottype=plottype,
        offscale_errs=offscale_errs,
    )


def plot_1d(
    hist,
    label,
    *,
    stat_errs=None,
    color=None,
    attach_bands=False,
    ax=None,
    flow=False,
    ignore_variances=None,
    stat_err=None,
    **kwargs,
):
    """
    Plot a 1D histogram from a PlottableHistogram as an unfilled line.

    Parameters
    ----------
    hist : PlottableHistogram
        Histogram, or a profile, which is drawn as points with the error on the mean.
    label : str
        Legend label.
    stat_errs : array_like, PlottableHistogram, str, or False, optional
        Statistical uncertainty in each bin, replacing the variances:

        - shape (N,) or one histogram: symmetric uncertainties.
        - shape (2, N) or two histograms: down and up uncertainties, in that order.
        - ``"sqrt"``: the square root of the bin contents.
        - ``"poisson"``, ``"poisson2"``: ROOT's Poisson intervals (see
          :func:`atlas_mpl_style.utils.poisson_errors`).
        - False: no uncertainty.

        A histogram's values are used. If omitted, the square root of the variances.
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
        hist, name="hist", ndim=1, check_kind=False, func_name="plot_1d"
    )
    if ax is None:
        ax = _mpl.pyplot.gca()
    stat_errs = _deprecated_sqrt(stat_errs, ignore_variances)
    if stat_err is not None:
        _warn.warn(
            "stat_err is deprecated. Use stat_errs=False to draw no uncertainty.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not stat_err:
            stat_errs = False
    if stat_errs is not False:
        _validate_errs(stat_errs, "stat_errs", "plot_1d")
    profile = _is_profile(hist)

    bins = _bins(hist.axes[0])
    if flow:
        values, variances = _uhi_val.extract_flow(hist)
        stat_errs = _with_flow(stat_errs)
        base_bins = bins
        bins = _np.concatenate(
            ([bins[0] - (bins[1] - bins[0])], bins, [bins[-1] + (bins[-1] - bins[-2])])
        )
    else:
        values, variances = hist.values(), hist.variances()

    if profile:
        if isinstance(stat_errs, str):
            raise ValueError(f'stat_errs="{stat_errs}" does not apply to a profile histogram')
        if kwargs:
            raise TypeError(
                "plot_1d draws a profile histogram as points and takes no ax.hist arguments"
            )
        counts = _counts(hist, flow)
        if stat_errs is False:
            stat_errs = None
        elif stat_errs is None and variances is not None:
            # boost-histogram, hist, and uproot give the variance of the mean for a profile.
            # It is undefined for bins with one entry or fewer.
            stat_errs = _np.where(counts > 1, _np.sqrt(variances), _np.nan)
        values = _np.where(counts > 0, values, _np.nan)
        if color is None:
            color = ax._get_lines.get_next_color()
        _amplplt.plot_data(bins, values, stat_errs, color=color, label=label, ax=ax)
    else:
        if stat_errs is False:
            stat_errs = None
        elif stat_errs is None and variances is not None:
            stat_errs = _np.sqrt(variances)
        _amplplt.plot_1d(
            label,
            bins,
            values,
            stat_errs,
            color=color,
            attach_bands=attach_bands,
            ax=ax,
            **kwargs,
        )

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
        2D histogram, or a profile.
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
