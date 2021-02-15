ATLAS Style
===========

The main purpose of this package is to provide a Matplotlib style closely
resembling that used by the `ATLAS <https://atlas.cern/>`_ experiment for
it's plots.

This style can be activated by calling ::

  import atlas_mpl_style as ampl
  ampl.use_atlas_style()

When the ATLAS style is active, text is typeset using LaTeX, and the
standard ATLAS label can be drawn using the ``ampl.draw_atlas_label``
function. The use of LaTeX can be disabled by instead calling ``ampl.use_atlas_style(usetex=False)``.

The axis labels should be set using the ``ampl.set_xlabel`` and
``ampl.set_ylabel`` functions, to ensure they are correctly
right / top aligned.

Other Styles
============

Additionally, two other styles based on the Paper VIM color scheme
are provided. **Slides** has an off-white central background, and works well
on slides. **Print** has a white background, for use in print. These styles
do not use LaTeX for text typesetting, and can be activated using ::

  # import matplotlib in the usual way
  import matplotlib.pyplot as plt
  import atlas_mpl_style as ampl
  plt.style.use('slides')
  # or
  plt.style.use('print')
