#!/usr/bin/env python3

"""
    RGB2YIQ: RGB to YIQ Pillow-based conversion program for Python 3.x
    Copyright (C) 2025, Aura Lesse Programmer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import logging
import pathlib
import argparse

from struct import *
from PIL import Image

version = "1.3.0"


def get_writable_img_extensions():
    """ Get Pillow supported extensions.

    Based on https://stackoverflow.com/a/71114152.
    """
    exts = Image.registered_extensions()
    return [ex[1:] for ex, f in exts.items() if f in Image.SAVE]


def parse_args():
    """ Prepare the argument parser """
    parser = argparse.ArgumentParser(description="Converts an image into its YIQ equivalent.")

    parser.add_argument('imgsrc', help="Input image file to be processed", metavar='infile')
    
    parser.add_argument('-q', '--quiet', action='store_true', help="don't output operation details, only errors")
    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s\tv{version}")
    parser.add_argument('-l', '--license', nargs=0, action=show_license, help="show license information and exit")
    parser.add_argument('-e', '--extensions', nargs=0, action=show_extensions, help="show supported extensions")

    grp_out = parser.add_mutually_exclusive_group()
    grp_out.add_argument('imgdest', nargs='?', help="Output image filename, let empty to stdout", default='-', metavar='outfile')
    grp_out.add_argument('-t', '--type', choices=get_writable_img_extensions(), help="Output image type to emit to stdout")

    return parser.parse_args()


def configure_logger(quiet):
    """ Configure logger. """
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level=logging.ERROR if quiet else logging.INFO
    )


def smart_open(fname, use_stdout=False):
    """ Determine whether output should be a file or stdout """
    if use_stdout:
        return sys.stdout.buffer
    else:
        return open(fname, 'wb')


def smart_close(fp):
    """ Close output if applicable """
    if fp != sys.stdout.buffer:
        fp.close()


class show_license(argparse.Action):
    """ Define custom action that merely prints license information """

    def __call__(self, parser, namespace, values, option_string=None):
        print("RGB2YIQ: RGB to YIQ Pillow-based conversion program for Python 3.x")
        print("Copyright (C) 2025, Aura Lesse Programmer\n")
        print("This program is free software: you can redistribute it and/or modify")
        print("it under the terms of the GNU General Public License as published by")
        print("the Free Software Foundation, either version 3 of the License, or")
        print("(at your option) any later version.\n")
        print("This program is distributed in the hope that it will be useful,")
        print("but WITHOUT ANY WARRANTY; without even the implied warranty of")
        print("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
        print("GNU General Public License for more details.\n")
        print("You should have received a copy of the GNU General Public License")
        print("along with this program.  If not, see <http://www.gnu.org/licenses/>.\n")

        parser.exit()


class show_extensions(argparse.Action):
    """ Define custom action that shows supported output extensions """

    def __call__(self, parser, namespace, values, option_string=None):
        print("Supported extensions:")
        print(", ".join(get_writable_img_extensions()))

        parser.exit()


def rgb2yiq(fRGB, type):
    fR, fG, fB = fRGB

    if type == "ntsc-1953":
        fY = 0.299  * fR + 0.587  * fG + 0.114  * fB
        fI = 0.5959 * fR - 0.2746 * fG - 0.3213 * fB
        fQ = 0.2115 * fR - 0.5227 * fG + 0.3112 * fB
    elif type == "smpte-c":
        fY = 0.3   * fR + 0.59   * fG + 0.11   * fB
        fI = 0.599 * fR - 0.2773 * fG - 0.3217 * fB
        fQ = 0.213 * fR - 0.5251 * fG + 0.3121 * fB
    else:
        raise ValueError(f"Conversion method {type} not supported!")
    
    return (fY, fI, fQ)


def yiq2rgb(fYIQ, type):
    fY, fI, fQ = fYIQ

    if type == "ntsc-1953":
        fR = fY + 0.956 * fI + 0.619 * fQ
        fG = fY - 0.272 * fI - 0.647 * fQ
        fB = fY - 1.106 * fI + 1.703 * fQ
    elif type == "smpte-c":
        fR = fY + 0.9469 * fI + 0.6236 * fQ
        fG = fY - 0.2748 * fI - 0.6357 * fQ
        fB = fY - 1.1    * fI + 1.7    * fQ
    else:
        raise ValueError(f"Conversion method {type} not supported!")

    return (fR, fG, fB)


def generate_yiq_v1(img_data):
    """ Generate YIQ image, v1, given image pixels and size """

    img_pix = img_data["data"]
    img_size = img_data["size"]

    yiq_data = bytearray()

    logging.info("Writing header information...")

    yiq_data.extend("YIQ1".encode('utf-8'))
    yiq_data.extend(pack('<LL', *img_size))
    yiq_data.extend("DATA".encode('utf-8'))

    logging.info("Processing pixels...")

    for y in range(0, img_size[1]):
        for x in range(0, img_size[0]):
            fRGB = tuple(i / 255 for i in img_pix[x, y])

            fY, fI, fQ = rgb2yiq(fRGB, "smpte-c")
            yiq_t = (fY, (fI + 0.5957), (fQ + 0.5226))

            yiq_data.extend(pack('<bbb', *(round(i * 100) for i in yiq_t)))

    logging.info("Image processed!")

    return yiq_data


def write_yiq(img_converted, imgdest_props):
    """ Write YIQ file given raw file data and destination path. """
    imgdest_path = imgdest_props["path"]
    
    imgdest = smart_open(f"{imgdest_path}", imgdest_path == "-")
    imgdest.write(img_converted)
    smart_close(imgdest)


def generate_rgb_v1(img_data):
    """ Obtain RGB data and other information from YIQ file data. """

    img_pix = img_data["data"]
    img_size = img_data["size"]

    logging.info("Gathering header information...")

    rgb_data = {
        "size": img_size,
        "data": []
    }

    logging.info("Processing triplets...")

    for y in range(0, img_size[1]):
        for x in range(0, img_size[0]):
            idx = (y * img_size[0] + x) * 3

            cY = img_pix[idx] / 100.0
            cI = (img_pix[idx + 1] / 100.0) - 0.5957
            cQ = (img_pix[idx + 2] / 100.0) - 0.5226

            fR, fG, fB = yiq2rgb((cY, cI, cQ), "smpte-c")
            rgb_t = tuple(round(i * 255) for i in (fR, fG, fB))

            rgb_data["data"].append(rgb_t)

    logging.info("Image processed!")

    return rgb_data


def write_rgb(img_converted, imgdest_props):
    """ Write image file given structured RGB data and destination path. """
    imgdest = Image.new('RGB', img_converted["size"])
    imgdest.putdata(img_converted["data"])

    imgdest_path = imgdest_props["path"]
    imgdest_type = imgdest_props["type"]

    if imgdest_path == '-':
        imgdest.save(sys.stdout, imgdest_type)
    else:
        imgdest.save(imgdest_path)


def get_image_data_yiq(imgsrc):
    """ Opens the image as YIQ and extracts its properties, if possible. """

    format = None
    w, h = (0, 0)
    data = None

    try:
        with open(imgsrc, "rb") as fp:
            format = fp.read(4).decode('utf-8')
            if format != "YIQ1":
                return None

            w, h = unpack("<LL", fp.read(8))

            dmark = fp.read(4).decode('utf-8')
            if dmark != 'DATA':
                return None

            data = fp.read()
    except:
        return None

    if len(data) != (w * h) * 3:
        return None

    return {
        "path": imgsrc,
        "format": format,
        "size": (w, h),
        "data": data,
        "generate_fn": generate_rgb_v1,
        "write_fn": write_rgb
    }


def get_image_data_pillow(imgsrc):
    """ Opens the image and extracts its properties, via Pillow. """

    img = Image.open(imgsrc)

    logging.info(f"Name: {imgsrc}")
    logging.info(f"Format: {img.format}")
    logging.info(f"Size: {img.size[0]} X {img.size[1]}")
    logging.info(f"Colour model: {img.mode}\n")

    img_rgb = img if img.mode == 'RGB' else img.convert('RGB')

    return {
        "path": imgsrc,
        "format": img.format,
        "size": img.size,
        "data": img_rgb.load(),
        "generate_fn": generate_yiq_v1,
        "write_fn": write_yiq
    }


def get_image_data(imgsrc):
    """ Opens the image and extracts its properties.
    
    Supports either YIQ files or the formats supported by Pillow.
    """

    options = [
        get_image_data_yiq,
        get_image_data_pillow
    ]

    for opt in options:
        img_data = opt(imgsrc)

        if img_data is not None:
            return img_data

    return None


def process_img(img_data, imgdest_props):
    """ Process image given source data and destination. """
    img_converted = img_data["generate_fn"](img_data)
    img_data["write_fn"](img_converted, imgdest_props)


def main():
    """ Main program entrypoint """

    # Get the arguments
    args = parse_args()

    # Initialize logging facility
    configure_logger(args.quiet)

    # Determine if source image exists
    imgsrc = pathlib.Path(args.imgsrc)
    if not imgsrc.is_file():
        logging.error(f"File \"{imgsrc}\" does not exist! Aborting...")
        exit(1)
    
    # Process image with given arguments
    try:
        img_data = get_image_data(imgsrc)
        if img_data is None:
            raise TypeError("Source image could not be opened!")

        imgdest_props = {
            "path": args.imgdest,
            "type": args.type
        }

        process_img(img_data, imgdest_props)

        logging.info("Completed!")
    except Exception as e:
        logging.error("Error processing image!")
        logging.error(f"Reason: {e}")


if __name__ == "__main__":
    main()
