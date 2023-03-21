import numpy as _np
import matplotlib as _mpl
import matplotlib.pyplot as _plt


class IncorrectAxesError(Exception):
    "Error due to passing incorrect axes to draw_pull_impact_legend"

    def __init__(self, msg):
        "Axes do not contain pull or impact plots"
        super().__init__(self, msg)


def sort_impacts(data):
    """
    Sort an impact (and pull) dataframe in-place by descending postfit impacts.

    The frame must have at least the following columns:

    =================== ==========================
    name                Parameter name
    impact_postfit_up   Impact on POI from fit with parameter fixed to +1σ (using postfit σ)
    impact_postfit_down Impact on POI from fit with parameter fixed to -1σ (using postfit σ)
    =================== ==========================

    Parameters
    -----------
    data : pd.DataFrame
        Pandas dataframe containing impacts
    """
    data["max_impact"] = _np.maximum(
        _np.abs(data["impact_postfit_up"]), _np.abs(data["impact_postfit_down"])
    )
    data.sort_values(by="max_impact", ascending=False, inplace=True)


def make_impact_figure(num_parameters):
    """
    Create a new figure for a pull / impact plot.

    Parameters
    ----------
    num_parameters : Integer
        Number of parameters on this plot

    Returns
    -------
    fig : Figure
        Created figure
    """
    fig = _plt.figure(figsize=(10, 6))
    _plt.ylim(num_parameters + 0.1, -2 - (num_parameters // 5))
    return fig


def plot_pulls(data, ax=None, **kwargs):
    """
    Plot pulls from a Pandas dataframe (``data``).

    The dataframe must have at least the following columns:

    =================== ==========================
    name                Parameter name
    value               Post nominal fit central value of parameter
    err_high            Post nominal fit error (high side) on parameter
    err_low             Post nominal fit error (low side) on parameter.
    =================== ==========================

    Parameters
    -----------
    data : pd.DataFrame
        Pandas dataframe containing pulls
    ax : mpl.axes.Axes, optional
        Axes to draw pulls on (defaults to current axes)
    **kwargs
        Keyword arguments passed to ``errorbar``

    Returns
    -------
    ax : mpl.axes.Axes
       The axes pulls were drawn on
    pull_plot : mpl.container.ErrorbarContainer
       The return value of ``errorbar``
    """
    if ax is None:
        ax = _plt.gca()
    xerr = _np.abs(_np.array(data[["err_low", "err_high"]]))
    pulls = ax.errorbar(
        y=data["name"],
        x=data["value"],
        xerr=xerr.T,
        fmt=".k",
        capsize=8,
        ms=10,
        zorder=4,
        **kwargs
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
    Plot impacts from a Pandas dataframe (``data``).

    The dataframe must have the following columns. The prefit columns are not required if ``draw_prefix == False``.

    =================== ==========================
    name                Parameter name
    impact_prefit_up    Impact on POI from fit with parameter fixed to +1σ (using prefit σ)
    impact_prefit_down  Impact on POI from fit with parameter fixed to -1σ (using prefit σ)
    impact_postfit_up   Impact on POI from fit with parameter fixed to +1σ (using postfit σ)
    impact_postfit_down Impact on POI from fit with parameter fixed to -1σ (using postfit σ)
    =================== ==========================

    Parameters
    -----------
    data : pd.DataFrame
        Pandas dataframe containing impacts
    draw_prefit : Boolean, optional
        Whether to draw the prefit bands
    up_color : Color specification
        Color to use for upper band (postfit band will be at 50% opacity)
    up_color : Color specification
        Color to use for lower band (postfit band will be at 50% opacity)
    ax : mpl.axes.Axes, optional
        Axes to pulls were drawn on (defaults to current axes). Impact axes will be a twin of these.

    Returns
    -------
    ax : mpl.axes.Axes
       The axes impacts were drawn on
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
                    _np.max(_np.abs(data["impact_postfit_up"])),
                    _np.max(_np.abs(data["impact_postfit_down"])),
                ),
                _np.maximum(
                    _np.max(_np.abs(data["impact_prefit_up"])),
                    _np.max(_np.abs(data["impact_prefit_down"])),
                ),
            )
            * 1.05
        )
    else:
        impact_limits = (
            _np.maximum(
                _np.max(_np.abs(data["impact_postfit_up"])),
                _np.max(_np.abs(data["impact_postfit_down"])),
            )
            * 1.05
        )
    dn_impacts_postfit = impact_axes.barh(
        data["name"],
        height=0.5,
        width=data["impact_postfit_down"],
        color=down_color,
        zorder=1,
        alpha=0.5,
    )
    impact_axes._dn_impacts_post = dn_impacts_postfit
    up_impacts_postfit = impact_axes.barh(
        data["name"],
        height=0.5,
        width=data["impact_postfit_up"],
        color=up_color,
        zorder=1,
        alpha=0.5,
    )
    impact_axes._up_impacts_post = up_impacts_postfit
    if draw_prefit:
        dn_impacts_prefit = impact_axes.barh(
            data["name"],
            height=0.5,
            width=data["impact_prefit_down"],
            edgecolor=down_color,
            color="transparent",
            zorder=1,
        )
        impact_axes._dn_impacts_pre = dn_impacts_prefit
        up_impacts_prefit = impact_axes.barh(
            data["name"],
            height=0.5,
            width=data["impact_prefit_up"],
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


def draw_pull_impact_legend(*args, ax=None, **kwargs):
    """
    Add legend to a pull / impact plot.

    Parameters
    ----------
    ax : mpl.axes.Axes, optional
        Pull axes
    **kwargs :
       Passed to ``ax.legend``
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
        impact_axes.legend(
            artist_tuple,
            labels,
            loc="upper left",
            fontsize=14,
            facecolor="white",
            frameon=False,
            ncols=2,
            handlelength=3.0,
            handler_map={
                _mpl.container.ErrorbarContainer: _mpl.legend_handler.HandlerErrorbar(
                    xerr_size=1.0
                )
            },
            **kwargs
        )
    else:
        ax.legend(
            (ax._has_pulls),
            ["Pulls"],
            loc="upper left",
            fontsize=14,
            facecolor="transparent",
            frameon=False,
            handlelength=3.0,
        )
