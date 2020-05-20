import numexpr as _ne
import numpy as _np

def significance(data, data_errs, bkg, bkg_errs):
    """
    Calculates significance in each bin

    Uses the significance definition in https://cds.cern.ch/record/2643488

    Parameters
    ------------
    data : array_like
    data_errs : array_like
              Errors / uncertainties on `data`
    bkg : array_like
         Total background prediction
    bkg_errs : array_like
            Errors / uncertainties on `bkg`
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
