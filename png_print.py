from PIL import Image
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="svgfile", help="SVG Layer File to Print")

(options, args) = parser.parse_args()

i = Image.open(options.svgfile)

pixels = i.load() # this is not a list
width, height = i.size
row_averages = []
for y in range(height):
    cur_row_ttl = 0
    for x in range(width):
        cur_pixel = pixels[x, y]
        cur_pixel_mono = sum(cur_pixel) / len(cur_pixel)
        cur_row_ttl += cur_pixel_mono

    cur_row_avg = cur_row_ttl / width
    row_averages.append(cur_row_avg)

print options.svgfile,
print " Height:",
print height,
print " Width:",
print width