# playte

A photo frame app for the [Inkplate10][ip] using [MicroPython][mp].

[ip]: https://soldered.com/product/soldered-inkplate-10-9-7-e-paper-board-with-enclosure-copy/
[mp]: https://github.com/SolderedElectronics/Inkplate-micropython

## Setup

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), or use 
the nix flake and `nix develop`.

Then use `uv sync` to install Python dependencies:

### Linux: serial port access

Add your user to the `dialout` group.

You may need to log out and back in for the change to take effect.

## Flashing MicroPython firmware

Download the firmware (click "Download raw file" button):
https://github.com/SolderedElectronics/Inkplate-micropython/blob/master/Inkplate-firmware.bin

Find your serial port (typically `/dev/ttyUSB0`):

```sh
ls /dev/ttyUSB*
```

Flash the firmware:

```sh
uv run esptool --port /dev/ttyUSB0 erase-flash
uv run esptool --port /dev/ttyUSB0 --baud 460800 write-flash --flash-mode dio 0x1000 Inkplate-firmware.bin
```

Install the Inkplate10 drivers:

```sh
uv run mpremote connect /dev/ttyUSB0 mip install github:SolderedElectronics/Inkplate-micropython/Inkplate10
```

## Development

### Run a script (without deploying)

```sh
uv run mpremote connect /dev/ttyUSB0 run src/main.py
```

### Deploy to device

Copy `main.py` to the device root. It will run automatically on boot:

```sh
uv run mpremote connect /dev/ttyUSB0 cp src/main.py :main.py
```

### Access REPL

```sh
uv run mpremote connect /dev/ttyUSB0 repl
```
