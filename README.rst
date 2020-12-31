ATLAS Matplotlib Style
======================
.. image:: https://img.shields.io/pypi/v/atlas-mpl-style?label=PyPI&style=for-the-badge   :alt: PyPI 

Provides a Matplotlib style replicating that used by the
`ATLAS <http://atlas.cern>`__ collaboration.

**Please open an issue if you find this style deviates from the guidelines.**

Install from PyPI using pip: :code:`pip install atlas-mpl-style`

Documentation: https://atlas-mpl.readthedocs.io/en/latest/index.html

In addition, this package also provides:

-  A function to draw the ATLAS label (requires ``usetex: true`` as set
   by the included ATLAS style)
-  A `plot` module containing functions to plot pre-binned histograms and limits. This includes functionality for plotting stacked backgrounds along with data and ratios in the usual ATLAS style.
-  A matplotlib style based on the background / foreground from the VIM
   `Paper <https://github.com/NLKNguyen/papercolor-theme>`__ color
   scheme, along with a print version with a white background.

   -  The default color cycle in all three styles is generated with HCL Wizard

-  Additional Matplotlib color definitions based on the Paper theme, and
   the `Oceanic
   Next <https://github.com/voronianski/oceanic-next-color-scheme>`__
   theme

UHI and the ``PlottableHistogram`` protocol
----------------------------------------- 

With the development of the `UHI
<https://github.com/henryiii/uhi>`__ interface, this package now has support for
histogram objects that follow the ``PlottableHistogram`` protocol.
``plot.Background`` objects can be constructed using ``PlottableHistograms`` and a
list of such ``Backgrounds`` can be passed to ``plot.plot_backgrounds`` omitting
the ``bins`` argument. The other histogram plotting functions could not be
modified to accept ``PlottableHistogram`` in a backward compatible manner since
they take ``bins`` before the histogram argument. Alternate versions of these
functions are therefore provided in the ``uhi`` module.

TeXLive and Fonts Needed
------------------------
When using the ATLAS style, text is typeset using LaTeX. A working TeXLive installation providing the following is required:

- pdflatex
- amsmath
- TeX Gyre Heros
- mathastext
- physics (the package)
- siunitx

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

**TeXLive is not required for the "paper" or "print" style.** `Fira Sans
<https://bboxtype.com/typefaces/FiraSans/>`__ and `Iosevka
<https://github.com/be5invis/Iosevka/releases/tag/v2.3.3>`__ should be installed
for these styles to appear as intended. However, neither is *necessary*.
