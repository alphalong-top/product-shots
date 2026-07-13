#!/usr/bin/env python3
"""Validate generated image files and product-shots manifests."""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError


FORMAT_SUFFIXES = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "WEBP": {".webp"},
    "BMP": {".bmp"},
}


def parse_ratio(value: str) -> float:
    try:
        width, height = value.split(":", 1)
        ratio = float(width) / float(height)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError(f"Invalid ratio {value!r}; expected W:H") from exc
    if ratio <= 0:
        raise argparse.ArgumentTypeError("Aspect ratio must be positive")
    return ratio


def border_white_fraction(image: Image.Image, border_fraction: float = 0.01) -> float:
    rgb = image.convert("RGB")
    border = max(1, round(min(rgb.size) * border_fraction))
    width, height = rgb.size
    white = 0
    sampled = 0
    pixels = rgb.load()
    for y in range(height):
        for x in range(width):
            if x < border or x >= width - border or y < border or y >= height - border:
                sampled += 1
                if all(channel >= 250 for channel in pixels[x, y]):
                    white += 1
    return white / sampled if sampled else 0.0


def white_background_occupancy(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    mask = Image.new("1", rgb.size)
    mask.putdata(
        [
            0 if all(channel >= 245 for channel in pixel) else 1
            for pixel in rgb.get_flattened_data()
        ]
    )
    bbox = mask.getbbox()
    if bbox is None:
        return {
            "bounding_box": None,
            "width_fraction": 0.0,
            "height_fraction": 0.0,
            "max_dimension_fraction": 0.0,
        }
    left, top, right, bottom = bbox
    width_fraction = (right - left) / rgb.width
    height_fraction = (bottom - top) / rgb.height
    return {
        "bounding_box": [left, top, right, bottom],
        "width_fraction": round(width_fraction, 4),
        "height_fraction": round(height_fraction, 4),
        "max_dimension_fraction": round(max(width_fraction, height_fraction), 4),
    }


def validate_image(
    path: Path,
    *,
    expected_ratio: float | None = None,
    ratio_tolerance: float = 0.02,
    require_white_border: bool = False,
    min_white_fraction: float = 0.98,
    min_occupancy: float | None = None,
    max_bytes: int | None = None,
) -> dict:
    result = {"path": str(path), "errors": [], "warnings": []}
    if not path.is_file():
        result["errors"].append("file does not exist")
        return result

    try:
        with Image.open(path) as opened:
            opened.verify()
        with Image.open(path) as opened:
            image = opened.copy()
            image_format = opened.format
    except (OSError, UnidentifiedImageError) as exc:
        result["errors"].append(f"invalid image: {exc}")
        return result

    result.update(
        {
            "format": image_format,
            "mode": image.mode,
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 6),
        }
    )

    if max_bytes is not None and path.stat().st_size > max_bytes:
        result["errors"].append(
            f"file size {path.stat().st_size} exceeds maximum {max_bytes} bytes"
        )

    allowed_suffixes = FORMAT_SUFFIXES.get(image_format)
    if allowed_suffixes is None:
        result["errors"].append(f"unsupported image format: {image_format}")
    elif path.suffix.lower() not in allowed_suffixes:
        result["errors"].append(
            f"extension {path.suffix or '<none>'} does not match {image_format}"
        )

    if image.mode not in {"RGB", "RGBA"}:
        result["errors"].append(f"unsupported color mode: {image.mode}")
    elif image.mode == "RGBA":
        result["warnings"].append(
            "image has alpha; convert to RGB before Amazon upload"
        )

    if expected_ratio is not None:
        actual = image.width / image.height
        relative_error = abs(actual - expected_ratio) / expected_ratio
        if relative_error > ratio_tolerance:
            result["errors"].append(
                f"aspect ratio {actual:.4f} differs from expected {expected_ratio:.4f}"
            )

    if require_white_border:
        white_fraction = border_white_fraction(image)
        occupancy = white_background_occupancy(image)
        result["white_border_fraction"] = round(white_fraction, 4)
        result["occupancy_heuristic"] = occupancy
        if white_fraction < min_white_fraction:
            result["errors"].append(
                f"white border fraction {white_fraction:.3f} is below {min_white_fraction:.3f}"
            )
        if (
            min_occupancy is not None
            and occupancy["max_dimension_fraction"] < min_occupancy
        ):
            result["errors"].append(
                "non-white bounding-box occupancy "
                f"{occupancy['max_dimension_fraction']:.3f} is below {min_occupancy:.3f}"
            )

    return result


def resolve_artifact_path(manifest_path: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    relative_to_manifest = manifest_path.parent / path
    if relative_to_manifest.exists():
        return relative_to_manifest
    return path


def validate_manifest(path: Path, expected_slots: set[str]) -> tuple[dict, list[Path]]:
    result = {"path": str(path), "errors": [], "warnings": []}
    artifact_paths = []
    try:
        manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        result["errors"].append(f"invalid manifest: {exc}")
        return result, artifact_paths

    required_top_level = {"schema_version", "workflow", "mode", "status", "artifacts"}
    missing = sorted(required_top_level - set(manifest)) if isinstance(manifest, dict) else []
    if not isinstance(manifest, dict):
        result["errors"].append("manifest root must be an object")
        return result, artifact_paths
    if missing:
        result["errors"].append(f"missing top-level fields: {missing}")
    if manifest.get("status") != "complete":
        result["errors"].append("manifest status is not complete")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        result["errors"].append("artifacts must be a non-empty list")
        return result, artifact_paths

    slots = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            result["errors"].append(f"artifact {index} must be an object")
            continue
        missing_artifact = {"slot", "status", "path"} - set(artifact)
        if missing_artifact:
            result["errors"].append(
                f"artifact {index} missing fields: {sorted(missing_artifact)}"
            )
            continue
        slot = artifact["slot"]
        if not isinstance(slot, str) or not slot:
            result["errors"].append(f"artifact {index} slot must be a non-empty string")
            continue
        slots.append(slot)
        if artifact["status"] != "complete":
            result["errors"].append(f"artifact {slot!r} is not complete")
        if not artifact.get("prompt"):
            result["errors"].append(f"artifact {slot!r} has no prompt")
        if not isinstance(artifact["path"], str) or not artifact["path"]:
            result["errors"].append(f"artifact {slot!r} path must be a non-empty string")
            continue
        artifact_path = resolve_artifact_path(path, artifact["path"])
        artifact_paths.append(artifact_path)
        if not artifact_path.is_file():
            result["errors"].append(
                f"artifact {slot!r} file does not exist: {artifact_path}"
            )

    duplicate_slots = sorted({slot for slot in slots if slots.count(slot) > 1})
    if duplicate_slots:
        result["errors"].append(f"duplicate slots: {duplicate_slots}")
    missing_slots = sorted(expected_slots - set(slots))
    if missing_slots:
        result["errors"].append(f"missing expected slots: {missing_slots}")
    result["slots"] = slots
    return result, artifact_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="append", default=[], metavar="PATH")
    parser.add_argument("--manifest", metavar="PATH")
    parser.add_argument("--expected-slot", action="append", default=[])
    parser.add_argument("--expected-ratio", type=parse_ratio, metavar="W:H")
    parser.add_argument("--main-image", action="store_true")
    parser.add_argument("--min-white-border", type=float, default=0.98)
    parser.add_argument(
        "--min-occupancy",
        type=float,
        help="Optional non-white bounding-box heuristic; not an Amazon guarantee",
    )
    parser.add_argument("--report", metavar="PATH")
    parser.add_argument("--max-bytes", type=int)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if not args.image and not args.manifest:
        raise SystemExit("Provide at least one --image or --manifest")
    if not 0 <= args.min_white_border <= 1:
        raise SystemExit("--min-white-border must be between 0 and 1")
    if args.min_occupancy is not None and not 0 <= args.min_occupancy <= 1:
        raise SystemExit("--min-occupancy must be between 0 and 1")
    if args.max_bytes is not None and args.max_bytes < 1:
        raise SystemExit("--max-bytes must be positive")

    report = {"manifest": None, "images": [], "status": "pass"}
    image_paths = [Path(path).expanduser() for path in args.image]
    if args.manifest:
        manifest_result, manifest_images = validate_manifest(
            Path(args.manifest).expanduser(), set(args.expected_slot)
        )
        report["manifest"] = manifest_result
        image_paths.extend(manifest_images)

    seen = set()
    for path in image_paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        report["images"].append(
            validate_image(
                path,
                expected_ratio=args.expected_ratio,
                require_white_border=args.main_image,
                min_white_fraction=args.min_white_border,
                min_occupancy=args.min_occupancy,
                max_bytes=args.max_bytes,
            )
        )

    all_results = report["images"] + ([report["manifest"]] if report["manifest"] else [])
    if any(result["errors"] for result in all_results):
        report["status"] = "fail"
    serialized = json.dumps(report, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(serialized)
    else:
        print(serialized, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
