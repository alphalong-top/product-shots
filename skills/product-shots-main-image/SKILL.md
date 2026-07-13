---
name: product-shots-main-image
description: Plan, generate, and review Amazon main and alternate listing images from product references. Use for Amazon main images, white-background product images, listing carousels, secondary images, infographics, detail shots, lifestyle images, what's-in-the-box images, and size references. Apply current marketplace and category rules, generate through product-shots-image-gen, run deterministic checks, and describe outputs as generated against constraints rather than guaranteed Amazon-compliant.
---

# Amazon Main And Alternate Images

Create grounded listing images without changing the SKU or implying that an
unvalidated image is guaranteed to pass Amazon review.

## Load rules

Read `references/hard-constraints.md` and
`references/image-specifications.md` before planning a main image. The bundled
rules are a US-market snapshot retrieved 2026-07-13. If the user targets
another marketplace or a regulated/category-specific product, verify that
market's current Seller Central rules before generation.

Use `references/secondary-images.md` only as design guidance for alternate
images. Amazon recommends additional images; the suggested slot mix is not a
mandatory platform template.

## Workflow

1. Identify the exact SKU, market, category, variant, package contents, and
   source-of-truth reference images. Ask only for missing facts that could
   change what is shown.
2. Decide scope:
   - main only: one main image;
   - listing set: main plus up to six alternate slots by default;
   - A+ Content: route to `product-shots-detail-page`.
3. Generate the main image first through `product-shots-image-gen`. In Codex,
   use its built-in imagegen path. Preserve real scale, quantity, color,
   product markings, packaging details, and included accessories.
4. Apply the general main-image constraints plus the exact category rules.
   Do not generalize adult-clothing rules to accessories, children's products,
   footwear, multipacks, or other categories.
5. Inspect the generated main image visually against the source references.
   Reject product drift, invented controls, altered labels, missing parts,
   misleading accessories, clipped product edges, and malformed packaging.
6. Run deterministic checks, selecting the planned ratio rather than assuming
   every category must be square:

   ```bash
   python ../product-shots-image-gen/scripts/validate_artifacts.py \
     --image ./main.jpg --expected-ratio 1:1 --main-image \
     --report ./validation-main.json
   ```

   Border and occupancy results are heuristics. A visual source comparison and
   Amazon review remain necessary.
7. Plan alternate slots by customer question and product category. Pass the
   accepted main image and original product references to every downstream
   generation. Prefer separate image calls with slot-specific prompts.
8. Create `manifest.json` using the image-gen manifest specification. For a
   seven-image set, use slots `main` and `secondary-01` through
   `secondary-06`; record prompt, references, path, and validation status.
9. Deliver only complete artifacts. Say "generated against the recorded Amazon
   constraints" and list any checks that remain manual.

## Review boundaries

Deterministic checks can verify file format, dimensions, aspect ratio, color
mode, white border sampling, a conservative non-white bounding box, and
manifest completeness.

Always review product identity, included accessories, packaging accuracy,
category exceptions, claims, product markings, and misleading composition
manually or with a grounded agent comparison. Do not claim that prompt text
alone enforces these properties.

AI-generated main images may be unacceptable where Amazon requires a photo of
the actual product. Surface that risk instead of presenting an AI render as an
automatically upload-ready photograph.
