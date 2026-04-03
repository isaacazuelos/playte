# MicroPython entry point for Inkplate10 photo frame
# Displays images from SD card with configurable interval and ordering

import time
from os import listdir

import machine
from inkplate10 import Inkplate

from config import load_config, load_state, save_state

# Display dimensions
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 825

IMG_DIR = "/sd/img"


def get_image_files():
    """Get sorted list of image files in the img directory."""
    try:
        files = listdir(IMG_DIR)
    except OSError:
        return []

    image_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    image_files.sort()
    return image_files


def shuffle_list(items):
    """Simple Fisher-Yates shuffle using hardware RNG."""
    import urandom

    result = list(items)
    for i in range(len(result) - 1, 0, -1):
        j = urandom.getrandbits(16) % (i + 1)
        result[i], result[j] = result[j], result[i]
    return result


def get_next_image(config, state, image_files):
    """
    Determine the next image to display based on config and state.
    Returns (image_filename, new_state).
    """
    if not image_files:
        return None, state

    order = config.get("order", "sequential")

    if order == "shuffle":
        # Shuffle mode: use shuffled order from state, reshuffle when exhausted
        if state is None or "shuffled_order" not in state:
            # First run or corrupted state - create new shuffle
            shuffled = shuffle_list(image_files)
            state = {"index": 0, "shuffled_order": shuffled}
        else:
            # Check if files changed (added/removed)
            current_set = set(image_files)
            state_set = set(state["shuffled_order"])

            if current_set != state_set:
                # Files changed - reshuffle
                shuffled = shuffle_list(image_files)
                state = {"index": 0, "shuffled_order": shuffled}

        index = state.get("index", 0)
        shuffled_order = state["shuffled_order"]

        if index >= len(shuffled_order):
            # Exhausted current shuffle - reshuffle
            shuffled_order = shuffle_list(image_files)
            index = 0
            state = {"index": 0, "shuffled_order": shuffled_order}

        image = shuffled_order[index]
        state["index"] = index + 1

    else:
        # Sequential mode: alphabetical order
        if state is None:
            state = {"index": 0}

        index = state.get("index", 0)

        # Handle case where files were removed
        if index >= len(image_files):
            index = 0

        image = image_files[index]
        state["index"] = (index + 1) % len(image_files)
        # Remove shuffle state if switching from shuffle to sequential
        if "shuffled_order" in state:
            del state["shuffled_order"]

    return image, state


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
    print(f"Config: interval={config['interval_minutes']}min, order={config['order']}")

    # Load state
    state = load_state()

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

    # Get next image
    image_file, new_state = get_next_image(config, state, image_files)

    if image_file:
        image_path = f"{IMG_DIR}/{image_file}"
        print(f"Displaying: {image_file}")

        # Clear display and draw image
        display.clearDisplay()

        start_time = time.ticks_ms()
        display.drawImage(
            image_path,
            0,
            0,
            invert=False,
            dither=True,
            kernel_type=Inkplate.KERNEL_FLOYD_STEINBERG,
        )
        draw_time = time.ticks_ms() - start_time
        print(f"Draw time: {draw_time}ms")

        # Update display
        display.display()

        # Save state
        save_state(new_state)
        print(f"State saved: index={new_state.get('index', 0)}")

    # Put SD card to sleep
    display.SDCardSleep()

    # Deep sleep until next image change
    deep_sleep_minutes(config["interval_minutes"])


if __name__ == "__main__":
    main()
