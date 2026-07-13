---
name: product-shots-api-model-selection
description: Model routing supported by the optional product-shots API client.
---

# API Model Selection

This file applies only to explicit API mode. Built-in Codex mode delegates
model selection to the attached image-generation capability.

The bundled client recognizes these gateway model names:

| Family | Models | Endpoint |
|---|---|---|
| OpenAI | `gpt-image-1`, `gpt-image-2`, `dall-e-3` | `/images/generations` or `/images/edits` |
| Gemini | `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image-preview`, `gemini-2.5-flash-image` | `/chat/completions` |

The model name determines the endpoint family. Unknown names fail validation.
The client does not implement Flux, vendor-specific model families, automatic
model selection, or provider failover.

Choose the model explicitly based on the configured gateway's current
documentation and the user's requirements. Do not preserve hard-coded pricing,
latency, or quality rankings here because those claims change independently of
this repository.
