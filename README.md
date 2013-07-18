svgprint
========

Usage:
======
Usage: stlprint.py [--svg | --stl --slic3r=(path to slic3r)] [--inkscape=(path t
o inkscape)] [--laser | --simulate] [--movie] [--dpi=<DPI (defaults to 2540)>] [
--bgcolor=<bgcolor ex. #000000>] --file <FILE_TO_PRINT> [--batch]

Options:
  -h, --help            show this help message and exit
  -f PRINTFILE, --file=PRINTFILE
                        File to Print
  -g, --svg             Input File is SVG
  -t, --stl             Input File is an STL file
  -l, --laser           LASER!
  -s, --simulate        Preview Scan
  -p, --png             Do Not Generate PNG files, they are ready
  -m, --movie           Output FFMPEG Movie instead of printing
  -d DPI, --dpi=DPI     Print DPI
  -r SLIC3R_PATH, --slic3r=SLIC3R_PATH
                        full path to Slic3r executable (if printing in --stl
                        mode)
  -i INKSCAPE_PATH, --inkscape=INKSCAPE_PATH
                        full path to inkscape executable
  -b BGCOLOR, --bgcolor=BGCOLOR
                        Background Color for Resulting PNG images
  -a, --batch           Batch Inkscape Commands (faster, but not supported
                        everywhere)
						
Windows Example:
================
"python stlprint.py --svg -f EiffelTower.svg --inkscape="C:\Program Files (x86)\Inkscape\inkscape.exe" --png --simulate" 
