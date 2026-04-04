#!/usr/bin/env python3
"""
Prepare images for the playte photo frame.

Resizes images to fit 1200x825 (Inkplate10 resolution), converts to 2-bit
grayscale (4 levels), and saves as PNG for precise pixel control.

Usage:
    python scripts/prepare_images.py input_dir output_dir
    python scripts/prepare_images.py photo.jpg output_dir
    python scripts/prepare_images.py input_dir output_dir --dither
"""

import argparse
import sys
from pathlib import Path
from statistics import quantiles

from PIL import Image, ImageOps

# Inkplate10 display dimensions
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 825

# 2-bit grayscale levels (4 shades)
GRAYSCALE_LEVELS = [0, 85, 170, 255]

# Supported input formats
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


PALETTE = Image.new("P", (1, 1))
PALETTE.putpalette([0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255])


def process(input: Path, output: Path, dither: bool = False):
    """Process an image.

    1. Remove any exif transpose and rotate the underlaying image.
    2. Resize the image and pad it out to the resolution of the inkplate.
    3. Quantize (and dither if selected) the image to our 4-colour grayscale.
    4. Save the image as an RGB PNG.
    """

    mode = Image.Dither.NONE
    if dither:
        mode = Image.Dither.FLOYDSTEINBERG

    with Image.open(input) as img:
        img = ImageOps.exif_transpose(img)
        img = ImageOps.pad(
            img,
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            method=Image.Resampling.LANCZOS,
            color=min(GRAYSCALE_LEVELS),
            centering=(0.5, 0.5),
        )
        img = img.quantize(colors=4, palette=PALETTE, dither=mode)
        img = img.convert("RGB")
        img.save(output, "PNG", optimize=True)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare images for playte photo frame",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s photos/ sd/img/
    %(prog)s vacation.jpg sd/img/
    %(prog)s photos/ sd/img/ --dither
        """,
    )
    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument("output", help="Output directory")
    parser.add_argument(
        "--dither",
        action="store_true",
        help="Apply Floyd-Steinberg dithering for smoother gradients",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        print(f"Error: Input path does not exist: {in_path}")
        sys.exit(1)

    images = []
    if in_path.is_file() and in_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        images.append(in_path)
    else:
        for path, name, files in in_path.walk():
            for f in files:
                f = Path(path, f)
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                    images.append(f)

    if not images:
        print("No supported image files found.")
        sys.exit(1)

    print(f"Processing {len(images)} image(s).")
    print(f"Output directory: {out_path}")

    successes = 0
    for file in images:
        out = out_path / (file.stem + ".png")
        print(f"Processing: {file.name}")
        try:
            process(file, out, dither=args.dither)
            successes += 1
        except Exception as e:
            print(f"Error: Failed to process {out}: {e}")

    print(f"Processed {successes} of {len(images)} images successfully.")


if __name__ == "__main__":
    main()
