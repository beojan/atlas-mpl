import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, DefaultDict, List
from collections import defaultdict, OrderedDict
from cycler import cycle
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerTuple

# To make it easier to remove these when drawing legend
stat_label = "Stat. Uncertainty"
syst_label = "Stat. $\\oplus$ Syst. Unc."


@dataclass
class LimitConfig:
    has_obs: bool = False
    has_exp: bool = True
    obs_label: str = ""
    exp_label: str = ""
    color: Any = None
    has_1sig: bool = False
    has_2sig: bool = False


@dataclass
class AMPLLegend:
    "Keep track of legend"
    has_stat: bool = False
    has_syst: bool = False
    fill_hists: Dict[str, Artist] = field(default_factory=dict)
    line_hists: Dict[str, Artist] = field(default_factory=dict)
    bands: DefaultDict[str, List[Artist]] = field(
        default_factory=lambda: defaultdict(list)
    )
    data_hists: Dict[str, Artist] = field(default_factory=dict)
    limits: Dict[str, LimitConfig] = field(default_factory=dict)


@dataclass
class AMPLAxesInfo:
    "Keep track of attached axes"
    main_ax: Axes = None
    low_ax: Axes = None
    cbar: Axes = None


def decorate_axes(ax):
    "Add AMPLLegend and AMPLAxesInfo to an ax if they don't exist"
    if not hasattr(ax, "_ampllegend"):
        ax._ampllegend = AMPLLegend()
    if not hasattr(ax, "_amplaxesinfo"):
        ax._amplaxesinfo = AMPLAxesInfo()


def get_main_ax(ax):
    if not hasattr(ax, "_amplaxesinfo"):
        decorate_axes(ax)
    if ax._amplaxesinfo.main_ax is not None:
        return ax._amplaxesinfo.main_ax
    else:
        return ax


def plot_type(ax):
    "Does ax show histograms or limits."
    if len(ax._ampllegend.limits) != 0:
        return "limits"
    else:
        return "hists"


def get_extras(ax):
    "Get extra items"
    al = ax._ampllegend
    ampl_labels = set().union(
        al.fill_hists.keys(),
        al.line_hists.keys(),
        al.data_hists.keys(),
        [x.obs_label for x in al.limits.values()],
        [x.exp_label for x in al.limits.values()],
        [stat_label, syst_label],
    )
    extras = OrderedDict()
    handles, labels = ax.get_legend_handles_labels()
    for handle, label in zip(handles, labels):
        if label not in ampl_labels:
            extras[label] = handle
    return extras


class BandHandler(HandlerTuple):
    "Legend handler for bands"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        # Adapted from HandlerTuple
        handler_map = legend.get_legend_handler_map()

        if self._ndivide is None:
            ndivide = len(orig_handle)
        else:
            ndivide = self._ndivide

        if self._pad is None:
            pad = legend.borderpad * fontsize
        else:
            pad = self._pad * fontsize

        if ndivide > 1:
            width = (width - pad * (ndivide - 1)) / ndivide

        xds_cycle = cycle(xdescent - (width + pad) * np.arange(ndivide))

        a_list = []
        n_bands = len(orig_handle) - 1
        for i, handle1 in enumerate(orig_handle):
            handler = legend.get_legend_handler(handler_map, handle1)
            _a_list = handler.create_artists(
                legend,
                handle1,
                next(xds_cycle),
                ydescent,
                width,
                height * (1 if i == 0 else i / n_bands),
                fontsize,
                trans,
            )
            a_list.extend(_a_list)

        return list(reversed(a_list))


def draw_hists_legend(ax, args, kwargs):
    "Draw hist-type legend"
    al = ax._ampllegend
    extras = get_extras(ax)
    band_labels = set(al.bands.keys())
    handler_map = {}
    handles = []
    labels = []
    for label, handle in al.data_hists.items():
        handles.append(handle)
        labels.append(label)
    for label, handle in al.fill_hists.items():
        handles.append(handle)
        labels.append(label)
    if al.has_stat:
        labels.append("Stat. Uncertainty")
        handles.append(Rectangle((0, 0), 0, 0, fc="transparent", ec="k", hatch=r"////"))
    if al.has_syst:
        labels.append("Total Uncertainty" if al.has_stat else "Uncertainty")
        handles.append(Rectangle((0, 0), 0, 0, fc="grey", alpha=0.5))
    for label, handle in al.line_hists.items():
        labels.append(label)
        if label not in band_labels:
            handles.append(handle)
        else:
            handle_ = tuple([handle] + al.bands[label])
            handles.append(handle_)
            handler_map[handle_] = BandHandler()

    for label, handle in extras:
        labels.append(label)
        if label not in band_labels:
            handles.append(handle)
        else:
            handle_ = tuple([handle] + al.bands[label])
            handles.append(handle_)
            handler_map[handle_] = BandHandler()
    if handler_map == {}:
        handler_map = None
    ax.legend(handles, labels, handler_map=handler_map, *args, **kwargs)


def draw_limit_legend(ax, args, kwargs):
    "Draw limit-type legend"
    al = ax._ampllegend
    extras = get_extras(ax)
    band_labels = set(al.bands.keys())
    handler_map = {}
    handles = []
    labels = []

    if len(al.limits) == 1:
        # Single limit
        lc = al.limits.values()[0]
        line_c = "k" if lc.color is None else lc.color
        two_sig_c = "atlas:twosigma" if lc.color is None else to_rgba(lc.color, 0.25)
        one_sig_c = "atlas:onesigma" if lc.color is None else to_rgba(lc.color, 0.5)
        if lc.has_obs:
            labels.append(lc.obs_label)
            handles.append(Line2D([0], [0], color=line_c, linestyle="-"))
        if lc.has_exp:
            labels.append(lc.exp_label)
            handles.append(Line2D([0], [0], color=line_c, linestyle="--"))
            labels.append("Expected ±1σ")
            handles.append(Rectangle((0, 0), [0], [0], fc=one_sig_c, ec=None))
            labels.append("Expected ±2σ")
            handles.append(Rectangle((0, 0), [0], [0], fc=two_sig_c, ec=None))
    else:
        for lc in al.limits.values():
            # Multiple limits
            line_c = "k" if lc.color is None else lc.color
            two_sig_c = (
                "atlas:twosigma" if lc.color is None else to_rgba(lc.color, 0.25)
            )
            one_sig_c = "atlas:onesigma" if lc.color is None else to_rgba(lc.color, 0.5)
            if lc.has_obs:
                labels.append(lc.obs_label)
                handles.append(Line2D([0], [0], color=line_c, linestyle="-"))
            if lc.has_exp:
                labels.append(lc.exp_label)
                handle_ = (
                    Line2D([0], [0], color=line_c, linestyle="--"),
                    Rectangle((0, 0), [0], [0], fc=one_sig_c, ec=None),
                    Rectangle((0, 0), [0], [0], fc=two_sig_c, ec=None),
                )
                handles.append(handle_)
                handler_map[handle_] = BandHandler()

    for label, handle in extras:
        labels.append(label)
        if label not in band_labels:
            handles.append(handle)
        else:
            handle_ = tuple([handle] + al.bands[label])
            handles.append(handle_)
            handler_map[handle_] = BandHandler()
    if handler_map == {}:
        handler_map = None
    ax.legend(handles, labels, handler_map=handler_map, *args, **kwargs)
