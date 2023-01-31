ATLAS Matplotlib Style
======================
.. image:: https://img.shields.io/pypi/v/atlas-mpl-style?label=PyPI&style=for-the-badge   :alt: PyPI 

**Despite the last commit date, this package is still maintained. If you have any comments or improvements, open an issue or PR.**

Provides a Matplotlib style replicating that used by the
`ATLAS <http://atlas.cern>`__ collaboration.

**Please open an issue if you find this style deviates from the guidelines.**

Install from PyPI using pip: :code:`pip install atlas-mpl-style`

Documentation: https://atlas-mpl.readthedocs.io/en/latest/index.html

In addition, this package also provides:

- A function to draw the ATLAS label
- A ``plot`` module containing functions to plot pre-binned histograms and
   limits. This includes functionality for plotting stacked backgrounds along
   with data and ratios in the usual ATLAS style.
- A matplotlib style based on the background / foreground from the VIM `Paper <https://github.com/NLKNguyen/papercolor-theme>`__ color scheme, along with a print version with a white background.
  - The default color cycle in all three styles is generated with HCL Wizard

- Additional Matplotlib color definitions based on the Paper theme, and the
   `Oceanic Next <https://github.com/voronianski/oceanic-next-color-scheme>`__
   theme

UHI and the PlottableHistogram protocol
----------------------------------------- 

With the development of the `UHI <https://github.com/henryiii/uhi>`__ interface,
this package now has support for histogram objects that follow the
``PlottableHistogram`` protocol. ``plot.Background`` objects can be constructed
using ``PlottableHistograms`` and a list of such ``Backgrounds`` can be passed
to ``plot.plot_backgrounds`` omitting the ``bins`` argument. The other histogram
plotting functions could not be modified to accept ``PlottableHistogram`` in a
backward compatible manner since they take ``bins`` before the histogram
argument. Alternate versions of these functions are therefore provided in the
``uhi`` module.

As a result of this support, the histogram objects returned by `Uproot 4
<https://github.com/scikit-hep/uproot4>`__ can be plotted directly, as can
`Boost-Histogram <https://github.com/scikit-hep/boost-histogram>`__ histograms
and `Hist <https://github.com/scikit-hep/hist>`__ objects (once the relevent PRs
are merged into those repositories).


``usetex=False`` Mode
------------------------

From version 0.15, it is possible to use the ATLAS style without a LaTeX
installation by passing ``usetex=False`` to ``use_atlas_style``. When this is
done, there are a few of points to bear in mind (particularly when producing PDF
plots):

1. The call to ``draw_atlas_label`` should be the last thing done before calling ``savefig``.
2. The figure ``dpi`` is set to 72 to match that of the PDF backend. This *must
   not* be changed if the plot will be exported in PDF or (E)PS format since
   doing so would cause the spacing in the ATLAS label to be incorrect.
3. Due to the above, the ``dpi`` parameter should not be passed when exporting to
   a raster format.
4. When converting a plotting script that uses ``usetex=True`` mode, ensure labels
   are updated to remove LaTeX macros that are not supported by Matplotlib's
   mathtext.

TeXLive and Fonts Needed
------------------------
When using the ATLAS style, text is (by default) typeset using LaTeX. From version 0.15, this can be avoided by passing ``usetex=False`` to ``use_atlas_style``.

A working TeXLive installation providing the following is required:

- pdflatex
- amsmath
- TeX Gyre Heros
- mathastext
- physics (the package)
- siunitx

If no LaTeX installation is available, the style will warn and fall back to the ``usetex=False`` behaviour.
To check if all necessary packages are installed, try building ``atlas_mpl_style/testing/ampl-test.tex``.

On Arch (and related distributions), the ``texlive-most`` group is sufficient.

On Debian (Jessie or above) or Ubuntu (18.04+), the following set of packages should be sufficient. It is however highly recommended
that you install `texlive-full` to obtain a complete installation of texlive.

- texlive
- texlive-latex-extra
- texlive-fonts-recommended
- texlive-lang-greek
- tex-gyre
- dvipng
- ghostscript

On CentOS 7, the supplied TeXLive (2012) is extremely old. TeXLive should be
installed from `upstream <https://www.tug.org/texlive/quickinstall.html>`__.

**TeXLive is not required for the "slides" or "print" style.** `Fira Sans
<https://bboxtype.com/typefaces/FiraSans/>`__ and `Iosevka
<https://github.com/be5invis/Iosevka/releases/>`__ should be installed
for these styles to appear as intended. However, neither is *necessary*.
