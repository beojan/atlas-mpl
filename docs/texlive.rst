TeXLive and Fonts
=================

Default Mode (``usetex=False``)
-------------------------------

``ampl.use_atlas_style()`` sets ``usetex=False`` by default, so no LaTeX
installation is required.

In this mode, Matplotlib renders ``$...$`` expressions with its built-in
mathtext engine using upright text by default (``mathtext.default = "regular"``)
to match surrounding sans-serif labels. Write ``\mathit{...}`` (for example
``$\mathit{m}_{jj}$`` or ``$\mathit{p}_{\mathrm{T}}$``) when a math symbol
should be italic.

If you convert a plotting script from ``usetex=True`` to ``usetex=False``,
replace macros from LaTeX packages such as ``siunitx`` or ``physics`` with plain
text or standard Matplotlib mathtext.

LaTeX Mode (``usetex=True``)
----------------------------

If you have a LaTeX installation available, pass ``usetex=True`` to
``ampl.use_atlas_style(usetex=True)`` to typeset text with LaTeX.

``use_atlas_style(usetex=True)`` checks for ``pdflatex``, ``dvipng``, and ``gs``
(Ghostscript) on ``PATH``. If any of these programs is missing, it emits a
warning and falls back to ``usetex=False``.

The LaTeX preamble requires a working TeXLive installation providing:

- ``pdflatex``
- ``fontenc`` (with ``LGR`` and ``T1`` encodings)
- ``tgheros`` (TeX Gyre Heros)
- ``amsmath``
- ``mathastext``
- ``physics``
- ``siunitx``

To check whether all required packages are installed, compile
``atlas_mpl_style/testing/ampl-test.tex`` (which also uses the ``standalone``
class).

On Arch Linux and related distributions, ``texlive-most`` and ``ghostscript``
are sufficient.

On Debian or Ubuntu, the following packages are sufficient (or install
``texlive-full`` for a complete TeXLive installation):

- ``texlive``
- ``texlive-latex-extra``
- ``texlive-fonts-recommended``
- ``texlive-lang-greek``
- ``tex-gyre``
- ``dvipng``
- ``ghostscript``

Font Resolution and ``set_font``
--------------------------------

When ``usetex=False`` (including in the ``print`` style, which never uses
LaTeX), Matplotlib selects the first installed font from the active style's
preference list:

- **ATLAS style** (``ampl.use_atlas_style()``):

  - **Sans-serif** (default, including mathtext with ``stixsans`` fallback):
    TeX Gyre Heros, Helvetica, Nimbus Sans, FreeSans, Arial.
  - **Serif**: TeX Gyre Termes, Times, Times Roman, Times New Roman,
    Nimbus Roman, FreeSerif.
  - **Monospace**: TeX Gyre Cursor, Courier, Courier New, Nimbus Mono,
    FreeMono.

- **Print style** (``plt.style.use("print")``):

  - **Sans-serif** (default, with ``stixsans`` mathtext): TeX Gyre Heros,
    Helvetica Neue, Helvetica, Free Sans, Nimbus Sans L, Arial, DejaVu Sans.
  - **Serif**: TeX Gyre Pagella, Palatino, Palatino Linotype, URW Palladio L,
    DejaVu Sans.
  - **Monospace**: Source Code Pro, Inconsolata, Monaco, Consolas, Ubuntu Mono,
    DejaVu Sans Mono.

To switch to a different font or change the base font size, call
``ampl.set_font(family=..., size=...)`` after activating the style. ``size``
scales the style's title, axis label, tick label, and legend sizes
proportionally. ``family`` prepends one or more preferred sans-serif fonts when
``usetex=False``.
