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

version = "1.2.0"


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


def generate_yiq_v1(img_pix, img_size):
    """ Generate YIQ image, v1, given image pixels and size """

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
            
            yiq_data.extend(pack('<bbb', *(round(i * 100) for i in (fY, fI, fQ))))

    logging.info("Image processed!")

    return yiq_data


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
    img = Image.open(imgsrc)

    logging.info(f"Name: {imgsrc}")
    logging.info(f"Format: {img.format}")
    logging.info(f"Size: {img.size[0]} X {img.size[1]}")
    logging.info(f"Colour model: {img.mode}\n")

    if img.mode == 'RGB':
        img_rgb = img
    else:
        img_rgb = img.convert('RGB')
    
    try:
        imgdest = smart_open(f"{args.imgdest}", args.imgdest == "-")
        pix = img_rgb.load()

        imgdest.write(generate_yiq_v1(pix, img.size))
        
        smart_close(imgdest)
        
        logging.info("Completed!")
    except:
        logging.error("Can't create output file!")


if __name__ == "__main__":
    main()
