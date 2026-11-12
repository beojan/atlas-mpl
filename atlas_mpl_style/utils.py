"""Statistical functions used by the plotting functions."""

import numexpr as _ne
import numpy as _np


def significance(data, data_errs, bkg, bkg_errs):
    """
    Calculate the significance of the difference between data and background in each bin.

    This uses the definition in https://cds.cern.ch/record/2643488, with the uncertainties on
    the data and the background added in quadrature as the background uncertainty. The result
    is positive where the data are at least the background.

    Parameters
    ----------
    data : array_like
        Observed yields.
    data_errs : array_like
        Uncertainties on ``data``.
    bkg : array_like
        Background prediction.
    bkg_errs : array_like
        Uncertainties on ``bkg``.

    Returns
    -------
    numpy.ndarray
        Significance in each bin.
    """
    err2 = _ne.evaluate(
        "data_errs**2 + bkg_errs**2",
        local_dict={"data_errs": data_errs, "bkg_errs": bkg_errs},
    )
    local = {"n": data, "b": bkg, "s2": err2}
    return _ne.evaluate(
        """(where(n >= b, 1, -1)
                        * sqrt(
                            2
                             * (
                                 n * log(n * (b + s2) / (b**2 + n*s2))
                                 - (b**2 / s2) * log(1 + (s2*(n-b))/(b*(b+s2)))
                                )
                          ))""",
        local_dict=local,
    )
