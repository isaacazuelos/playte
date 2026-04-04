# MicroPython entry point for Inkplate10 photo frame
# Displays images from SD card with configurable interval and ordering

import random
import time
from os import listdir

import machine
from inkplate10 import Inkplate

from config import load_config, load_state, save_state

IMG_DIR = "/sd/img"


def get_image_files() -> list[str]:
    """Get sorted list of image files in the img directory."""
    try:
        files = listdir(IMG_DIR)
    except OSError:
        return []

    image_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    image_files.sort()
    return image_files


def get_next_image(image_files, current, shuffle: bool = False) -> str | None:
    """Determine the next image to display based on config and state. If possible, it'll try to avoid showing the same image twice."""
    if not image_files:
        return None
    elif len(image_files) == 1:
        return image_files[0]
    elif shuffle:
        next_image = current
        while next_image == current:
            next_image = random.choice(image_files)
        return next_image
    elif current in image_files:
        index = image_files.index(current)
        return image_files[(index + 1) % len(image_files)]
    else:
        return image_files[0]


def deep_sleep_minutes(minutes):
    """Enter deep sleep for the specified number of minutes."""
    sleep_ms = minutes * 60 * 1000
    print(f"Entering deep sleep for {minutes} minutes...")
    machine.deepsleep(sleep_ms)


def main():
    print("playte photo frame starting...")

    # Initialize display in 2-bit grayscale mode
    display = Inkplate(Inkplate.INKPLATE_2BIT)
    display.begin()

    # Initialize SD card with fast boot
    print("Initializing SD card...")
    display.initSDCard(fastBoot=True)

    # Load configuration
    print("Loading configuration...")
    config = load_config()
    state = load_state()
    print(
        f"Config: interval={config['interval_minutes']} min, shuffle={config['shuffle']}"
    )

    # Get list of image files
    image_files = get_image_files()
    print(f"Found {len(image_files)} images")

    if not image_files:
        # No images - display message and stay awake for debugging
        display.clearDisplay()
        display.setTextSize(3)
        display.printText(100, 400, "No images found in /sd/img/")
        display.display()
        print("No images found - staying awake for debugging")
        return

    image_file = get_next_image(
        image_files,
        state["current_image"],
        shuffle=config["shuffle"],
    )

    image_path = f"{IMG_DIR}/{image_file}"
    print(f"Displaying: {image_file}")

    # Clear display and draw image
    display.clearDisplay()

    start_time = time.ticks_ms()
    display.drawImage(image_path, 0, 0)
    draw_time = time.ticks_ms() - start_time
    print(f"Draw time: {draw_time}ms")

    # Update display
    display.display()

    # Save state before we go to sleep
    state["current_image"] = image_file
    save_state(state)

    # Put SD card to sleep
    display.SDCardSleep()

    # Deep sleep until next image change
    deep_sleep_minutes(config["interval_minutes"])


if __name__ == "__main__":
    main()
