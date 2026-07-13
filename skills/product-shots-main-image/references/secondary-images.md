---
name: amazon-alternate-image-planning
description: Customer-question-driven planning guidance for Amazon alternate listing images.
---

# Alternate Listing Images

Amazon recommends additional images to help customers evaluate a product. The
mix below is design guidance, not a mandatory platform template and not an
evidence-backed conversion ranking.

## Plan slots

Start from customer questions and verified product facts. Common slot types:

- **Infographic:** explain a small set of factual features with legible labels.
- **Multi-angle:** show form from useful additional views.
- **Detail:** show material, finish, controls, stitching, or construction.
- **Lifestyle:** show a truthful use context without implying unsupported
  performance or included accessories.
- **Variants:** show only variants that actually exist and label them clearly.
- **What's included:** show the exact package contents without invented items.
- **Size/fit:** use verified dimensions or a non-misleading scale reference.

## Suggested category emphasis

| Category | Questions commonly worth answering |
|---|---|
| Electronics | controls, compatibility, ports, form factor, included parts |
| Apparel/footwear | fit, fabric, construction, views, available variants |
| Home goods | room fit, dimensions, included parts, use context |
| Beauty/personal care | texture, packaging, verified ingredients, use context |
| Food/supplements | package contents, verified label facts, serving/use context |

These suggestions never override category rules or product evidence.

## Generation contract

For every slot:

1. Pass the original product references and accepted main image.
2. State invariants for geometry, materials, color, labels, package contents,
   and scale.
3. Choose an intentional canvas. Square is a practical default for many sets,
   not a universal Amazon requirement.
4. Keep text readable at mobile preview size. Use a visual preview rather than
   claiming an unsourced point-size threshold is an Amazon rule.
5. Compare the result with source references and record prompt, path, and
   validation status in the workflow manifest.
