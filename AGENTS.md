# Agent instructions

## Docstring rules

1. **Format.** Follow PEP 257 and numpydoc. The type line lists every accepted kind. Bullets
   give each form's values and shapes, and say what each one means. Don't repeat the options in
   the prose. Wrap lines at the same length as the code.
2. **Scope.** Document purpose, usage, and anything that would surprise a caller. Leave out
   implementation details, rationale, and caveats that don't prevent a surprise.
3. **Audience.** Write for ATLAS members and students. Use ATLAS and ROOT terms without
   explaining them, but state exactly what each option does.
4. **Precision.** Define a term once and reuse it. Make order explicit wherever it matters.
   Prefer descriptions that hold up when the output is rescaled, such as a figure's shape rather
   than its size.
5. **Neutrality.** Don't promote legacy features, discouraged combinations, or one option over
   another in examples.
6. **Wording.** Use short, plain, concrete sentences. Describe the same behaviour the same way
   everywhere.
7. **Process.** Verify every claim against the code, and show proposed changes for approval
   before applying them.
