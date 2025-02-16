rgb2yiq
=======

RGB to YIQ PIL-based image converter for Python 3.x

Copyright (C) 2025, Aura Lesse Programmer

Objective
=========

This project aims to develop software capable of converting any type of images into special YIQ image files (for now using a custom file structure).

YIQ files are interesting when it comes to obtaining compatible B/W images with no extra processing, whilst preserving colour information as well.

This small program demonstrates its usefulness as it only requires Pillow and a Python 3 interpreter to run properly.

Get and set up
==============

1. Ensure you have, at least, Python 3.7 installed.
2. Clone this repository to any directory desired.
3. Go to the directory of step 2, then create an environment with the following command:

       $ python -m venv env

4. Go into the environment with the following command:

       $ source env/bin/activate

5. Install the required dependencies with the following command:

       $ python -m pip install -r requirements.txt

6. Once installed, grant execution permissions to the script with the following command:

       $ chmod u+x rgb2yiq.py

7. You are ready to execute the program! Check the following section.

How to use
==========

From a terminal, type the following:

    ./rgb2yiq.py [-hqvle] [-m (ntsc-1953 | smpte-c)] infile (outfile | -t type)

- Option `-h` displays a help message.
- Option `-q` prevents messages from appearing (only outputs errors).
- Option `-v` prints version number.
- Option `-l` shows license information.
- Option `-e` shows supported output extensions to use with `-t`.
- Option `-m` chooses a colorimetry method to use:
  * Value `ntsc-1953` uses the original NTSC color specification of 1953.
  * Value `smpte-c` uses the SMPTE C standard, adopted in 1987. This is the default.
- Mandatory parameter `infile` is the input filename.
- Selectable parameter `outfile` is the output file name (omitting it sends output to stdout).
- Selectable option `-t` defines output file type to emit to `stdout`.
- Parameters `outfile` and `-t` are mutually exclusive: only one of them can be given at a time.

It currently supports any image type supported by Pillow.

When the program generates a file as output, it can either stream it to standard output (if no `outfile` is given), or write it to the file whose name is given as `outfile`.

File structure
==============

A YIQ file has the following structure, regardless of where it has been written (to a file or standard output).

1. The first 3 bytes indicate filetype magic number (the string `YIQ` is used for valid YIQ images).
2. Following the magic number, a byte number indicates the image version, currently at `1`.
3. Then a byte is used to indicate the colorimetry method used to generate the file.
   * If the value is `0`, the file uses the `ntsc-1953` method.
   * If the value is `1`, the file uses the `smpte-c` method.
4. Following are the width and height of the image, each value stored as a 4-byte, little-endian number.
5. Then comes the string `DATA` (4 bytes long), indicating where the actual YIQ data starts.
6. Finally, in sequential order, triplets of $(Y, I, Q)$ bytes are stored for each point in the image, ajusted to the following:
   - All $Y$, $I$, and $Q$ values are multiplied by 100, then rounded, prior to saving.
   - Y value domain after rounding: $0 <= Y <= 100$.
   - I value domain after rounding: $0 <= I <= 119$ (with pre-multiply translation of $0.5957$).
   - Q value domain after rounding: $0 <= Q <= 105$ (with pre-multiply translation of $0.5226$).

To Do
=====

1. ~~Implement reverse-direction conversion: from YIQ to image files.~~
2. ~~Allow for selection of image format for inverse conversion, when outputting to `stdout`.~~
3. ~~Allow for colorimetry method selection, between original NTSC 1953 and SMPTE C.~~
4. Allow native compression to generated files (requires changes in file structure). This issue can be partially addressed by sending to stdout and piping to any compression utility like `gzip`.
5. Use `numpy` to vectorize process and allow for faster conversion.

License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
