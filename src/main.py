# MicroPython entry point for Inkplate10
# This file runs automatically when the device boots

from inkplate10 import Inkplate

display = Inkplate(Inkplate.INKPLATE_1BIT)
display.begin()
display.clearDisplay()

# Draw "playte" text
display.setTextSize(5)
display.printText(100, 400, "playte")

display.display()
print("playte initialized")
