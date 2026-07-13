---
name: product-shots-detail-page
description: Plan, generate, and review Amazon Basic or Premium A+ Content image assets from grounded product references. Use for Amazon A+, Enhanced Brand Content, detail-page modules, hero images, feature modules, comparison content, lifestyle modules, and mobile previews. Select current Content Manager templates, use each template's displayed image box, generate through product-shots-image-gen, and validate files without claiming guaranteed Amazon approval.
---

# Amazon A+ Content Images

Create image assets for the selected Amazon A+ Content templates. Keep the
creative content plan separate from Amazon's module definitions.

## Load current requirements

Read `references/aplus-specifications.md` before planning. The bundled rules are
a US-market snapshot retrieved 2026-07-13. Recheck Seller Central for another
marketplace or when the Content Manager displays different template limits.

Read `references/aplus-modules.md` for content-planning ideas, not as a list of
official Amazon modules.

## Workflow

1. Identify the target marketplace, ASIN family, brand, product references,
   source claims, and whether the account will use Basic A+, Premium A+, or
   Brand Story. If Premium eligibility is unknown, plan Basic A+ rather than
   assuming Premium access.
2. Select actual templates in A+ Content Manager:
   - Basic A+: at most five modules on the detail page;
   - Premium A+: at most seven modules;
   - Brand Story: a separate carousel area and contract.
3. Record every selected template and the exact image-box dimensions shown by
   Content Manager. Do not force all assets into 21:9 or 3:2. The general guide
   summarizes Basic and Premium image sizes, but individual template boxes are
   the delivery contract.
4. Build a factual content plan. Map customer questions and approved product
   evidence to the chosen template slots. Keep promotional claims, pricing,
   competitor comparisons, warranties, and time-sensitive language out unless
   current A+ policy explicitly permits them.
5. Generate one image per template image box through
   `product-shots-image-gen`. In Codex, use its built-in imagegen path. Pass the
   original SKU references to every call and preserve product geometry, color,
   labels, packaging, and included accessories.
6. Inspect each result for product drift, malformed text, unsupported claims,
   duplicated gallery imagery, watermarks, QR codes, and unreadable mobile
   content.
7. Fit each accepted image to its exact template box only after composition is
   approved. Use `cover` when the brief includes safe bleed; use `contain` when
   the product must remain fully visible.
8. Validate actual files and create `manifest.json` with one artifact per image
   box. Record the selected Amazon template, prompt, source references, expected
   dimensions, saved path, and validation result.
9. Preview the assembled content in both desktop and mobile views in A+ Content
   Manager. Revise only the failed modules.
10. Deliver the assets as generated against the recorded A+ constraints. Do
    not guarantee approval or publication.

## Review boundaries

Scripts can check format, file size, dimensions, aspect ratio, color mode, and
manifest completeness. The Content Manager preview and final review must still
confirm responsive cropping, text readability, claim accuracy, unique content,
alt text, template fit, and product consistency.
