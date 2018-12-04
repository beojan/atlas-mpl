import matplotlib as _mpl
import matplotlib.style as _style
import pkg_resources as _pkg
import atexit as _atexit

_stylesheets = _pkg.resource_filename(__name__, 'stylesheets')
_atexit.register(_pkg.cleanup_resources)
_style.core.USER_LIBRARY_PATHS.append(_stylesheets)
_style.core.reload_library()

_EXTRA_COLORS = {
        'paper:bg': '#eeeeee',
        'paper:fg': '#444444',
        'paper:bgAlt': '#e4e4e4',
        'paper:red': '#af0000',
        'paper:green': '#008700',
        'paper:blue': '#005f87',
        'paper:yellow': '#afaf00',
        'paper:orange': '#d75f00',
        'paper:pink': '#d70087',
        'paper:purple': '#8700af',
        'paper:lightBlue': '#0087af',
        'paper:olive': '#5f7800',
        'on:bg': '#1b2b34',
        'on:fg': '#d8dee9',
        'on:bgAlt': '#343d46',
        'on:fgAlt': '#cdd3de',
        'on:red': '#ec5f67',
        'on:orange': '#f99157',
        'on:yellow': '#fac863',
        'on:green': '#99c794',
        'on:cyan': '#5fb3b3',
        'on:blue': '#6699cc',
        'on:pink': '#c594c5',
        'on:brown': '#ab7967'
}

_atlas_label = "ATLAS"
_mpl.colors.EXTRA_COLORS = _EXTRA_COLORS
_mpl.colors.colorConverter.colors.update(_EXTRA_COLORS)


def use_atlas_style(atlasLabel='ATLAS'):
    "Setup ATLAS style."
    _style.use('atlas')
    _atlas_label = atlasLabel
    _mpl.rcParams['font.size'] = 16
    _mpl.rcParams['text.latex.preamble'] = [r'\usepackage{helvet}',
                                            r'\usepackage{sansmath}',
                                            r'\setlength{\parindent}{0pt}'
                                            r'\sansmath']
    _mpl.pyplot.minorticks_on()


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
    ax.set_xlabel(label, x=1.0, ha='right', *args, **kwargs)


def set_ylabel(label, ax=None, *args, **kwargs):
    """
    Set y label in ATLAS style (right aligned).

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
    ax.set_ylabel(label, y=1.0, ha='right', *args, **kwargs)


def draw_atlas_label(x, y, ax=None, status='int', simulation=False,
                     energy=None, lumi=None, desc=None, lumi_lt=False, 
                     *args, **kwargs):
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
    status : [ *'int'* | 'wip' | 'prelim' | 'final' ], optional
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
    if ax is None:
        ax = _mpl.pyplot.gca()
    sim_str = "Simulation " if simulation else ""

    if status == 'final':
        status_str = ''
    elif status == 'int':
        status_str = 'Internal'
    elif status == 'wip':
        status_str = 'Work in Progress'
    elif status == 'prelim':
        status_str = 'Preliminary'
    else:
        status_str = status

    show_e_nl = False
    if energy is not None:
        show_e_nl = True
        energy_str = rf'$\sqrt{{s}} = $ {energy}'
    else:
        energy_str = ''

    if lumi is not None:
        show_e_nl = True
        lumi_str = (fr', ${"< " if lumi_lt else ""}{lumi:.4g} \ '
                    fr'\textsf{{fb}}^{{-1}}$')
    else:
        lumi_str = ''

    desc_line = desc is not None
    nl = r'\\'
    label = (fr'\textbf{{\textit{{{_atlas_label}}}}} {sim_str}{status_str}'
             fr'{nl if show_e_nl else ""}'
             fr'{energy_str}{lumi_str}{nl if desc_line else ""}'
             fr'{desc if desc_line else ""}')
    ax.text(x, y, label, ha='left', va='top', multialignment='left',
            transform=ax.transAxes, size=14, *args, **kwargs)


def ratio_axes():
    fig = _mpl.pyplot.figure(figsize=(8, 8), dpi=600)
    gs = _mpl.gridspec.GridSpec(4, 1, hspace=0., wspace=0.)
    ax1 = fig.add_subplot(gs[0:3])
    ax1.tick_params(labelbottom=False)
    ax2 = fig.add_subplot(gs[3], sharex=ax1)
    ax2.yaxis.set_major_locator(_mpl.ticker.MaxNLocator(
        symmetric=True, prune='both', min_n_ticks=5, nbins=4))
    ax2.autoscale(axis='x', tight=True)
    return fig, ax1, ax2
