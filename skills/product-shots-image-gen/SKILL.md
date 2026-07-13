---
name: product-shots-image-gen
description: Generate or edit product, Amazon listing, A+, advertising, and social images from grounded briefs and reference images. In Codex, use the built-in image-generation capability by default without requiring an external API key. Use the bundled Python gateway client only when the user explicitly requests API, CLI, or gateway-driven batch automation. Validate saved files and maintain a manifest for multi-image workflows.
---

# Product Shots Image Generation

Turn a product-shots brief into saved, inspected image artifacts. Treat product
identity, packaging, included accessories, and claims as invariants taken from
the user's source material.

Resolve bundled `scripts/` and `references/` paths relative to this SKILL.md;
do not assume the user's current working directory is the skill directory.

## Choose an execution mode

Use **built-in mode** when an image-generation capability such as `$imagegen`
is available. This is the default in Codex and does not require an external API
key.

Use **API mode** only when the user explicitly asks for the bundled CLI, an
external gateway, provider/model controls, or unattended API batch automation.
API mode supports the OpenAI and Gemini model families listed in
`references/model-selection.md`. It does not support Flux and does not switch
providers automatically.

If built-in generation is unavailable, explain that API mode is optional and
requires configuration. Do not silently change modes.

## Built-in workflow

1. Read the caller's product brief and relevant marketplace reference.
2. Identify every input image as an edit target, product reference, or style
   reference. Inspect local references before generation.
3. Preserve exact product geometry, materials, colors, labels, packaging, and
   included accessories. Do not invent claims or included items.
4. Invoke the built-in image-generation capability once per distinct artifact.
   Use separate calls for different listing slots; do not use variants of one
   prompt as substitutes for distinct briefs.
5. Inspect every result for product drift, malformed text, misleading props,
   cropping, and prompt violations. Regenerate only failed artifacts.
6. Move or copy accepted files into the requested workspace directory. Never
   leave project deliverables only in a tool-owned cache directory.
7. Normalize to an exact platform canvas only when needed:

   ```bash
   python scripts/fit_canvas.py --input generated.png --output final.jpg \
     --width 970 --height 300 --mode cover
   ```

   Use `contain` when the entire product must remain visible. Use `cover` only
   when the brief has expendable bleed and a center crop is safe.
8. Run deterministic checks. For an Amazon main image:

   ```bash
   python scripts/validate_artifacts.py --image main.jpg \
     --expected-ratio 1:1 --main-image
   ```

   White-border and occupancy checks are conservative heuristics, not proof of
   Amazon acceptance.
9. For two or more artifacts, create and validate `manifest.json` according to
   `references/manifest-spec.md`. Record the exact prompt, source references,
   requested ratio, saved path, generation status, and validation result for
   each slot.

## API workflow

Read these references before using API mode:

- `references/parameter-spec.md` for flags, supported ratios, and output rules.
- `references/reference-image-handling.md` for preprocessing and cleanup.
- `references/error-handling.md` for retry and failure behavior.

Set up the isolated environment once:

```bash
bash scripts/setup.sh
```

Then run the wrapper:

```bash
scripts/run.sh \
  --prompt "A grounded product photograph on white" \
  --model gpt-image-2 \
  --aspect-ratio 1:1 \
  --reference-image ./reference.jpg \
  --output ./output/main \
  --manifest ./output/manifest.json
```

The output suffix comes from the actual image bytes. With `--n 3`, the CLI
saves `main-01.*`, `main-02.*`, and `main-03.*` and reports every path.

## Delivery rules

- Say "generated against Amazon constraints" until validation and human/agent
  review pass. Never guarantee marketplace approval.
- Keep product identity, misleading accessories, packaging accuracy, and claim
  accuracy as mandatory visual review items.
- Do not log prompts by default. API mode prints prompt text only with the
  explicit `--log-prompt` flag.
- Do not expose API keys in prompts, logs, manifests, examples, or fixtures.
- Do not retry with another provider or model without telling the user.
