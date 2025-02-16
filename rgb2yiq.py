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


def parse_args():
    """ Prepare the argument parser """
    parser = argparse.ArgumentParser(description="Converts an image into its YIQ equivalent.")

    parser.add_argument('imgsrc', help="Input image file to be processed", metavar='infile')
    parser.add_argument('imgdest', nargs='?', help="Output image basename, let empty to output to stdout", default='-', metavar='outfile')
    
    parser.add_argument('-q', '--quiet', action='store_true', help="don't output operation details, only errors")
    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s\tv{version}")
    parser.add_argument('-l', '--license', nargs=0, action=show_license, help="show license information and exit")

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
            r, g, b = tuple(i / 255 for i in img_pix[x, y])

            fY = r * 0.30 + g * 0.59 + b * 0.11
            fI = r * 0.599 - g * 0.2773 - b * 0.3217
            fQ = r * 0.213 - g * 0.5251 + b * 0.3121
            
            yiq_t = (fY, (fI + 0.5957), (fQ + 0.5226))

            yiq_data.extend(pack('<bbb', *(round(i * 100) for i in yiq_t)))

    logging.info("Image processed!")

    return yiq_data


def write_yiq(img_converted, imgdest_path):
    """ Write YIQ file given raw file data and destination path. """
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

            cy = img_pix[idx] / 100.0
            ci = (img_pix[idx + 1] / 100.0) - 0.5957
            cq = (img_pix[idx + 2] / 100.0) - 0.5226

            fR = cy + ci * 0.9469 + cq * 0.6236
            fG = cy - ci * 0.2748 - cq * 0.6357
            fB = cy - ci * 1.1 + cq * 1.7

            rgb_t = tuple(round(i * 255) for i in (fR, fG, fB))
            rgb_data["data"].append(rgb_t)

    logging.info("Image processed!")

    return rgb_data


def write_rgb(img_converted, imgdest_path):
    """ Write image file given structured RGB data and destination path. """
    imgdest = Image.new('RGB', img_converted["size"])
    imgdest.putdata(img_converted["data"])

    if imgdest_path == '-':
        # TODO: Get from the user the desired format for piped output.
        imgdest.save(sys.stdout, 'png')
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


def process_img(img_data, imgdest_path):
    """ Process image given source data and destination. """
    img_converted = img_data["generate_fn"](img_data)
    img_data["write_fn"](img_converted, imgdest_path)


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

        process_img(img_data, args.imgdest)

        logging.info("Completed!")
    except Exception as e:
        logging.error("Error processing image!")
        logging.error(f"Reason: {e}")


if __name__ == "__main__":
    main()
