ATLAS Matplotlib Style
======================
.. image:: https://img.shields.io/pypi/v/atlas-mpl-style?label=PyPI&style=for-the-badge   :alt: PyPI 

Provides a Matplotlib style replicating that used by the
`ATLAS <http://atlas.cern>`__ collaboration.

**Please open an issue if you find this style deviates from the guidelines.**

Install from PyPI using pip: :code:`pip install atlas-mpl-style`

Documentation: https://atlas-mpl.readthedocs.io/en/latest/index.html

In addition, this package also provides:

-  A matplotlib style based on the background / foreground from the VIM
   `Paper <https://github.com/NLKNguyen/papercolor-theme>`__ color
   scheme, along with a print version with a white background.

   -  The default color cycle in all three styles is generated with HCL Wizard

-  Additional Matplotlib color definitions based on the Paper theme, and
   the `Oceanic
   Next <https://github.com/voronianski/oceanic-next-color-scheme>`__
   theme
-  A function to draw the ATLAS label (requires ``usetex: true`` as set
   by the included ATLAS style)

TeXLive and Fonts Needed
------------------------
When using the ATLAS style, text is typeset using LaTeX. A working TeXLive installation providing the following is required:

- pdflatex
- amsmath
- TeX Gyre Heros
- mathastext
- physics (the package)
- siunitx

On Arch (and related distributions), the ``texlive-most`` group is sufficient.

On Debian (Jessie or above) or Ubuntu (18.04+), the following set of packages should be sufficient:

- texlive
- texlive-latex-extra
- texlive-fonts-recommended
- texlive-lang-greek
- tex-gyre
- dvipng
- ghostscript

On CentOS 7, the supplied TeXLive (2012) is extremely old. TeXLive should be installed from `upstream <https://www.tug.org/texlive/quickinstall.html>`__.

**TeXLive is not required for the "paper" or "print" style.**  
`Fira Sans <https://bboxtype.com/typefaces/FiraSans/>`__ and `Iosevka <https://github.com/be5invis/Iosevka/releases/tag/v2.3.3>`__ should be installed for these styles to look as intended. However, neither is *necessary*.

