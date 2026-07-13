---
name: product-shots-manifest-spec
description: Output manifest contract for multi-image product-shots workflows.
---

# Output Manifest

Create one `manifest.json` for every multi-image workflow. Keep it beside the
generated artifacts and update each artifact status as work progresses.

```json
{
  "schema_version": 1,
  "workflow": "amazon-listing",
  "mode": "builtin",
  "status": "complete",
  "references": ["refs/product-front.jpg"],
  "artifacts": [
    {
      "slot": "main",
      "status": "complete",
      "path": "main.png",
      "prompt": "The exact prompt used for this artifact",
      "requested_aspect_ratio": "1:1",
      "validation": {
        "status": "pass",
        "report": "validation-main.json"
      }
    }
  ]
}
```

Required top-level fields: `schema_version`, `workflow`, `mode`, `status`, and
`artifacts`. Required artifact fields: `slot`, `status`, `path`, and `prompt`.
Use workspace-relative paths when practical. Never mark the workflow complete
while an expected slot is missing or any artifact has a failed validation.

Validate a seven-image Amazon listing manifest with:

```bash
python scripts/validate_artifacts.py \
  --manifest manifest.json \
  --expected-slot main \
  --expected-slot secondary-01 \
  --expected-slot secondary-02 \
  --expected-slot secondary-03 \
  --expected-slot secondary-04 \
  --expected-slot secondary-05 \
  --expected-slot secondary-06
```
