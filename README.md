<!-- ============================================================ -->
<!-- TIER 1: ABOVE THE FOLD                                       -->
<!-- ============================================================ -->

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset=".github/logo-light.svg">
    <img alt="product-shots" src=".github/logo-light.svg" width="540">
  </picture>

  <p><strong>One product photo in. Your full e-commerce visual stack out.</strong></p>
</div>

<div align="center">

[![License: MIT][license-shield]][license-url]
[![Skills: 7][skills-count-shield]][skills-anchor]
[![Agent Skills][skills-shield]][skills-url]
[![Platforms: 5][platforms-shield]][platforms-anchor]
[![Status: alpha][status-shield]][status-anchor]

</div>

<div align="center">
  <a href="#gallery">Gallery</a> &middot;
  <a href="#features">Features</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#install">Install</a> &middot;
  <a href="#usage">Usage</a> &middot;
  <a href="#skills">Skills</a>
</div>

<br>

> Drop grounded SKU references into Codex or another compatible agent. Build Amazon listing images, A+ assets, advertising creatives, and social content with saved prompts, manifests, and deterministic file checks. Marketplace acceptance still requires category-aware review.

---

<!-- ============================================================ -->
<!-- GALLERY — moved to the top                                    -->
<!-- ============================================================ -->

## Gallery

Real outputs from the five user-facing `product-shots-*` skills. Two products, one section per skill, two examples per skill, two-or-more images per example. Generated end-to-end via `product-shots-image-gen` against the OmniMaaS gateway (`gemini-3-pro-image-preview`). No manual prompt tuning beyond what the skill emits.

### `product-shots-main-image` — Amazon main + alternate images

> Historical outputs generated against a white-background and product-occupancy brief. Gallery files demonstrate output quality, not Amazon acceptance or current-policy compliance.

<table>
<tr>
<th align="center" colspan="2">☕ Smart espresso machine</th>
<th align="center" colspan="2">👗 Women's floral midi dress</th>
</tr>
<tr>
<td><img src="assets/gallery/coffee-machine/main-image/01-amazon-main.jpeg" width="200"></td>
<td><img src="assets/gallery/coffee-machine/main-image/02-secondary-feature.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/main-image/01-amazon-main.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/main-image/02-secondary-feature.jpeg" width="200"></td>
</tr>
<tr>
<td align="center"><sub>Main, white bg</sub></td>
<td align="center"><sub>Secondary, 3/4 detail</sub></td>
<td align="center"><sub>Main, full body</sub></td>
<td align="center"><sub>Fabric closeup</sub></td>
</tr>
</table>

### `product-shots-detail-page` — A+ Content modules

> Hero band + feature module + lifestyle scene + spec callouts, with cross-image consistency anchors so the SKU doesn't morph between modules.

<table>
<tr>
<th align="center" colspan="2">☕ Smart espresso machine</th>
<th align="center" colspan="2">👗 Women's floral midi dress</th>
</tr>
<tr>
<td><img src="assets/gallery/coffee-machine/detail-page/01-hero-band.jpeg" width="200"></td>
<td><img src="assets/gallery/coffee-machine/detail-page/02-feature-module.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/detail-page/01-hero-band.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/detail-page/02-lifestyle-feature.jpeg" width="200"></td>
</tr>
<tr>
<td align="center"><sub>Wide hero creative</sub></td>
<td align="center"><sub>Feature module</sub></td>
<td align="center"><sub>Hero band, lifestyle</sub></td>
<td align="center"><sub>Café feature, 3:2</sub></td>
</tr>
</table>

### `product-shots-multi-angle` — fashion-on-model lookbook

> 14 identity anchors (face / hair / skin / eyes / outfit / accessories / lighting / camera) locked across all frames so every angle reads as the same model wearing the same look. Specialized for **fashion-on-model** lookbooks; works on products without a model but with reduced identity fidelity.

**👗 Floral midi dress — 9 canonical angles (killer demo)**

<table>
<tr>
<td><img src="assets/gallery/dress/multi-angle/01-front.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/02-three-quarter-front.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/03-side.jpeg" width="180"></td>
</tr>
<tr>
<td align="center"><sub>1. Front</sub></td>
<td align="center"><sub>2. 3/4 front</sub></td>
<td align="center"><sub>3. Side</sub></td>
</tr>
<tr>
<td><img src="assets/gallery/dress/multi-angle/04-three-quarter-back.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/05-back.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/06-detail.jpeg" width="180"></td>
</tr>
<tr>
<td align="center"><sub>4. 3/4 back</sub></td>
<td align="center"><sub>5. Back</sub></td>
<td align="center"><sub>6. Detail closeup</sub></td>
</tr>
<tr>
<td><img src="assets/gallery/dress/multi-angle/07-on-hanger.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/08-lifestyle-indoor.jpeg" width="180"></td>
<td><img src="assets/gallery/dress/multi-angle/09-lifestyle-outdoor.jpeg" width="180"></td>
</tr>
<tr>
<td align="center"><sub>7. On hanger</sub></td>
<td align="center"><sub>8. Lifestyle indoor</sub></td>
<td align="center"><sub>9. Lifestyle outdoor</sub></td>
</tr>
</table>

**☕ Smart espresso machine — 2-angle product rotation (non-fashion fallback)**

<table>
<tr>
<td><img src="assets/gallery/coffee-machine/multi-angle/01-front.jpeg" width="220"></td>
<td><img src="assets/gallery/coffee-machine/multi-angle/02-three-quarter.jpeg" width="220"></td>
</tr>
<tr>
<td align="center"><sub>Front</sub></td>
<td align="center"><sub>3/4 angle</sub></td>
</tr>
</table>

### `product-shots-ad-creative` — platform-native ads

> Per-platform style profiles (TikTok UGC ≠ Meta editorial ≠ Google polished) baked into the prompt; banned-words filter applied; user copy preserved verbatim.

<table>
<tr>
<th align="center" colspan="2">☕ Smart espresso machine</th>
<th align="center" colspan="2">👗 Women's floral midi dress</th>
</tr>
<tr>
<td><img src="assets/gallery/coffee-machine/ad-creative/01-tiktok-ugc.jpeg" width="200"></td>
<td><img src="assets/gallery/coffee-machine/ad-creative/02-meta-feed.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/ad-creative/01-tiktok-ugc.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/ad-creative/02-meta-feed.jpeg" width="200"></td>
</tr>
<tr>
<td align="center"><sub>TikTok UGC, 9:16</sub></td>
<td align="center"><sub>Meta feed, 1:1</sub></td>
<td align="center"><sub>TikTok UGC, 9:16</sub></td>
<td align="center"><sub>Meta feed, 1:1</sub></td>
</tr>
</table>

### `product-shots-social-post` — feed / story / reel / carousel

> Industry-aware DNA preset (beauty ≠ hardware ≠ apparel each get a different visual language) + 14-point self-check before render.

<table>
<tr>
<th align="center" colspan="2">☕ Smart espresso machine</th>
<th align="center" colspan="2">👗 Women's floral midi dress</th>
</tr>
<tr>
<td><img src="assets/gallery/coffee-machine/social-post/01-ig-feed.jpeg" width="200"></td>
<td><img src="assets/gallery/coffee-machine/social-post/02-ig-story.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/social-post/01-ig-carousel.jpeg" width="200"></td>
<td><img src="assets/gallery/dress/social-post/02-ig-story.jpeg" width="200"></td>
</tr>
<tr>
<td align="center"><sub>IG feed, 1:1</sub></td>
<td align="center"><sub>IG story, 9:16</sub></td>
<td align="center"><sub>IG carousel, 1:1</sub></td>
<td align="center"><sub>IG story, 9:16</sub></td>
</tr>
</table>

---

<!-- ============================================================ -->
<!-- TIER 2: SCAN QUICKLY                                          -->
<!-- ============================================================ -->

## The Problem

One SKU on a cross-border listing can require a main image, alternate listing images, A+ template assets, ad variants, and social crops. Each artifact needs the right source facts, canvas, and review instead of one generic prompt reused everywhere.

Sellers either pay a closed SaaS to do it (and hand over their brand assets), hire a studio (slow, expensive, single-channel), or burn weeks tuning Midjourney prompts by hand. None of those compose with the rest of an AI-first workflow.

`product-shots` ships this workflow as open-source Agent Skills. In Codex it uses the built-in image-generation capability by default. An isolated Python gateway client remains available for users who explicitly choose API or CLI automation.

**If you sell on Amazon, Shopify, TikTok Shop, or an independent storefront — and you want the visual production layer to be code you control, not a subscription — you're the target user.**

## Features

Seven skills, ordered by what carries the most weight in a real listing. The first three are where the wow lives; the rest are platform breadth, then the infrastructure that makes the whole thing portable.

| Skill | What you get |
|---|---|
| [`product-shots-multi-angle`](#skills) | One reference photo of a model + outfit → a 9-angle lookbook workflow. Identity anchors and per-frame review reduce drift; they do not guarantee biometric or garment consistency. |
| [`product-shots-detail-page`](#skills) | **Basic or Premium A+ Content assets** mapped to templates selected in Content Manager, with exact image-box dimensions, desktop/mobile preview, and grounded SKU references. |
| [`product-shots-main-image`](#skills) | Amazon **main + alternate images** generated against sourced marketplace/category constraints, followed by file checks and mandatory visual review. |
| [`product-shots-ad-creative`](#skills) | Platform-native ad creatives across **8 platforms** — Meta, TikTok, Google Display, Google Demand Gen, YouTube, Pinterest, LinkedIn, X. Per-platform style profiles, banned-words filter, user copy preserved verbatim. |
| [`product-shots-social-post`](#skills) | Feed / Story / Reel / Carousel posts with industry-aware DNA (beauty vs hardware vs apparel each get a different visual language) and a 14-point self-check before render. |
| [`product-shots-image-gen`](#skills) | The shared execution workflow. Codex built-in image generation is the default and needs no external key. Explicit API mode supports the documented OpenAI/Gemini gateway routes, validates inputs/responses, saves every result, and produces manifests. |
| [`product-shots`](#skills) | The **intent router** at the front door. Four-stage clarification (≤4 rounds), Visual DNA injection (platform × industry), then dispatch to one of the five business skills above. Stops underspecified prompts from wasting a render. |

> **What product-shots is not:** a generic design tool. It does not write copy, build landing pages, or replace a brand designer. Every skill is sharpened around one job in a cross-border seller's daily workflow.

## Quick Start

Three distinct operations. Pick the one that matches your job:

```text
"Generate Amazon listing photos for this product"            — main + alternate images generated against current recorded constraints and reviewed per slot.
"Get a 9-angle shoot of this dress"                          — fashion-on-model lookbook: front / back / side / 3/4 / detail / hanger / lifestyle, 14 identity anchors locked.
"Make cross-platform ad creatives for this product"          — Meta + TikTok + Google + YouTube variants in correct ratios, platform style applied, copy preserved verbatim.
```

Each command lands in `product-shots`, which clarifies what's missing (≤4 rounds), injects platform × industry Visual DNA, and dispatches to the right specialist. The render goes through the shared `product-shots-image-gen` engine.

## Install

```bash
npx skills add motiful/product-shots
```

This registers the seven skills with whichever Agent Skills harness you're running (Claude Code, Codex, Cursor, Windsurf, GitHub Copilot).

**Codex:** no image API key is required. `product-shots-image-gen` uses Codex's built-in image-generation capability by default.

**Optional API/CLI mode:** configure a gateway only when you explicitly want provider/model controls or unattended API automation:

```bash
# Option A — Cloubic / OmniMaaS gateway
export OMNIMAAS_API_KEY='sk-...'
# optional: defaults to https://api.omnimaas.com/v1 when API key is set
export OMNIMAAS_BASE_URL='https://api.omnimaas.com/v1'

# Option B — any other OpenAI-SDK-compatible image gateway
export PRODUCT_SHOTS_IMAGEGEN_API_KEY='sk-...'
export PRODUCT_SHOTS_IMAGEGEN_BASE_URL='https://your-image-gateway.example.com/v1'

# Option C — file-based, no env vars
echo "sk-..." > ~/.product_shots_imagegen_api_key
chmod 600 ~/.product_shots_imagegen_api_key
```

Install API-mode dependencies into an isolated environment with `bash skills/product-shots-image-gen/scripts/setup.sh`, then use its `scripts/run.sh` wrapper. API keys are sent only in the `Authorization` header and are never printed.

**Manual registration** (clone + symlink — only if you don't want the `npx skills` route). The skills are platform-agnostic — register in whichever Agent Skills harness root your editor uses:

```bash
git clone https://github.com/motiful/product-shots ~/skills/product-shots

SKILLS=(product-shots product-shots-image-gen \
        product-shots-main-image product-shots-detail-page \
        product-shots-multi-angle product-shots-ad-creative \
        product-shots-social-post)

# Pick whichever harness root(s) you actually use:
# Claude Code   → ~/.claude/skills/
# Codex         → ~/.agents/skills/
# Cursor        → ~/.cursor/skills/
# Windsurf      → ~/.codeium/windsurf/skills/
# GitHub Copilot (VS Code) → ~/.copilot/skills/

HARNESS=~/.claude/skills    # change to the path for your editor
mkdir -p "$HARNESS"
for s in "${SKILLS[@]}"; do
  ln -sfn ~/skills/product-shots/skills/$s "$HARNESS/$s"
done
```

## Usage

Two real scenarios, end-to-end. Both start from a single reference photo in your working directory.

### Scenario A — Smart coffee machine, full Amazon listing

```text
> here's the product shot: ./refs/coffee-machine-v2.jpg
> give me the full Amazon listing — main, 6 secondaries, A+ page, and 4 ad creatives
```

What `product-shots` will do, in order:

1. **Clarify** category (small kitchen appliance), market (US Amazon), brand voice in ≤4 questions.
2. **Dispatch** `product-shots-main-image` → a main image plus six alternate slots, each generated and reviewed against the recorded US/category rules.
3. **Dispatch** `product-shots-detail-page` → assets for the Basic or Premium A+ templates selected in Content Manager, with the original SKU references passed to every call.
4. **Dispatch** `product-shots-ad-creative` → 4 variants targeting Meta feed, Meta story, TikTok feed, YouTube short. Each in correct ratio with platform-native styling.

Output: organized image files, manifests, and validation reports. Review Content Manager previews and remaining manual checks before upload.

### Scenario B — Women's dress, 9-angle shoot + social rollout

```text
> reference: ./refs/dress-floral.jpg
> i need a 9-angle shoot + 5 Instagram posts (3 feed, 2 story)
```

What happens:

1. `product-shots` confirms this is apparel (triggers `product-shots-multi-angle`'s fashion-on-model profile).
2. `product-shots-multi-angle` locks face, hair, skin, eyes, outfit, accessories, lighting, and camera — then renders front / 3/4 front / side / 3/4 back / back / detail (closeup) / on-hanger / lifestyle (indoor) / lifestyle (outdoor).
3. `product-shots-social-post` applies the apparel industry DNA preset (editorial, warm-neutral palette, type hierarchy) and produces 3 feed posts (1:1) + 2 stories (9:16), all derived from the same 9-angle set so the campaign reads as one shoot.

Output: 14 requested images plus a manifest. Identity and garment consistency are review goals, not guaranteed model properties.

---

<!-- ============================================================ -->
<!-- TIER 3: SUPPORTING CONTENT                                    -->
<!-- ============================================================ -->

## Skills

Each skill is self-contained — a `SKILL.md` plus its `references/` and `scripts/`. Trigger phrases below are the canonical ones; `product-shots` accepts free-form natural-language variants and routes on intent, not exact wording.

| Skill | Trigger | Primary deliverable |
|---|---|---|
| `product-shots` | (front door for all of the below) | Clarified, DNA-injected dispatch to one specialist |
| `product-shots-multi-angle` | "9-angle shoot of this dress" | 9 identity-locked angles, same model in same outfit |
| `product-shots-detail-page` | "build an A+ detail page for this" | Image assets mapped to selected Basic/Premium A+ templates |
| `product-shots-main-image` | "Amazon main image for this product" | Main + alternate set with validation reports |
| `product-shots-ad-creative` | "cross-platform ad creatives" | 8-platform ad variants, per-platform style profiles |
| `product-shots-social-post` | "Instagram / TikTok posts for this" | Feed / Story / Reel / Carousel with industry DNA |
| `product-shots-image-gen` | (called by the others; or `"just generate: <prompt>"`) | Built-in generation by default; optional OpenAI/Gemini API mode |

## How It Works

`product-shots` turns sourced constraints into a brief, generates one artifact per slot, inspects the actual output, runs deterministic file checks, and records the result in a manifest. Prompt constraints reduce errors but do not prove compliance or identity preservation. Codex uses built-in image generation; optional API mode uses one explicitly selected OpenAI or Gemini gateway route and never performs silent provider failover.

## What's Inside

```text
skills/
  product-shots/              — intent router (4-stage clarification + Visual DNA injection)
  product-shots-image-gen/    — built-in workflow + optional OpenAI/Gemini API client + validators
  product-shots-main-image/   — sourced Amazon rules + category-aware review
  product-shots-detail-page/  — Basic/Premium A+ template asset workflow
  product-shots-multi-angle/  — 14-anchor identity lock, fashion-editorial portraits
  product-shots-ad-creative/  — 8-platform style profiles, banned-words filter
  product-shots-social-post/  — 7-industry DNA presets, 14-point self-check
.github/          — logo (light/dark), repo metadata
assets/gallery/   — 27 real outputs across 5 skills × 2 products
LICENSE           — MIT
```

## Compatibility

Built against the [Agent Skills](https://agentskills.io) protocol. The default path requires a host with a built-in image-generation capability, such as Codex. Hosts without one can use the explicitly configured Python API client when their gateway implements the documented OpenAI/Gemini-compatible response shapes.

## Contributing

Issues and PRs welcome. Each skill is independently reviewable — open a PR scoped to one skill at a time. For new platform support (e.g., a new ad network in `product-shots-ad-creative`), include the platform's spec source and a sample render.

## Contact

The skills in this repo are the **open-source surface** of what we build. `motiful` runs an internal stack that goes further — bigger product galleries from a single brand kit, model-locked lookbooks at studio scale, on-prem rendering, brand-asset integration, and managed pipelines for sellers shipping thousands of SKUs.

If you're a cross-border seller, agency, or platform team and any of that is interesting:

- **Commercial / partnerships / custom skills** — [kungfu@motiful.ai](mailto:kungfu@motiful.ai)
- **Follow what we ship next** — [@whiletrue0x on X](https://x.com/whiletrue0x/)

Bug reports and skill-level feature requests should stay on [GitHub Issues](https://github.com/motiful/product-shots/issues) — the inbox above is for the things issues can't capture.

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
  <sub>Forged with <a href="https://github.com/motiful/skill-forge">Skill Forge</a> · Crafted with <a href="https://github.com/motiful/readme-craft">Readme Craft</a></sub>
  <br>
  <sub><i>Submitted to UCWS Singapore Hackathon 2026. Built by <a href="https://github.com/motiful">motiful</a>.</i></sub>
</div>

<!-- Reference-style link definitions -->
[license-shield]: https://img.shields.io/badge/License-MIT-green.svg
[license-url]: LICENSE
[skills-count-shield]: https://img.shields.io/badge/skills-7-success.svg
[skills-anchor]: #skills
[skills-shield]: https://img.shields.io/badge/Agent%20Skills-compatible-DA7857?logo=anthropic
[skills-url]: https://agentskills.io
[platforms-shield]: https://img.shields.io/badge/platforms-CC%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%20Windsurf%20%C2%B7%20Copilot-5b8def
[platforms-anchor]: #compatibility
[status-shield]: https://img.shields.io/badge/status-alpha-orange.svg
[status-anchor]: #the-problem
