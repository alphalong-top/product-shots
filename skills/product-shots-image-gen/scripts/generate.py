#!/usr/bin/env python3
"""Optional API-mode image generator for product-shots.

Codex users should normally use the built-in image-generation capability
described by the parent SKILL.md. This CLI exists for explicitly selected API
or batch automation against OmniMaaS or another compatible gateway.
"""

import argparse
import base64
import binascii
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

import requests
from PIL import Image, UnidentifiedImageError


OMNIMAAS_DEFAULT_BASE_URL = "https://api.omnimaas.com/v1"
API_KEY_PATH = Path.home() / ".product_shots_imagegen_api_key"
COMPAT_API_KEY_PATH = Path.home() / ".product_shots_render_api_key"
LEGACY_API_KEY_PATH = Path.home() / ".canvasflow_imagegen_api_key"

TIMEOUT = 240
REF_MAX_DIM = 1024
REF_MAX_BYTES = 1024 * 1024
MAX_PROMPT_CHARS = 4000

I2I_TIMEOUT = (30, 180)
I2I_MAX_ATTEMPTS = 3
I2I_BACKOFF_SCHEDULE = (1, 4, 16)
I2I_RETRY_STATUSES = {429, 500, 502, 503, 504, 524}

OPENAI_MODELS = {"gpt-image-1", "gpt-image-2", "dall-e-3"}
GEMINI_MODELS = {
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image-preview",
    "gemini-2.5-flash-image",
}

ASPECT_RATIOS = {
    "1:1",
    "16:9",
    "9:16",
    "4:3",
    "3:4",
    "3:2",
    "2:3",
    "4:5",
    "1.91:1",
    "2.35:1",
    "21:9",
}

# These are generation canvas families, not promises of exact platform ratios.
OPENAI_SIZE_BY_RATIO = {
    "1:1": "1024x1024",
    "3:2": "1536x1024",
    "4:3": "1536x1024",
    "16:9": "1536x1024",
    "1.91:1": "1536x1024",
    "2.35:1": "1536x1024",
    "21:9": "1536x1024",
    "2:3": "1024x1536",
    "3:4": "1024x1536",
    "4:5": "1024x1536",
    "9:16": "1024x1536",
}

OPENAI_SIZES_BY_MODEL = {
    "gpt-image-1": {"1024x1024", "1536x1024", "1024x1536"},
    "gpt-image-2": {"1024x1024", "1536x1024", "1024x1536"},
    "dall-e-3": {"1024x1024", "1792x1024", "1024x1792"},
}

SUPPORTED_REFERENCE_FORMATS = {"JPEG", "PNG", "WEBP"}
FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}
FORMAT_TO_SUFFIX = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


class ImageGenError(RuntimeError):
    """Base error surfaced to CLI callers without a traceback."""


class ArgumentError(ImageGenError):
    pass


class ConfigurationError(ImageGenError):
    pass


class ResponseError(ImageGenError):
    pass


def make_http_session(*, trust_env: bool = False) -> requests.Session:
    """Create a session with explicit ambient proxy handling."""
    session = requests.Session()
    session.trust_env = trust_env
    return session


def post_with_i2i_retry(session, url, *, headers, **kwargs):
    """POST with bounded retry for reference-image calls."""
    kwargs.setdefault("timeout", I2I_TIMEOUT)
    last_exc = None
    response = None
    for attempt in range(1, I2I_MAX_ATTEMPTS + 1):
        reason = None
        try:
            response = session.post(url, headers=headers, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            reason = f"{type(exc).__name__}: {exc}"
        else:
            if response.status_code not in I2I_RETRY_STATUSES:
                return response
            last_exc = None
            reason = f"HTTP {response.status_code}"

        if attempt < I2I_MAX_ATTEMPTS:
            sleep_s = I2I_BACKOFF_SCHEDULE[attempt - 1]
            print(
                f"[image-gen] i2i retry {attempt}/{I2I_MAX_ATTEMPTS}: "
                f"{reason}; waiting {sleep_s}s",
                file=sys.stderr,
            )
            time.sleep(sleep_s)

    if last_exc is not None:
        raise last_exc
    if response is None:
        raise ResponseError("Image-to-image request failed without a response")
    return response


def load_api_key() -> tuple[str, str]:
    env_order = (
        "OMNIMAAS_API_KEY",
        "PRODUCT_SHOTS_IMAGEGEN_API_KEY",
        "RENDER_API_KEY",
        "CANVASFLOW_IMAGEGEN_API_KEY",
    )
    for env_name in env_order:
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip(), env_name
    for path in (API_KEY_PATH, COMPAT_API_KEY_PATH, LEGACY_API_KEY_PATH):
        if path.is_file() and path.read_text().strip():
            return path.read_text().strip(), str(path)
    raise ConfigurationError(
        "No API key configured for optional API mode. Set OMNIMAAS_API_KEY "
        "or PRODUCT_SHOTS_IMAGEGEN_API_KEY. Codex users should use the "
        "built-in imagegen workflow instead."
    )


def load_base_url() -> tuple[str, str]:
    env_order = (
        "OMNIMAAS_BASE_URL",
        "PRODUCT_SHOTS_IMAGEGEN_BASE_URL",
        "RENDER_BASE_URL",
        "CANVASFLOW_IMAGEGEN_BASE_URL",
    )
    for env_name in env_order:
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip().rstrip("/"), env_name
    if os.environ.get("OMNIMAAS_API_KEY"):
        return OMNIMAAS_DEFAULT_BASE_URL, "OMNIMAAS_DEFAULT_BASE_URL"
    raise ConfigurationError(
        "No API base URL configured. Set PRODUCT_SHOTS_IMAGEGEN_BASE_URL, "
        "or use OMNIMAAS_API_KEY with its default gateway URL."
    )


def model_family(model: str) -> str:
    if model in OPENAI_MODELS:
        return "openai"
    if model in GEMINI_MODELS:
        return "gemini"
    supported = sorted(OPENAI_MODELS | GEMINI_MODELS)
    raise ArgumentError(f"Unknown model {model!r}. Supported models: {supported}")


def inspect_image(path: Path) -> dict:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image_format = image.format
            width, height = image.size
            mode = image.mode
    except (OSError, UnidentifiedImageError) as exc:
        raise ArgumentError(f"Invalid reference image {path}: {exc}") from exc
    if image_format not in SUPPORTED_REFERENCE_FORMATS:
        raise ArgumentError(
            f"Unsupported reference image format for {path}: {image_format}. "
            f"Use JPEG, PNG, or WebP."
        )
    return {
        "format": image_format,
        "mime": FORMAT_TO_MIME[image_format],
        "width": width,
        "height": height,
        "mode": mode,
    }


def validate_args(args):
    args.prompt = args.prompt.strip()
    if not args.prompt:
        raise ArgumentError("Prompt must not be empty")
    if len(args.prompt) > MAX_PROMPT_CHARS:
        raise ArgumentError(
            f"Prompt is {len(args.prompt)} characters; maximum is {MAX_PROMPT_CHARS}"
        )
    if args.n < 1:
        raise ArgumentError("--n must be at least 1")
    if args.aspect_ratio and args.aspect_ratio not in ASPECT_RATIOS:
        raise ArgumentError(f"Unsupported aspect ratio: {args.aspect_ratio}")

    family = model_family(args.model)
    if family == "gemini":
        if args.n != 1:
            raise ArgumentError("Gemini API mode supports exactly one image per call")
        if args.size:
            raise ArgumentError("--size is only valid for OpenAI-family API mode")
        args.effective_size = None
        max_references = 9
    else:
        args.effective_size = (
            args.size
            or OPENAI_SIZE_BY_RATIO.get(args.aspect_ratio)
            or "1024x1024"
        )
        allowed_sizes = OPENAI_SIZES_BY_MODEL[args.model]
        if args.effective_size not in allowed_sizes:
            raise ArgumentError(
                f"Unsupported size {args.effective_size!r} for {args.model}. "
                f"Supported sizes: {sorted(allowed_sizes)}"
            )
        if args.model == "dall-e-3" and args.n != 1:
            raise ArgumentError("dall-e-3 supports exactly one image per call")
        if args.model == "dall-e-3" and args.reference_image:
            raise ArgumentError("dall-e-3 does not support reference-image edits")
        max_references = 16

    if len(args.reference_image) > max_references:
        raise ArgumentError(
            f"{args.model} accepts at most {max_references} reference images"
        )

    args.reference_paths = []
    for raw_path in args.reference_image:
        path = Path(raw_path).expanduser()
        if not path.is_file():
            raise ArgumentError(f"Reference image not found: {path}")
        inspect_image(path)
        args.reference_paths.append(path)

    args.family = family
    return args


def maybe_resize(path: Path) -> tuple[Path, bool]:
    """Return a gateway-safe reference and whether it needs cleanup."""
    info = inspect_image(path)
    if (
        path.stat().st_size <= REF_MAX_BYTES
        and max(info["width"], info["height"]) <= REF_MAX_DIM
    ):
        return path, False

    with Image.open(path) as source:
        image = source.copy()
    image.thumbnail((REF_MAX_DIM, REF_MAX_DIM), Image.Resampling.LANCZOS)

    has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
    suffix = ".webp" if has_alpha else ".jpg"
    image_format = "WEBP" if has_alpha else "JPEG"
    if not has_alpha:
        image = image.convert("RGB")

    temp_file = tempfile.NamedTemporaryFile(
        prefix="product-shots-ref-", suffix=suffix, delete=False
    )
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        quality = 88
        for _ in range(6):
            image.save(temp_path, image_format, quality=quality, method=6)
            if temp_path.stat().st_size <= REF_MAX_BYTES:
                break
            quality -= 10
            if quality < 48:
                new_size = (
                    max(1, int(image.width * 0.85)),
                    max(1, int(image.height * 0.85)),
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                quality = 78
        if temp_path.stat().st_size > REF_MAX_BYTES:
            raise ArgumentError(
                f"Could not reduce reference image below {REF_MAX_BYTES} bytes: {path}"
            )
        inspect_image(temp_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    print(
        f"[image-gen] resized {path.name}: {path.stat().st_size // 1024}KB -> "
        f"{temp_path.stat().st_size // 1024}KB, {image.width}x{image.height}"
    )
    return temp_path, True


def encode_data_url(path: Path) -> str:
    info = inspect_image(path)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{info['mime']};base64,{encoded}"


def compose_prompt(prompt: str, negative: str | None, aspect: str | None, family: str) -> str:
    parts = [prompt]
    if aspect and family == "gemini":
        parts.append(f"(requested aspect ratio: {aspect})")
    if negative:
        parts.append(f"Avoid: {negative.strip()}")
    return " ".join(parts)


def parse_json_response(response, provider: str) -> dict:
    try:
        body = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise ResponseError(
            f"{provider} returned invalid JSON: {response.text[:300]}"
        ) from exc
    if not isinstance(body, dict):
        raise ResponseError(f"{provider} response must be a JSON object")
    return body


def decode_base64_image(value: str, provider: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ResponseError(f"{provider} returned invalid base64 image data") from exc


def generate_openai(session, prompt, model, size, n, ref_images, api_key, base_url):
    headers = {"Authorization": f"Bearer {api_key}"}
    if ref_images:
        response = post_with_i2i_retry(
            session,
            f"{base_url}/images/edits",
            headers=headers,
            data={"model": model, "prompt": prompt, "n": str(n), "size": size},
            files=[
                ("image[]", (path.name, path.read_bytes(), inspect_image(path)["mime"]))
                for path in ref_images
            ],
        )
    else:
        response = session.post(
            f"{base_url}/images/generations",
            headers=headers,
            json={"model": model, "prompt": prompt, "n": n, "size": size},
            timeout=TIMEOUT,
        )

    if response.status_code != 200:
        raise ResponseError(f"OpenAI API error {response.status_code}: {response.text[:600]}")

    body = parse_json_response(response, "OpenAI")
    entries = body.get("data")
    if not isinstance(entries, list) or len(entries) != n:
        actual = len(entries) if isinstance(entries, list) else "invalid"
        raise ResponseError(f"OpenAI returned {actual} images; expected {n}")

    images = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ResponseError(f"OpenAI image entry {index} is not an object")
        if isinstance(entry.get("b64_json"), str):
            images.append(decode_base64_image(entry["b64_json"], "OpenAI"))
        elif isinstance(entry.get("url"), str):
            image_response = session.get(entry["url"], timeout=TIMEOUT)
            image_response.raise_for_status()
            images.append(image_response.content)
        else:
            raise ResponseError(
                f"OpenAI image entry {index} is missing b64_json or url"
            )
    return images, body.get("usage", {})


def generate_gemini(session, prompt, model, ref_images, api_key, base_url):
    content = [{"type": "text", "text": prompt}]
    content.extend(
        {"type": "image_url", "image_url": {"url": encode_data_url(path)}}
        for path in ref_images
    )
    payload = {"model": model, "messages": [{"role": "user", "content": content}]}
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/chat/completions"
    if ref_images:
        response = post_with_i2i_retry(
            session, url, headers=headers, json=payload
        )
    else:
        response = session.post(
            url, headers=headers, json=payload, timeout=TIMEOUT
        )
    if response.status_code != 200:
        raise ResponseError(f"Gemini API error {response.status_code}: {response.text[:600]}")

    body = parse_json_response(response, "Gemini")
    try:
        message = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ResponseError("Gemini response is missing choices[0].message.content") from exc
    if not isinstance(message, str):
        raise ResponseError("Gemini message content must be a string")
    match = re.search(
        r"data:image/(?:jpeg|jpg|png|webp);base64,([A-Za-z0-9+/=]+)",
        message,
    )
    if not match:
        raise ResponseError(
            f"Gemini response contained no supported image data: {message[:300]}"
        )
    return [decode_base64_image(match.group(1), "Gemini")], body.get("usage", {})


def inspect_image_bytes(data: bytes) -> dict:
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image_format = image.format
            width, height = image.size
            mode = image.mode
    except (OSError, UnidentifiedImageError) as exc:
        raise ResponseError(f"Generated payload is not a valid image: {exc}") from exc
    if image_format not in FORMAT_TO_SUFFIX:
        raise ResponseError(f"Unsupported generated image format: {image_format}")
    return {"format": image_format, "width": width, "height": height, "mode": mode}


def derive_output_paths(requested: str | None, formats: list[str]) -> list[Path]:
    timestamp = int(time.time())
    requested_path = Path(requested).expanduser() if requested else Path(f"output-{timestamp}")
    base = requested_path.with_suffix("") if requested_path.suffix else requested_path
    paths = []
    for index, image_format in enumerate(formats, start=1):
        numbered = f"-{index:02d}" if len(formats) > 1 else ""
        paths.append(base.with_name(base.name + numbered).with_suffix(FORMAT_TO_SUFFIX[image_format]))
    return paths


def find_preflight_conflicts(args) -> list[str]:
    candidates = []
    if args.output:
        requested_path = Path(args.output).expanduser()
        base = requested_path.with_suffix("") if requested_path.suffix else requested_path
        count = args.n if args.family == "openai" else 1
        for index in range(1, count + 1):
            numbered = f"-{index:02d}" if count > 1 else ""
            stem = base.with_name(base.name + numbered)
            candidates.extend(stem.with_suffix(suffix) for suffix in FORMAT_TO_SUFFIX.values())
    if args.manifest:
        candidates.append(Path(args.manifest).expanduser())
    return sorted({str(path) for path in candidates if path.exists()})


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(data)
    try:
        temp_path.replace(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def write_manifest(path: Path, *, args, outputs, output_info, elapsed, usage) -> None:
    manifest_parent = path.parent.resolve()

    def portable_path(output: Path) -> str:
        resolved = output.resolve()
        try:
            return str(resolved.relative_to(manifest_parent))
        except ValueError:
            return str(resolved)

    manifest = {
        "schema_version": 1,
        "workflow": "product-shots-image-gen",
        "mode": "api",
        "status": "complete",
        "model": args.model,
        "requested_aspect_ratio": args.aspect_ratio,
        "requested_size": args.effective_size,
        "prompt": args.prompt,
        "prompt_sha256": hashlib.sha256(args.prompt.encode("utf-8")).hexdigest(),
        "references": [str(path) for path in args.reference_paths],
        "elapsed_seconds": round(elapsed, 3),
        "usage": usage,
        "artifacts": [
            {
                "slot": f"variant-{index:02d}",
                "status": "complete",
                "path": portable_path(output),
                "prompt": args.prompt,
                **info,
            }
            for index, (output, info) in enumerate(zip(outputs, output_info), start=1)
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optional product-shots API image generator (OpenAI/Gemini gateways)"
    )
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--aspect-ratio", choices=sorted(ASPECT_RATIOS))
    parser.add_argument("--size", help="OpenAI only; must be supported by the selected model")
    parser.add_argument("--negative-prompt")
    parser.add_argument("--n", type=int, default=1, help="OpenAI variants for one prompt")
    parser.add_argument("--reference-image", action="append", default=[], metavar="PATH")
    parser.add_argument("--output", help="Output stem; real image format determines suffix")
    parser.add_argument("--manifest", help="Optional JSON manifest output path")
    parser.add_argument(
        "--overwrite", action="store_true", help="Allow replacing existing outputs"
    )
    parser.add_argument(
        "--trust-env",
        action="store_true",
        help="Honor HTTP(S)_PROXY and other requests environment settings",
    )
    parser.add_argument(
        "--log-prompt",
        action="store_true",
        help="Print the first 120 prompt characters (off by default)",
    )
    return parser


def run(args, *, session=None) -> list[Path]:
    args = validate_args(args)
    conflicts = find_preflight_conflicts(args)
    if conflicts and not args.overwrite:
        raise ArgumentError(
            f"Refusing to overwrite existing outputs: {conflicts}. Use --overwrite."
        )
    api_key, key_source = load_api_key()
    base_url, url_source = load_base_url()
    session = session or make_http_session(trust_env=args.trust_env)

    resized_paths = []
    ref_paths = []
    try:
        for reference_path in args.reference_paths:
            processed, temporary = maybe_resize(reference_path)
            ref_paths.append(processed)
            if temporary:
                resized_paths.append(processed)

        final_prompt = compose_prompt(
            args.prompt, args.negative_prompt, args.aspect_ratio, args.family
        )
        print(
            f"[image-gen] mode=api gateway={url_source} key_source={key_source} "
            f"model={args.model} family={args.family} refs={len(ref_paths)}"
        )
        if args.log_prompt:
            print(f"[image-gen] prompt={final_prompt[:120]!r}")

        started = time.time()
        if args.family == "openai":
            image_bytes, usage = generate_openai(
                session,
                final_prompt,
                args.model,
                args.effective_size,
                args.n,
                ref_paths,
                api_key,
                base_url,
            )
        else:
            image_bytes, usage = generate_gemini(
                session,
                final_prompt,
                args.model,
                ref_paths,
                api_key,
                base_url,
            )
        elapsed = time.time() - started

        output_info = [inspect_image_bytes(data) for data in image_bytes]
        outputs = derive_output_paths(
            args.output, [info["format"] for info in output_info]
        )
        protected_paths = outputs + (
            [Path(args.manifest).expanduser()] if args.manifest else []
        )
        existing = [str(path) for path in protected_paths if path.exists()]
        if existing and not args.overwrite:
            raise ArgumentError(
                f"Refusing to overwrite existing outputs: {existing}. Use --overwrite."
            )
        for output, data in zip(outputs, image_bytes):
            write_bytes_atomic(output, data)

        if args.manifest:
            write_manifest(
                Path(args.manifest).expanduser(),
                args=args,
                outputs=outputs,
                output_info=output_info,
                elapsed=elapsed,
                usage=usage,
            )

        total_bytes = sum(len(data) for data in image_bytes)
        print(
            f"[image-gen] OK {elapsed:.1f}s | images={len(outputs)} | "
            f"bytes={total_bytes:,} | tokens={usage.get('total_tokens', '?')}"
        )
        for output in outputs:
            print(output)
        return outputs
    finally:
        for path in resized_paths:
            path.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except (ImageGenError, requests.RequestException, OSError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    main()
