---
name: product-shots-reference-image-handling
description: Reference validation, resize, and cleanup behavior for optional API mode.
---

# Reference Image Handling

Before any request, validate that each reference exists, decodes successfully,
and is JPEG, PNG, or WebP. Reject unsupported MIME types and excess reference
counts.

Pass through a reference only when it is at most 1024 pixels on its longest
edge and at most 1 MB. Otherwise resize proportionally with Lanczos resampling.
Use JPEG for opaque inputs and WebP for inputs with alpha, reducing quality or
dimensions until the file is within the byte limit.

Create resized references with a safe named temporary file. Track every
temporary path and delete it in a `finally` block after success or failure.
Never expose a temporary reference path as a durable workflow artifact.

This preprocessing can remove small packaging text and fine product detail.
Keep accuracy-sensitive source images available for final visual comparison;
do not treat the reduced gateway input as the source of truth.
