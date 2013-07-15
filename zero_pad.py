import os
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p", "--path", dest="pngpath", help="Path to files")

(options, args) = parser.parse_args()

path = options.pngpath
for filename in os.listdir(path):
    prefix, num = filename[:-4].split('layer')
    num = num.zfill(4)
    new_filename = "layer" + num + ".png"
    os.rename(os.path.join(path, filename), os.path.join(path, new_filename))

