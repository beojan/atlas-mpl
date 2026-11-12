import warnings as _warn
import matplotlib as _mpl

# Sizes a style may give in points rather than relative to font.size.
_SIZE_KEYS = (
    "axes.titlesize",
    "axes.labelsize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
    "figure.titlesize",
    "figure.labelsize",
)

_MATHTEXT_KEYS = {
    "mathtext.rm": "",
    "mathtext.sf": "",
    "mathtext.it": ":italic",
    "mathtext.bf": ":bold",
    "mathtext.bfit": ":italic:bold",
}


def _escape(name):
    """Escape a font name for use in a fontconfig pattern."""
    for char in "\\-:,":
        name = name.replace(char, "\\" + char)
    return name


def set_font(family=None, size=None):
    """
    Change the font and base font size of the current style.

    Call this after ``use_atlas_style()`` or ``plt.style.use()``.

    Parameters
    ----------
    family : str or list of str, optional
        Font, or fonts in order of preference. Ignored with ``usetex=True``.
    size : float, optional
        Base font size in points. Other text sizes scale with it.
    """
    if family is not None:
        if _mpl.rcParams["text.usetex"]:
            _warn.warn("set_font cannot change the font of LaTeX text")
        else:
            families = [family] if isinstance(family, str) else list(family)
            sans = families + [
                f for f in _mpl.rcParams["font.sans-serif"] if f not in families
            ]
            _mpl.rcParams["font.sans-serif"] = sans
            if _mpl.rcParams["mathtext.fontset"] == "custom":
                pattern = ", ".join(_escape(f) for f in sans)
                for key, suffix in _MATHTEXT_KEYS.items():
                    _mpl.rcParams[key] = pattern + suffix

    if size is not None:
        scale = size / _mpl.rcParams["font.size"]
        _mpl.rcParams["font.size"] = size
        for key in _SIZE_KEYS:
            # Named sizes such as "large" already follow font.size.
            if key in _mpl.rcParams and isinstance(_mpl.rcParams[key], (int, float)):
                _mpl.rcParams[key] *= scale
