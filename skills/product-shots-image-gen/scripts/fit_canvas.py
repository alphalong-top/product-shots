#!/usr/bin/env python3
"""Fit an image to an exact canvas using contain/pad or cover/crop."""

import argparse
from pathlib import Path

from PIL import Image, ImageColor


def fit_image(image: Image.Image, width: int, height: int, mode: str, background: str):
    source = image.convert("RGB")
    if mode == "contain":
        source.thumbnail((width, height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (width, height), ImageColor.getrgb(background))
        left = (width - source.width) // 2
        top = (height - source.height) // 2
        canvas.paste(source, (left, top))
        return canvas

    scale = max(width / source.width, height / source.height)
    resized = source.resize(
        (round(source.width * scale), round(source.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--mode", choices=("contain", "cover"), default="contain")
    parser.add_argument("--background", default="#ffffff")
    args = parser.parse_args(argv)
    if args.width < 1 or args.height < 1:
        parser.error("--width and --height must be positive")

    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser()
    if not input_path.is_file():
        parser.error(f"input not found: {input_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as source:
        output = fit_image(source, args.width, args.height, args.mode, args.background)
    formats = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
        ".bmp": "BMP",
    }
    save_format = formats.get(output_path.suffix.lower())
    if save_format is None:
        parser.error("output extension must be .jpg, .jpeg, .png, .webp, or .bmp")
    output.save(output_path, save_format, quality=95, optimize=True)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
