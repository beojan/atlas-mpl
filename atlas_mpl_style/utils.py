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


_POISSON_LEVELS = {"poisson": 0.682689492, "poisson2": 0.95}


def poisson_errors(counts, interval="poisson"):
    """
    Return the down and up errors of a central Poisson confidence interval in each bin.

    These are ROOT's ``TH1::kPoisson`` and ``TH1::kPoisson2`` errors (PDG Review of Particle
    Physics 2026, Eqs. 40.81a and 40.81b). Requires SciPy.

    Parameters
    ----------
    counts : array_like
        Unweighted counts.
    interval : {"poisson", "poisson2"}, optional
        68.27% or 95% confidence level. Defaults to ``"poisson"``.

    Returns
    -------
    numpy.ndarray
        Down and up errors, with shape ``(2, N)``. Pass them as ``stat_errs`` to
        :func:`atlas_mpl_style.plot.plot_data`.

    Raises
    ------
    ValueError
        If ``interval`` is unknown, or a count is negative or not an integer.
    """
    from scipy.special import gammaincinv

    if interval not in _POISSON_LEVELS:
        raise ValueError(f"Unknown interval {interval!r}")
    n = _np.asarray(counts, dtype=float)
    if _np.any(n < 0) or _np.any(n != _np.round(n)):
        raise ValueError(
            "Poisson errors need unweighted counts, as non-negative integers. "
            "Counts that are not integers indicate a weighted histogram."
        )
    alpha = 1 - _POISSON_LEVELS[interval]
    # The interval's limits are quantiles of gamma distributions with shapes n and n + 1.
    low = _np.where(n > 0, gammaincinv(_np.maximum(n, 1e-300), alpha / 2), 0.0)
    high = gammaincinv(n + 1, 1 - alpha / 2)
    return _np.stack([n - low, high - n])
