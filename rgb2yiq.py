"""
	RGB2YIQ: RGB to YIQ Pillow-based conversion program for Python 3.x
	Copyright (C) 2014	sm-programmer

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

from PIL import Image
from struct import *
import sys
import argparse

def smart_open(fname=None):
	""" Determine whether output should be a file or stdout """
	if fname and fname != '-':
		return open(fname, 'wb')
	else:
		return sys.stdout.buffer

def smart_close(fp):
	""" Close output if applicable """
	if fp != sys.stdout.buffer:
		fp.close()
		
class show_license(argparse.Action):
	""" Define custom action that merely prints license information """
	def __call__(self, parser, namespace, values, option_string=None):
		print("RGB2YIQ: RGB to YIQ Pillow-based conversion program for Python 3.x")
		print("Copyright (C) 2014\tsm-programmer\n")
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

# Prepare the argument parser
parser = argparse.ArgumentParser(description="Converts an image into its YIQ equivalent.")
parser.add_argument('useimg', help="Input image file to be processed", metavar='infile')
parser.add_argument('target', nargs='?', help="Output image basename, let empty to output to stdout", default='-', metavar='outfile')
parser.add_argument('-q', '--quiet', action='store_true', help="don't output operation details, only errors")
parser.add_argument('-v', '--version', action='version', version="%(prog)s\tv1.1.0")
parser.add_argument('-l', '--license', nargs=0, action=show_license, help="show license information and exit")

# Get the arguments
args = parser.parse_args()

# Process files with given arguments
try:
	img = Image.open(args.useimg)
	if args.quiet is False:
		print("\nName:", args.useimg)
		print("Format:", img.format)
		print("Size:", img.size[0], "X", img.size[1])
		print("Colour model:", img.mode, "\n")
	if img.mode == 'RGB':
		img_rgb = img
	else:
		img_rgb = img.convert('RGB')
	try:
		target = smart_open(args.target + '.yiq')
		if args.quiet is False:
			print("Writing header information...")
		target.write("YIQ1".encode('utf-8'))
		target.write(pack('LL', img.size[0], img.size[1]))
		target.write("DATA".encode('utf-8'))
		pix = img_rgb.load()
		if args.quiet is False:
			print("Processing pixels...")
		for y in range(0, img.size[1]):
			for x in range(0, img.size[0]):
				r, g, b = pix[x, y]
				r /= 255
				g /= 255
				b /= 255
				fY = r * 0.30 + g * 0.59 + b * 0.11
				fI = r * 0.599 - g * 0.2773 - b * 0.3217
				fQ = r * 0.213 - g * 0.5251 + b * 0.3121
				target.write(pack('bbb', round(fY*100), round(fI*100), round(fQ*100)))
		smart_close(target)
		if args.quiet is False:
			print("Completed!")
	except:
		print("Can't create output file!", file=sys.stderr)
except:
	print(args.useimg, ": image not found", file=sys.stderr)

