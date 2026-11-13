"""
Plot the pulls and impacts of fit parameters.

Create the figure with :func:`make_impact_figure`, then call :func:`plot_pulls`,
:func:`plot_impacts`, and :func:`draw_pull_impact_legend`. They take a table with one row
per parameter, such as a pandas or Polars DataFrame, a PyArrow table, or a dict of arrays.
Use :func:`sorted_impacts` first to put the largest impacts at the top.
"""

import warnings as _warn
from collections.abc import Mapping as _Mapping
import numpy as _np
import matplotlib as _mpl
import matplotlib.pyplot as _plt


class IncorrectAxesError(Exception):
    """Raised when the axes passed to :func:`draw_pull_impact_legend` have no pull or impact plot."""


def _column(data, name):
    """Return column ``name`` of ``data`` as a NumPy array."""
    return _np.asarray(data[name])


def _take_rows(data, order):
    """Return the rows of ``data`` in ``order``, as the same kind of table."""
    if hasattr(data, "iloc"):  # pandas
        return data.iloc[order]
    if isinstance(data, _Mapping):  # dict of columns
        return {key: _np.asarray(col)[order] for key, col in data.items()}
    if hasattr(data, "take"):  # PyArrow
        return data.take(order)
    return data[order]  # Polars


def sorted_impacts(data):
    """
    Return the impacts sorted with the largest post-fit impact first.

    ``data`` is not changed.

    The table needs at least these columns:

    =================== ===========================================================
    name                Parameter name
    impact_postfit_up   Impact on POI from fit with parameter fixed to +1σ (using postfit σ)
    impact_postfit_down Impact on POI from fit with parameter fixed to -1σ (using postfit σ)
    =================== ===========================================================

    Parameters
    ----------
    data : DataFrame
        Impacts, which may share a table with the pulls.

    Returns
    -------
    DataFrame
        A copy of ``data``, of the same type, with its rows sorted.
    """
    size = _np.maximum(
        _np.abs(_column(data, "impact_postfit_up")),
        _np.abs(_column(data, "impact_postfit_down")),
    )
    return _take_rows(data, _np.argsort(-size, kind="stable"))


def sort_impacts(data):
    """
    Sort impacts in place, largest post-fit impact first.

    .. deprecated:: 0.28.0
       Use :func:`sorted_impacts`, which returns a sorted copy. Sorting in place works only
       for pandas DataFrames, and pandas is deprecating it.

    This adds a ``max_impact`` column, the larger of the two post-fit impacts in absolute value.

    The frame needs at least these columns:

    =================== ===========================================================
    name                Parameter name
    impact_postfit_up   Impact on POI from fit with parameter fixed to +1σ (using postfit σ)
    impact_postfit_down Impact on POI from fit with parameter fixed to -1σ (using postfit σ)
    =================== ===========================================================

    Parameters
    ----------
    data : pandas.DataFrame
        Impacts, which may share a frame with the pulls.
    """
    _warn.warn(
        "sort_impacts is deprecated. Use data = sorted_impacts(data), which returns a sorted copy.",
        DeprecationWarning,
        stacklevel=2,
    )
    data["max_impact"] = _np.maximum(
        _np.abs(data["impact_postfit_up"]), _np.abs(data["impact_postfit_down"])
    )
    data.sort_values(by="max_impact", ascending=False, inplace=True)


def make_impact_figure(num_parameters):
    """
    Create a figure for a pull/impact plot.

    Call :func:`plot_pulls` and :func:`plot_impacts` without ``ax`` next to draw on it.

    Parameters
    ----------
    num_parameters : int
        Number of parameters to show, which is the number of rows in the table.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig = _plt.figure(figsize=(10, 6))
    _plt.ylim(num_parameters + 0.1, -2 - (num_parameters // 5))
    return fig


def plot_pulls(data, ax=None, **kwargs):
    """
    Plot pulls as points with horizontal error bars, one row per parameter.

    The x range is fixed to -2 to 2, with dashed lines at 0 and ±1.

    The table needs at least these columns:

    =========== ===================================================
    name        Parameter name
    value       Post-fit value of the parameter
    err_high    Post-fit uncertainty above the value
    err_low     Post-fit uncertainty below the value (either sign)
    =========== ===================================================

    Parameters
    ----------
    data : DataFrame
        Pulls.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on (defaults to current axes).
    **kwargs
        Passed to ``ax.errorbar``.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes the pulls were drawn on.
    pulls : matplotlib.container.ErrorbarContainer
    """
    if ax is None:
        ax = _plt.gca()
    xerr = _np.abs(_np.stack([_column(data, "err_low"), _column(data, "err_high")]))
    pulls = ax.errorbar(
        y=_column(data, "name"),
        x=_column(data, "value"),
        xerr=xerr,
        fmt=".k",
        capsize=8,
        ms=10,
        zorder=4,
        **kwargs,
    )
    ax.axvline(x=0, lw=2, ls="--", c="paper:fg", alpha=0.5)
    ax.axvline(x=-1, lw=2, ls="--", c="paper:fg", alpha=0.2)
    ax.axvline(x=1, lw=2, ls="--", c="paper:fg", alpha=0.2)
    ax.set_facecolor("transparent")
    ax.set_xlabel(r"$\hat{\theta}$")
    ax.set_xlim(-2, 2)

    # Save some information to help draw legend later
    ax._has_pulls = pulls
    return (ax, pulls)


def plot_impacts(
    data, draw_prefit=False, up_color="paper:blue", down_color="paper:red", ax=None
):
    """
    Plot impacts as horizontal bars on a second x axis above a pull plot.

    Post-fit impacts are filled bars at 50% opacity, and pre-fit impacts are outlined bars.

    The table needs these columns. The pre-fit columns are needed only with ``draw_prefit``.

    =================== ===========================================================
    name                Parameter name
    impact_prefit_up    Impact on POI from fit with parameter fixed to +1σ (using prefit σ)
    impact_prefit_down  Impact on POI from fit with parameter fixed to -1σ (using prefit σ)
    impact_postfit_up   Impact on POI from fit with parameter fixed to +1σ (using postfit σ)
    impact_postfit_down Impact on POI from fit with parameter fixed to -1σ (using postfit σ)
    =================== ===========================================================

    Parameters
    ----------
    data : DataFrame
        Impacts.
    draw_prefit : bool, optional
        Also draw the pre-fit impacts. Defaults to False.
    up_color, down_color : color-like, optional
        Colors of the impacts from the +1σ and -1σ fits.
    ax : matplotlib.axes.Axes, optional
        Axes of the pull plot (defaults to current axes).

    Returns
    -------
    matplotlib.axes.Axes
        The new axes holding the impacts.
    """
    if ax is None:
        ax = _plt.gca()
    impact_axes = _plt.twiny(ax)

    # Save some information to help draw legend later
    ax._impact_axes = impact_axes
    impact_axes._up_color = up_color
    impact_axes._down_color = down_color
    impact_axes._has_prefit = draw_prefit

    if draw_prefit:
        impact_limits = (
            _np.maximum(
                _np.maximum(
                    _np.max(_np.abs(_column(data, "impact_postfit_up"))),
                    _np.max(_np.abs(_column(data, "impact_postfit_down"))),
                ),
                _np.maximum(
                    _np.max(_np.abs(_column(data, "impact_prefit_up"))),
                    _np.max(_np.abs(_column(data, "impact_prefit_down"))),
                ),
            )
            * 1.05
        )
    else:
        impact_limits = (
            _np.maximum(
                _np.max(_np.abs(_column(data, "impact_postfit_up"))),
                _np.max(_np.abs(_column(data, "impact_postfit_down"))),
            )
            * 1.05
        )
    dn_impacts_postfit = impact_axes.barh(
        _column(data, "name"),
        height=0.5,
        width=_column(data, "impact_postfit_down"),
        color=down_color,
        zorder=1,
        alpha=0.5,
    )
    impact_axes._dn_impacts_post = dn_impacts_postfit
    up_impacts_postfit = impact_axes.barh(
        _column(data, "name"),
        height=0.5,
        width=_column(data, "impact_postfit_up"),
        color=up_color,
        zorder=1,
        alpha=0.5,
    )
    impact_axes._up_impacts_post = up_impacts_postfit
    if draw_prefit:
        dn_impacts_prefit = impact_axes.barh(
            _column(data, "name"),
            height=0.5,
            width=_column(data, "impact_prefit_down"),
            edgecolor=down_color,
            color="transparent",
            zorder=1,
        )
        impact_axes._dn_impacts_pre = dn_impacts_prefit
        up_impacts_prefit = impact_axes.barh(
            _column(data, "name"),
            height=0.5,
            width=_column(data, "impact_prefit_up"),
            edgecolor=up_color,
            color="transparent",
            zorder=1,
        )
        impact_axes._up_impacts_pre = up_impacts_prefit
    impact_axes.set_xlim(-impact_limits, impact_limits)
    impact_axes.set_xlabel(r"$\hat{\mu} - \mu_{var}$")
    # In case draw_pull_impact_legend gets the impact axes
    impact_axes._pull_axes = ax
    ax.set_zorder(impact_axes.get_zorder() + 1)
    return impact_axes


def draw_pull_impact_legend(*, ax=None, **kwargs):
    """
    Draw the legend for a pull/impact plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes, optional
        Axes of the pull plot or the impact plot (defaults to current axes).
    **kwargs
        Passed to ``ax.legend``.

    Raises
    ------
    IncorrectAxesError
        If ``ax`` has no pull or impact plot.
    """
    if ax is None:
        ax = _plt.gca()
    if not hasattr(ax, "_has_pulls") and not hasattr(ax, "_impact_axes"):
        if hasattr(ax, "_pull_axes"):
            ax = ax._pull_axes
        else:
            raise IncorrectAxesError(
                "The axes passed to draw_pull_impact_legend do not contain a pull or impact plot."
            )
    kwargs.setdefault("loc", "upper left")
    # 14 pt in the ATLAS style, scaled with font.size.
    kwargs.setdefault("fontsize", _mpl.rcParams["font.size"] * 14 / 18)
    kwargs.setdefault("frameon", False)
    kwargs.setdefault("handlelength", 3.0)
    if hasattr(ax, "_impact_axes"):
        impact_axes = ax._impact_axes
        if impact_axes._has_prefit:
            if hasattr(ax, "_has_pulls"):
                artist_tuple = (
                    ax._has_pulls,
                    impact_axes._up_impacts_pre,
                    impact_axes._dn_impacts_pre,
                    _mpl.lines.Line2D([0], [0], color="w"),
                    impact_axes._up_impacts_post,
                    impact_axes._dn_impacts_post,
                )
                labels = [
                    "Pulls",
                    "Prefit Up",
                    "Prefit Down",
                    "",
                    "Postfit Up",
                    "Postfit Down",
                ]
            else:
                artist_tuple = (
                    impact_axes._up_impacts_pre,
                    impact_axes._dn_impacts_pre,
                    impact_axes._up_impacts_post,
                    impact_axes._dn_impacts_post,
                )
                labels = ["Prefit Up", "Prefit Down", "Postfit Up", "Postfit Down"]
        else:
            if hasattr(ax, "_has_pulls"):
                artist_tuple = (
                    ax._has_pulls,
                    _mpl.lines.Line2D([0], [0], color="w"),
                    impact_axes._up_impacts_post,
                    impact_axes._dn_impacts_post,
                )
                labels = ["Pulls", "", "Postfit Up", "Postfit Down"]
            else:
                artist_tuple = (
                    impact_axes._up_impacts_post,
                    impact_axes._dn_impacts_post,
                )
                labels = ["Postfit Up", "Postfit Down"]
        kwargs.setdefault("facecolor", "white")
        kwargs.setdefault("ncols", 2)
        kwargs.setdefault(
            "handler_map",
            {
                _mpl.container.ErrorbarContainer: _mpl.legend_handler.HandlerErrorbar(
                    xerr_size=1.0
                )
            },
        )
        impact_axes.legend(artist_tuple, labels, **kwargs)
    else:
        kwargs.setdefault("facecolor", "transparent")
        ax.legend([ax._has_pulls], ["Pulls"], **kwargs)
