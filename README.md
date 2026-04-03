# playte

A battery-friendly photo frame for the [Inkplate10][ip] using [MicroPython][mp].

Displays images from an SD card with configurable intervals and ordering. Uses deep sleep between updates for long battery life.

[ip]: https://soldered.com/product/soldered-inkplate-10-9-7-e-paper-board-with-enclosure-copy/
[mp]: https://github.com/SolderedElectronics/Inkplate-micropython

## Features

- Displays PNG images from SD card
- Sequential or shuffle ordering
- Configurable update interval
- Deep sleep between updates for battery efficiency
- Automatic letterboxing for different aspect ratios
- Portrait images are rotated to fit the display

## Setup

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), or use the nix flake with `nix develop`.

Then install Python dependencies:

```sh
uv sync
```

### Linux: serial port access

Add your user to the `dialout` group. You may need to log out and back in for the change to take effect.

### Flash MicroPython firmware

Download the firmware (click "Download raw file"):
https://github.com/SolderedElectronics/Inkplate-micropython/blob/master/Inkplate-firmware.bin

Find your serial port (typically `/dev/ttyUSB0`):

```sh
ls /dev/ttyUSB*
```

Flash the firmware:

```sh
uv run esptool --port /dev/ttyUSB0 erase_flash
uv run esptool --port /dev/ttyUSB0 --baud 460800 write_flash --flash_mode dio 0x1000 Inkplate-firmware.bin
```

Install the Inkplate10 drivers:

```sh
uv run mpremote connect /dev/ttyUSB0 mip install github:SolderedElectronics/Inkplate-micropython/Inkplate10
```

## Preparing images

Use the included script to resize and convert images for the Inkplate display:

```sh
uv run python scripts/prepare_images.py photos/ sd/img/
```

This will:
- Resize images to fit 1200x825 (or 825x1200 for portraits)
- Convert to 4-level grayscale (matching the Inkplate's 2-bit mode)
- Add letterboxing if needed
- Output as PNG

For smoother gradients, enable dithering:

```sh
uv run python scripts/prepare_images.py photos/ sd/img/ --dither
```

## SD card setup

Format a microSD card as FAT32 and create this structure:

```
/
├── config.json
└── img/
    ├── photo1.png
    ├── photo2.png
    └── ...
```

See `sd/config.json` for an example configuration:

```json
{
  "interval_minutes": 60,
  "order": "sequential"
}
```

Options:
- `interval_minutes`: Time between image changes (default: 60)
- `order`: `"sequential"` (alphabetical) or `"shuffle"` (random)

## Deploy to device

Copy the code to your Inkplate:

```sh
uv run mpremote connect /dev/ttyUSB0 cp src/main.py :main.py
uv run mpremote connect /dev/ttyUSB0 cp src/config.py :config.py
```

Insert the SD card and reset the device. The photo frame will start automatically.

## Development

### Run without deploying

```sh
uv run mpremote connect /dev/ttyUSB0 run src/main.py
```

### Access REPL

```sh
uv run mpremote connect /dev/ttyUSB0 repl
```
