---
name: amazon-us-main-image-rules
description: Sourced US Amazon main-image requirements and review boundaries.
---

# Amazon US Main Image Rules

Source snapshot retrieved 2026-07-13:

- Product image guide: https://sellercentral.amazon.com/gp/help/external/G1881
- Clothing image guide: https://sellercentral.amazon.com/gp/help/external/G200498950

Recheck these sources for other marketplaces, category exceptions, or later
policy changes.

## General main-image requirements

- Represent the product accurately as a realistic, professional-quality image,
  including real scale, quantity, and color.
- Use a pure white RGB(255,255,255) background, except for the limited product
  types Amazon explicitly allows to use a lifestyle main image.
- Show the product as 85% of the image and keep the entire product in frame.
- Do not place text, extra logos, borders, color blocks, watermarks, or other
  graphics over the product or in the background. A real marking printed on
  the product is part of product identity and must not be erased merely because
  it is a logo.
- Show the product once and generally show one unit, plus only the accessories
  included in the sale.
- Do not include packaging unless it is an important product feature, such as
  an included carrying case or gift basket.
- Do not show props or accessories that are not included and could confuse the
  customer.
- Do not show a mannequin or hanger.

The general guide does not make "perfectly centered," "no shadow of any kind,"
or "strictly square" universal upload requirements. Treat those as composition
choices only when appropriate.

## Category rules

Apply category-specific rules rather than one generic apparel clause:

- Adult-size clothing main images use a standing model under the current US
  clothing guidance. The product must be complete and the aspect ratio should
  be close to 3:4 with 85% image-area occupancy.
- Clothing accessories and multipacks are shown flat without a model.
- Children's and baby undergarments, leotards, swimwear, and similar
  form-fitting items must be shown flat and without models.
- Footwear has its own orientation rule in the general guide.
- Clothing, multipacks, intimate products, and other specialized categories
  have additional rules. Load their current Seller Central page before use.

## Consequences

Use Amazon's documented language: images that fail requirements may be removed,
and a listing without a compliant main image may be suppressed from search
until one is provided. Do not replace this with a blanket claim of immediate
delisting.

## Validation boundary

Prompt constraints do not prove output compliance. Deterministic validation can
sample the white border and estimate a non-white bounding box, but it cannot
prove SKU accuracy, category eligibility, packaging truth, included items, or
Amazon acceptance.
