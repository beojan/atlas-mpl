"""UHI protocol validation and kind checking helpers."""

from __future__ import annotations

from typing import Any
import uhi.typing.plottable as _uhi_plottable
import atlas_mpl_style.plot as _amplplt


import inspect
import numpy as _np


class UnsupportedKindError(ValueError):
    """Error due to unsupported histogram kind (e.g., profile histogram)."""

    def __init__(self, msg: str):
        super().__init__(msg)


ProfileHistogramError = UnsupportedKindError


class FlowNotSupportedError(TypeError):
    """Error raised when flow bins are requested but not supported by the histogram."""

    def __init__(self, msg: str):
        super().__init__(msg)


def validate_plottable_histogram(
    hist: Any,
    name: str = "hist",
    ndim: int | None = 1,
    check_kind: bool = True,
    func_name: str | None = None,
    dim_msg: str | None = None,
) -> None:
    """Validate that `hist` satisfies the PlottableHistogram protocol version 1.2,

    has the expected dimensionality, and has kind='COUNT' if required.

    Parameters
    ----------
    hist : object
        The object to validate.
    name : str
        The argument name (e.g., 'hist', 'data', 'syst_errs').
    ndim : int or None
        Expected number of dimensions, or None if dimensionality is not checked.
    check_kind : bool
        If True, requires hist.kind to be 'COUNT' and rejects profile histograms.
    func_name : str, optional
        Calling function/class name for descriptive error messages.
    dim_msg : str, optional
        Custom error message for dimension mismatch.
    """
    if not isinstance(hist, _uhi_plottable.PlottableHistogram):
        raise _amplplt.ViolatesPlottableHistogramError(
            f"{name} violates PlottableHistogram protocol"
        )

    if check_kind:
        kind = getattr(hist.kind, "value", None)
        if not isinstance(kind, str):
            kind = getattr(hist.kind, "name", None)
        if not isinstance(kind, str):
            kind = str(hist.kind)
        kind_str = kind.upper()
        if kind_str != "COUNT":
            context = f" for {func_name}" if func_name else ""
            raise UnsupportedKindError(
                f"{name} has kind '{hist.kind}', but kind='COUNT' is required{context}. "
                f"Profile histograms (kind='{hist.kind}') are not appropriate input{context}."
            )

    if ndim is not None and len(hist.axes) != ndim:
        if dim_msg is not None:
            raise _amplplt.DimensionError(dim_msg)
        dim_str = "1D" if ndim == 1 else f"{ndim}D"
        raise _amplplt.DimensionError(f"Only {dim_str} histograms are supported here")


def extract_flow(hist: Any) -> tuple[_np.ndarray, _np.ndarray | None]:
    """Extract values and variances including flow bins, or raise FlowNotSupportedError."""
    values_func = getattr(hist, "values", None)
    if not callable(values_func) or "flow" not in inspect.signature(values_func).parameters:
        raise FlowNotSupportedError("Histogram does not support flow bins")

    try:
        vals = hist.values(flow=True)
    except (ValueError, TypeError) as err:
        raise FlowNotSupportedError(str(err)) from err

    if len(vals) <= len(hist.values()):
        raise FlowNotSupportedError("Histogram axis does not have flow bins")

    vars_func = getattr(hist, "variances", None)
    vars_ = None
    if callable(vars_func):
        if "flow" in inspect.signature(vars_func).parameters:
            vars_ = hist.variances(flow=True)
        else:
            vars_ = hist.variances()

    return vals, vars_



