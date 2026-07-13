---
name: product-shots-api-parameter-spec
description: CLI contract for the optional product-shots API image generator.
---

# API Parameter Specification

`scripts/generate.py` validates arguments before reading credentials or making
a request.

| Flag | Contract |
|---|---|
| `--prompt` | Required, non-empty, at most 4000 characters |
| `--model` | Required; one model from `model-selection.md` |
| `--aspect-ratio` | Optional: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `4:5`, `1.91:1`, `2.35:1`, or `21:9` |
| `--size` | OpenAI only; must be supported by the selected model |
| `--negative-prompt` | Appended to the effective prompt as an avoid clause |
| `--n` | OpenAI variants of one prompt; integer at least 1. Gemini and `dall-e-3` require 1 |
| `--reference-image` | Repeatable JPEG, PNG, or WebP path; Gemini max 9, OpenAI max 16 |
| `--output` | Output stem. The detected image format determines the suffix |
| `--manifest` | Optional JSON manifest path |
| `--log-prompt` | Opt in to printing the first 120 prompt characters |
| `--overwrite` | Explicitly allow replacing existing output or manifest files |
| `--trust-env` | Explicitly honor ambient proxy/environment settings; off by default |

## Canvas mapping

OpenAI API mode maps requested ratios to the nearest supported generation
canvas:

```text
1:1                                  -> 1024x1024
3:2, 4:3, 16:9, 1.91:1, 2.35:1, 21:9 -> 1536x1024
2:3, 3:4, 4:5, 9:16                  -> 1024x1536
```

This mapping does not produce exact platform ratios. Use `fit_canvas.py` after
generation and validate the result when an exact canvas is required.

## Credential resolution

API keys resolve in this order: `OMNIMAAS_API_KEY`,
`PRODUCT_SHOTS_IMAGEGEN_API_KEY`, `RENDER_API_KEY`,
`CANVASFLOW_IMAGEGEN_API_KEY`, then the compatible key files documented by the
CLI. Base URLs use the corresponding environment variables. An
`OMNIMAAS_API_KEY` without a URL uses `https://api.omnimaas.com/v1`.

Credential precedence is configuration lookup, not runtime provider fallback.
