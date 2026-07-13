---
name: product-shots-api-error-handling
description: Retry and failure contract for the optional product-shots API client.
---

# API Error Handling

Reference-image requests retry connection errors, timeouts, HTTP 429, and HTTP
500/502/503/504/524 up to three attempts with bounded backoff. Authentication
errors, malformed responses, invalid base64, missing images, and text-only
responses fail immediately. Text-to-image requests make one attempt.

The client validates that an OpenAI response contains exactly the requested
number of image entries and that every entry contains `b64_json` or a URL. It
validates Gemini's nested response shape and embedded image data. Saved payloads
must decode as supported images.

No error path switches model or provider automatically. A caller may retry only
after reporting the failure and deciding whether the same request is safe to
repeat.

Errors may include a bounded response excerpt for diagnosis. They must never
include an API key. Prompt logging is disabled unless `--log-prompt` is set.
