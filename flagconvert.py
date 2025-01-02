import os
import shutil
import sys

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

from config import Config
from logToFile import Logger

MAX_RGB = 256

def get_magick_path():
    if getattr(sys, "frozen", False):
        return os.path.join(getattr(sys, "_MEIPASS"), 'magick.exe')
    return os.path.join(os.path.dirname(__file__), "ImageMagick/magick.exe")

os.environ["MAGICK_HOME"] = get_magick_path()

def color_to_rgb_array(color):
    return [int(color.red_quantum() / MAX_RGB),
            int(color.green_quantum() / MAX_RGB),
            int(color.blue_quantum() / MAX_RGB)]


def compile_flag(sourcepath, dest_folder):

    if not dest_folder:
        dest_folder = os.path.join(Config().converter_dir, "output")
    filename = os.path.splitext(os.path.basename(sourcepath))[0]

    if not os.path.exists(sourcepath):
        Logger().log("warning", f"Could not find \"{sourcepath}\"")
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
    shutil.move(filename + ".dds", os.path.join(
        Config().converter_dir,
        "output",
        Config().get_mod_name(),
        "flags",
        "convertedflags"
    ))

    tiny = Image(dropshadow)
    tiny.type = imagetype
    tiny.resize(24, 24)
    tiny.save(filename=filename + ".dds")
    shutil.move(filename + ".dds", os.path.join(
        Config().converter_dir,
        "output",
        Config().get_mod_name(),
        "flags",
        "convertedflags",
        "small"
    ))

    image2.resize(186, 118)

    geom = Image(width=256, height=256)
    geom.composite(image2, 35, 69, 'over')
    geom.type = 'grayscale'
    if os.name == "nt":
        geom.flip()

    geom.save(filename=filename+".dds")
    shutil.move(filename + ".dds", os.path.join(
        Config().converter_dir,
        "output",
        Config().get_mod_name(),
        "flags",
        "convertedflags",
        "map"
    ))
