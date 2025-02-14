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

7. You are ready to execute the program! check the following section.

How to use
==========

From a terminal, type the following:

    ./rgb2yiq.py [-h] [-q] [-v] [-l] infile [outfile]

- Option `-h` displays a help message.
- Option `-q` prevents messages from appearing (only outputs errors).
- Option `-v` prints version number.
- Option `-l` shows license information.
- Mandatory argument `infile` is the input filename
- Optional argument `outfile` is the output file (ommitting it sends output to stdout).

It currently supports any image type supported by Pillow.

When the program generates a file as output, it can either stream it to standard output (if no `outfile` is given), or write it to the file whose name is given as `outfile`.

File structure
==============

A YIQ file has the following structure, regardless of where it has been written (to a file or standard output).

1. The first 4 bytes indicate filetype magic number (the string `YIQ1` is used for valid YIQ images).
2. Following the magic number, width and height of the image are stored as 4-byte, little-endian numbers.
3. Then comes the string `DATA` (4 bytes long), indicating where the actual YIQ data starts.
4. Finally, in sequential order, triplets of (Y, I, Q) bytes are stored for each point in the image, ajusted to the following:
    - Y value is stored as an integer, $0 <= Y <= 100$
    - I and Q are rounded and stored as integers, $0 <= I, Q <= 255$

To Do
=====

1. Implement reverse-direction conversion: from YIQ to image files.
2. Allow native compression to generated files (requires changes in file structure). This issue can be partially addressed by sending to stdout and piping to any compression utility like `gzip`.
3. Use `numpy` to vectorize process and allow for faster conversion.

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
