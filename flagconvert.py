#!/usr/bin/python

# This entire script is a mess for now, but it works ok, at least.

import os
import sys
import math
import numpy
import shutil

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

MaxRGB = 256


def colorToRGBArray(color):
    return [int(color.red_quantum() / MaxRGB),
            int(color.green_quantum() / MaxRGB),
            int(color.blue_quantum() / MaxRGB)]


# def colorSet(image):
#     colorset = {}
#     for x in range(image.width):
#         for y in range(image.height):
#             color = (image[x, y].string)
#             color.removeprefix("srgb(")
#             if color not in colorset:
#                 colorset[color] = 1
#             else:
#                 colorset[color] += 1
#     return colorset


def CompileFlag(sourcepath, destFolder):

    if not destFolder:
        destFolder = "output/"
    filename = os.path.splitext(os.path.basename(sourcepath))[0]

    if not os.path.exists(sourcepath):
        print("WARNING: Could not find \"" + sourcepath + "\".")
        return

    image = Image(filename=sourcepath)
    imagetype = image.type

    nonecolor = Color('rgba(256, 0, 0, 0)')
    canvas = Image(width=128, height=128, background=nonecolor)
    canvas.type = imagetype

    dropshadow = Image(width=128, height=128, background=nonecolor)
    dropshadow.type = imagetype

    image = Image(filename=sourcepath)
    image2 = image
    image.resize(115, 73)

    dropshadow.colorize(Color('rgba(0, 0, 0, 0)'), 'rgba(0, 0, 0, 1')
    with dropshadow as img:
        with Drawing() as draw:
            draw.rectangle(left=5.5, top=26.5, height=122.5, width=101.5)
            draw(img)
            img.blur(5, 5)
            img.composite(image, operator='over')

    geom = Image(width=128, height=128)
    geom.composite(image, 7, 28, 'over')
    if os.name == "nt":
        geom.flip()
    dropshadow = geom
    dropshadow.type = imagetype

    dropshadow.save(filename=filename + ".dds")
    shutil.move(filename + ".dds", os.path.join(os.getcwd(),
                "outputMod/flags/convertedflags/"))

    tiny = Image(dropshadow)
    tiny.type = imagetype
    tiny.resize(24, 24)
    tiny.save(filename=filename + ".dds")
    shutil.move(filename + ".dds", os.path.join(os.getcwd(),
                "outputMod/flags/convertedflags/small/"))

    #mapflag = Image(Drawing(256, 256), nonecolor)

    # colorFrequencies = colorSet(image2)
    # sortedcolors = [(k, colorFrequencies[k]) for k in sorted(
    #     colorFrequencies, key=colorFrequencies.get, reverse=True)]

    ### Commented out temporarily until I can figure out how to get it to work via wand. ###

    # maxIntensity = 0
    # minIntensity = 255
    # for i in range(10):
    #     if i >= len(sortedcolors):
    #         break
    #     sortedcolor = sortedcolors[i][0][1:-1].split(',')
    #     intensity = int(sortedcolor[0]) + int(1.2 * float(sortedcolor[1])) + \
    #         int(0.5 * float(sortedcolor[2]))

    #     if intensity > maxIntensity:
    #         maxIntensity = intensity
    #     if intensity < minIntensity:
    #         minIntensity = intensity

    # for x in range(image2.width):
    #     for y in range(image2.height):
    #         c = colorToRGBArray(image2.pixelColor(x, y))
    #         intensity = c[0] + (1.2 * float(c[1])) + (0.5 * float(c[2]))
    #         actualIntensity = (intensity - minIntensity) / (maxIntensity - minIntensity)
    #         if (actualIntensity < 0.0):
    #             actualIntensity = 0
    #         elif (actualIntensity > 1.0):
    #             actualIntensity = 255 * MaxRGB
    #         else:
    #             actualIntensity = int(actualIntensity * 255 * MaxRGB)
    #         newcolor = Color(min(actualIntensity + MaxRGB, 255 * MaxRGB), actualIntensity, actualIntensity, 1 * MaxRGB)
    #         image2.pixelColor(x, y, newcolor)

    image2.resize(186, 118)

    # dropshadow2 = Image(Drawing(256, 256), nonecolor)
    # dropshadow2.type = imagetype
    # dropshadow2.fillColor(Color('rgba(0, 0, 0, 6400'))
    # dropshadow2.draw(wand.DrawableRectangle((256 / 2) - (186 / 2) - 1, (256 / 2) - (118 / 2) - 1,
    #                                                 (256 / 2) + (186 / 2) + 1, (256 / 2) + (118 / 2) + 1))
    # dropshadow2.blur(10, 10)

    geom = Image(width=256, height=256)
    geom.composite(image2, 35, 69, 'over')
    geom.type = 'grayscale'
    if os.name == "nt":
        geom.flip()
    # dropshadow2 = geom
    # dropshadow2.type = imagetype

    # dropshadow2.fillColor(Color('rgba(0, 0, 0, 1)'))
    # dropshadow2.strokeColor(Color('rgba(255, 255, 255, 0'))
    # dropshadow2.strokeWidth(2)
    # dropshadow2.draw(wand.DrawableRectangle((256 / 2) - (186 / 2) - 1, (256 / 2) - (118 / 2) - 1,
    #                                                 (256 / 2) + (186 / 2) + 1, (256 / 2) + (118 / 2) + 1))'

    geom.save(filename=filename+".dds")
    shutil.move(filename + ".dds", os.path.join(os.getcwd(),
                "outputMod/flags/convertedflags/map/"))


if __name__ == "__main__":
    SetUpFolders()
    for filename in os.listdir("hoi4samples"):
        CompileFlag("hoi4samples/" + filename)
