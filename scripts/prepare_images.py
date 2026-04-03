#!/usr/bin/env python3
"""
Prepare images for the playte photo frame.

Resizes images to fit 1200x825 (Inkplate10 resolution), converts to 2-bit
grayscale (4 levels), and saves as PNG for precise pixel control.

Usage:
    python scripts/prepare_images.py input_dir output_dir
    python scripts/prepare_images.py photo.jpg output_dir
    python scripts/prepare_images.py input_dir output_dir --dither

Requirements:
    pip install Pillow
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

# Inkplate10 display dimensions
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 825

# 2-bit grayscale levels (4 shades)
GRAYSCALE_LEVELS = [0, 85, 170, 255]

# Supported input formats
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"}


def create_grayscale_palette() -> Image.Image:
    """Create a palette image with exactly 4 grayscale levels."""
    palette_img = Image.new("P", (1, 1))
    # Build palette: 4 grayscale values, each repeated 3 times for RGB
    palette = []
    for level in GRAYSCALE_LEVELS:
        palette.extend([level, level, level])
    # Pad to 256 colors (required by PIL)
    palette.extend([0] * (768 - len(palette)))
    palette_img.putpalette(palette)
    return palette_img


def quantize_to_4_levels(img: Image.Image, dither: bool = False) -> Image.Image:
    """
    Quantize image to exactly 4 grayscale levels, output as RGB.
    Optionally apply Floyd-Steinberg dithering.
    """
    if img.mode != "L":
        img = img.convert("L")

    if dither:
        # Use Pillow's built-in dithering via quantize
        palette_img = create_grayscale_palette()
        # Convert to RGB for quantize (required by Pillow)
        rgb = img.convert("RGB")
        quantized = rgb.quantize(
            colors=4,
            palette=palette_img,
            dither=Image.Dither.FLOYDSTEINBERG
        )
        # Convert to RGB for Inkplate compatibility
        return quantized.convert("RGB")
    else:
        # Simple nearest-neighbor quantization
        def nearest_level(value):
            return min(GRAYSCALE_LEVELS, key=lambda x: abs(x - value))

        quantized = img.point(nearest_level)
        return quantized.convert("RGB")


def resize_and_letterbox(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize image to fit within target dimensions, maintaining aspect ratio.
    Adds black letterboxing if aspect ratios don't match.
    """
    img_width, img_height = img.size
    scale_w = target_width / img_width
    scale_h = target_height / img_height
    scale = min(scale_w, scale_h)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    # Resize with high-quality resampling
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create new image with black background
    result = Image.new("L", (target_width, target_height), 0)

    # Center the image
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2

    if resized.mode != "L":
        resized = resized.convert("L")
    result.paste(resized, (x, y))

    return result


def process_image(input_path: Path, output_path: Path, dither: bool = False) -> bool:
    """
    Process a single image: resize, convert to 2-bit grayscale, save as PNG.
    Returns True on success, False on failure.
    """
    try:
        with Image.open(input_path) as img:
            img = ImageOps.exif_transpose(img)

            img_width, img_height = img.size
            is_portrait = img_height > img_width

            if is_portrait:
                target_width, target_height = DISPLAY_HEIGHT, DISPLAY_WIDTH
            else:
                target_width, target_height = DISPLAY_WIDTH, DISPLAY_HEIGHT

            processed = resize_and_letterbox(img, target_width, target_height)
            processed = quantize_to_4_levels(processed, dither=dither)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            processed.save(output_path, "PNG", optimize=True)

            return True

    except Exception as e:
        print(f"  Error processing {input_path.name}: {e}")
        return False


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

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)

    if input_path.is_file():
        input_files = [input_path]
    else:
        input_files = [
            f
            for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        input_files.sort()

    if not input_files:
        print("No supported image files found.")
        sys.exit(1)

    print(f"Processing {len(input_files)} image(s)...")
    print(f"Output directory: {output_dir}")
    print(f"Target resolution: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print(f"Dithering: {'enabled' if args.dither else 'disabled'}")
    print()

    success_count = 0
    for input_file in input_files:
        output_file = output_dir / (input_file.stem + ".png")
        print(f"Processing: {input_file.name}")

        if process_image(input_file, output_file, dither=args.dither):
            size_kb = output_file.stat().st_size / 1024
            print(f"  -> {output_file.name} ({size_kb:.1f}KB)")
            success_count += 1
        print()

    print(f"Processed {success_count}/{len(input_files)} images successfully.")

    if success_count > 0:
        print(f"\nCopy {output_dir}/ to your SD card's img/ folder.")


if __name__ == "__main__":
    main()
