import matplotlib as _mpl
import matplotlib.style as _style
import importlib_resources as _ilr
import packaging as _pkging
from contextlib import ExitStack
import atexit as _atexit
import shutil as _shutil
import warnings as _warn
import cycler as _cycler
import atlas_mpl_style._utils as _u
import atlas_mpl_style.plot as plot
import atlas_mpl_style.stats as stats
import atlas_mpl_style.utils as utils
import atlas_mpl_style.uhi as uhi
from atlas_mpl_style.plot import (
    set_xlabel,
    set_ylabel,
    set_zlabel,
    draw_atlas_label,
    draw_legend,
    draw_tag,
)

_stylesheets_ref = _ilr.files(__name__) / "stylesheets"
_stylesheets_mgr = ExitStack()
_atexit.register(_stylesheets_mgr.close)
_stylesheets = _stylesheets_mgr.enter_context(_ilr.as_file(_stylesheets_ref))
_style.core.USER_LIBRARY_PATHS.append(_stylesheets)
_style.core.reload_library()

_EXTRA_COLORS = {
    "petroff:blue": "#3f90da",
    "petroff:orange": "#ffa90e",
    "petroff:red": "#bd1f01",
    "petroff:gray": "#94a4a2",
    "petroff:purple": "#832db6",
    "petroff:brown": "#a96b59",
    "petroff:orange2": "#e76300",
    "petroff:tan": "#b9ac70",
    "petroff:gray2": "#717581",
    "petroff:lightBlue": "#92dadd",
    "paper:bg": "#eeeeee",
    "paper:fg": "#444444",
    "paper:bgAlt": "#e4e4e4",
    "paper:red": "#af0000",
    "paper:green": "#008700",
    "paper:blue": "#005f87",
    "paper:yellow": "#afaf00",
    "paper:orange": "#d75f00",
    "paper:pink": "#d70087",
    "paper:purple": "#8700af",
    "paper:lightBlue": "#0087af",
    "paper:olive": "#5f7800",
    "on:bg": "#1b2b34",
    "on:fg": "#cdd3de",
    "on:bgAlt": "#343d46",
    "on:fgAlt": "#d8dee9",
    "on:red": "#ec5f67",
    "on:orange": "#f99157",
    "on:yellow": "#fac863",
    "on:green": "#99c794",
    "on:cyan": "#5fb3b3",
    "on:blue": "#6699cc",
    "on:pink": "#c594c5",
    "on:brown": "#ab7967",
    "series:cyan": "#54c9d1",
    "series:orange": "#eca89a",
    "series:blue": "#95bced",
    "series:olive": "#ceb776",
    "series:purple": "#d3a9ea",
    "series:green": "#9bc57f",
    "series:pink": "#f0a1ca",
    "series:turquoise": "#5fcbaa",
    "atlas:onesigma": "#00ff26",
    "atlas:twosigma": "#fbff1f",
    "series2:green": "#00ff26",
    "series2:yellow": "#fbff1f",
    "series2:blue": "#00a1e0",
    "series2:red": "#a30013",
    "series2:purple": "#5100c2",
    "hdbs:starcommandblue": "#047cbc",
    "hdbs:spacecadet": "#283044",
    "hdbs:mintcream": "#ebf5ee",
    "hdbs:outrageousorange": "#fa7e61",
    "hdbs:pictorialcarmine": "#ca1551",
    "hdbs:maroonX11": "#b8336a",
    "hh:darkpink": "#f2385a",
    "hh:darkblue": "#343844",
    "hh:medturquoise": "#36b1bf",
    "hh:lightturquoise": "#4ad9d9",
    "hh:offwhite": "#e9f1df",
    "hh:darkyellow": "#fdc536",
    "hh:darkgreen": "#125125",
    "transparent": "#ffffff00",
}

_mpl.colors.EXTRA_COLORS = _EXTRA_COLORS
_mpl.colors.colorConverter.colors.update(_EXTRA_COLORS)
if _pkging.version.parse(_mpl.__version__) >= _pkging.version.parse("3.6"):
    _mpl.colormaps.register(
        name="bird",
        cmap=_mpl.colors.LinearSegmentedColormap.from_list(
            "bird",
            [
                (0.0592, 0.3599, 0.8684),
                (0.078, 0.5041, 0.8385),
                (0.0232, 0.6419, 0.7914),
                (0.1802, 0.7178, 0.6425),
                (0.5301, 0.7492, 0.4662),
                (0.8186, 0.7328, 0.3499),
                (0.9956, 0.7862, 0.1968),
                (0.9764, 0.9832, 0.0539),
            ],
            N=2560,
        ),
    )
else:
    _mpl.cm.register_cmap(
        name="bird",
        cmap=_mpl.colors.LinearSegmentedColormap.from_list(
            "bird",
            [
                (0.0592, 0.3599, 0.8684),
                (0.078, 0.5041, 0.8385),
                (0.0232, 0.6419, 0.7914),
                (0.1802, 0.7178, 0.6425),
                (0.5301, 0.7492, 0.4662),
                (0.8186, 0.7328, 0.3499),
                (0.9956, 0.7862, 0.1968),
                (0.9764, 0.9832, 0.0539),
            ],
            N=2560,
        ),
    )


def set_color_cycle(pal=None, n=10):
    """
    Sets a different color cycle.

    Parameters
    ----------
    pal : {'ATLAS', 'Paper', 'Oceanic', 'MPL', "HDBS", "HH", None}
      The palette to use. None resets to default palette (Petroff 6, 8, or 10 depending on n).
      'MPL' (alias 'Tab') provides the default matplotlib palette.
    n : int, optional
      Number of lines or histograms.
    """
    if n < 2:
        n = 2
    if pal.upper() == "ATLAS" or pal.upper().startswith("PETROFF") or pal is None:
        if n <= 6:
            colors = [
                (87/255, 144/255, 252/255),
                (248/255, 156/255, 32/255),
                (228/255, 37/255, 54/255),
                (150/255, 74/255, 139/255),
                (156/255, 156/255, 161/255),
                (122/255, 33/255, 221/255)
            ]
        elif n <= 8:
            colors = [
                (24/255, 69/255, 251/255),
                (255/255, 94/255, 2/255),
                (201/255, 31/255, 22/255),
                (200/255, 73/255, 169/255),
                (173/255, 173/255, 125/255),
                (134/255, 200/255, 221/255),
                (87/255, 141/255, 255/255),
                (101/255, 99/255, 100/255)
            ]
        else:
            colors = [
                "petroff:blue",
                "petroff:orange",
                "petroff:red",
                "petroff:gray",
                "petroff:purple",
                "petroff:brown",
                "petroff:orange2",
                "petroff:tan",
                "petroff:gray2",
                "petroff:lightBlue"
            ]

    elif pal.lower() == "paper":
        colors = [
            "paper:green",
            "paper:red",
            "paper:blue",
            "paper:orange",
            "paper:purple",
            "paper:yellow",
            "paper:lightBlue",
            "paper:olive",
        ]
    elif pal.lower() == "oceanic":
        colors = [
            "on:green",
            "on:red",
            "on:blue",
            "on:cyan",
            "on:orange",
            "on:pink",
            "on:yellow",
        ]
    elif pal.lower() == "tab" or pal.lower() == "tableau" or pal.lower() == "mpl":
        colors = [
            "tab:blue",
            "tab:orange",
            "tab:green",
            "tab:red",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]
    elif pal.lower() == "hdbs":
        colors = [
            "hdbs:starcommandblue",
            "hdbs:spacecadet",
            "hdbs:maroonX11",
            "hdbs:outrageousorange",
            "hdbs:pictorialcarmine",
        ]
    elif pal.lower() == "hh":
        colors = ["hh:darkblue", "hh:darkpink", "hh:darkyellow", "hh:medturquoise"]
    else:
        colors = [
            "series:cyan",
            "series:orange",
            "series:blue",
            "series:olive",
            "series:purple",
            "series:green",
            "series:pink",
        ]

    _mpl.rcParams["axes.prop_cycle"] = _cycler.cycler(color=colors)
    plot._hist_colors = _mpl.rcParams["axes.prop_cycle"]()


def use_atlas_style(atlasLabel="ATLAS", fancyLegend=False, usetex=False):
    """
    Setup ATLAS style.

    Parameters
    ----------
    atlasLabel : str, optional
       Replace ATLAS with a custom label
    fancyLegend : bool, optional
       Use matplotlib's fancy legend frame (defaults to False)
    usetex : bool, optional
       Use LaTeX installation to set text (defaults to False)
       If no LaTeX installation is found, this package will fallback to usetex=False.
       This is on a best-effort basis, since the detected LaTeX installation may be incomplete.
    """
    if usetex:
        if (
            _shutil.which("pdflatex") is None
            or _shutil.which("dvipng") is None
            or _shutil.which("gs") is None
        ):
            _warn.warn(
                "No LaTeX installation found -- atlas-mpl-style is falling back to usetex=False"
            )
            usetex = False

    _style.use("atlas")
    set_color_cycle("ATLAS")
    plot._atlas_label = atlasLabel
    _mpl.rcParams["xtick.minor.visible"] = True
    _mpl.rcParams["ytick.minor.visible"] = True
    if not usetex:
        _mpl.rcParams["text.usetex"] = False
        _mpl.rcParams["mathtext.default"] = "regular"
    else:
        plot._usetex = True
        _mpl.rcParams["text.latex.preamble"] = "\n".join(
            [
                r"\usepackage[LGR,T1]{fontenc}",
                r"\usepackage{tgheros}",
                r"\renewcommand{\familydefault}{\sfdefault}",
                r"\usepackage{amsmath}",
                r"\usepackage[symbolgreek,symbolmax]{mathastext}",
                r"\usepackage{physics}",
                r"\usepackage{siunitx}",
                r"\setlength{\parindent}{0pt}",
                r"\def\mathdefault{}",
            ]
        )
    if not fancyLegend:
        _mpl.rcParams["legend.frameon"] = False
        _mpl.rcParams["legend.fancybox"] = False
        _mpl.rcParams["legend.framealpha"] = 0.75


def ratio_axes(extra_axes=None):
    """
    Splits axes for ratio plots.

    Parameters
    -----------
    extra_axes : int, optional
       Number of additional axes. If not given, defaults to one.

    Returns
    -------
    fig : figure
    main_ax : axes
    ratio_ax : axes or list of axes
       Returns list if extra_axes is passed
    """
    hgt = 6 + 2 * (1 if extra_axes is None else extra_axes)  # * (100/72)
    fig = _mpl.pyplot.figure(figsize=(hgt, hgt))
    if extra_axes is None:
        gs = _mpl.gridspec.GridSpec(4, 1, hspace=0.0, wspace=0.0)
        ax1 = fig.add_subplot(gs[0:3])
        ax1.tick_params(labelbottom=False)
        ax2 = fig.add_subplot(gs[3], sharex=ax1)
        ax2.yaxis.set_major_locator(
            _mpl.ticker.MaxNLocator(
                symmetric=True, prune="both", min_n_ticks=5, nbins=4
            )
        )
        ax2.autoscale(axis="x", tight=True)
        _mpl.pyplot.sca(ax1)
        _u.decorate_axes(ax1)
        _u.decorate_axes(ax2)
        ax1._amplaxesinfo.low_ax = ax2
        ax2._amplaxesinfo.main_ax = ax1
        return fig, ax1, ax2
    else:
        gs = _mpl.gridspec.GridSpec(3 + extra_axes, 1, hspace=0.0, wspace=0.0)
        ax1 = fig.add_subplot(gs[0:3])
        ax1.tick_params(labelbottom=False)
        _u.decorate_axes(ax1)
        axs = []
        for i in range(3, extra_axes + 3):
            ax = fig.add_subplot(gs[i], sharex=ax1)
            _u.decorate_axes(ax)
            ax._amplaxesinfo.main_ax = ax1
            if i != extra_axes + 2:
                ax.tick_params(labelbottom=False)
            else:
                ax1._amplaxesinfo.low_ax = ax
            ax.yaxis.set_major_locator(
                _mpl.ticker.MaxNLocator(
                    symmetric=True, prune="both", min_n_ticks=5, nbins=4
                )
            )
            ax.autoscale(axis="x", tight=True)
            axs.append(ax)
        _mpl.pyplot.sca(ax1)
        return fig, ax1, axs
