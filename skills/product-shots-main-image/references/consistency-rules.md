---
name: product-shots-listing-consistency
description: Grounded consistency procedure for Amazon listing image sets.
---

# Listing Image Consistency

Generate the main image first, then pass both the accepted main image and the
original product references to every alternate-image call. Include explicit
invariants for product color, material, geometry, labels, controls, included
parts, and packaging.

Keep the visual system consistent where it helps scanning: palette, typography,
icon style, and lighting. Do not force every slot to use the same background or
composition when the slot has a different job.

After generation, compare each artifact with the source references and the
accepted main image. A reference image and a consistency prompt reduce drift;
they do not guarantee identity preservation.

Do not use unsourced conversion-lift percentages to choose slots. Select
alternate images from the product's customer questions, category norms, and
available factual evidence.
