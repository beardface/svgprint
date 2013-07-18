from PIL import Image
from optparse import OptionParser
import sys
import re
import subprocess
import os

try:
    input= raw_input
except NameError:
    pass
usage = "usage: %prog [--svg | --stl --slic3r=(path to slic3r)] [--inkscape=(path to inkscape)] [--laser | --simulate] [--movie] [--dpi=<DPI (defaults to 2540)>] [--bgcolor=<bgcolor ex. #000000>] --file <FILE_TO_PRINT> [--batch]"
parser = OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="printfile", help="File to Print")
parser.add_option("-g", "--svg", action="store_true", dest="svg", default=False,
                  help="Input File is SVG")
parser.add_option("-t", "--stl", action="store_true", dest="stl", default=False,
                  help="Input File is an STL file")
parser.add_option("-l", "--laser", action="store_true", dest="laser", default=False,
                  help="LASER!")
parser.add_option("-s", "--simulate", action="store_true", dest="simulate", default=False,
                  help="Preview Scan")
parser.add_option("-p", "--png", action="store_true", dest="nogen", default=False,
                  help="Do Not Generate PNG files, they are ready")
parser.add_option("-m", "--movie", action="store_true", dest="movie", default=False, help="Output FFMPEG Movie instead of printing")
parser.add_option("-d", "--dpi", dest="dpi", default=2540, help="Print DPI")
parser.add_option("-r", "--slic3r", dest="slic3r_path", help="full path to Slic3r executable (if printing in --stl mode)")
parser.add_option("-i", "--inkscape", dest="inkscape_path", help="full path to inkscape executable")
parser.add_option("-b", "--bgcolor", dest="bgcolor", default="#000000", help="Background Color for Resulting PNG images")
parser.add_option("-a", "--batch", action="store_true", dest="batch_inkscape", default=False,
                  help="Batch Inkscape Commands (faster, but not supported everywhere)")
(options, args) = parser.parse_args()

if options.stl:
	#Generate SVG File from Slic3r
	print "Converting STL input file to SVG using Slic3r... (please wait)"
	print options.slic3r_path
	svg_file="OUTPUT FILE FROM SLIC3R"
	
if options.svg:
	svg_file=options.printfile

if svg_file == None:
	sys.exit("Missing an SVG Input File!")

print "Preparing file for print:",svg_file,"..."

#Get the number of layers from the svg file
regex = re.compile(r'layer')
f=open(svg_file)
svg_layer_count=0
for i, line in enumerate(f.readlines()):
	searchedstr = regex.findall(line)
	for word in searchedstr:
		svg_layer_count+=1
		break
f.close()

print "Found",svg_layer_count,"layers in the SVG file."

layer_height="0"
regex = re.compile(r'slic3r:z="(.*)"')
f=open(svg_file)
found=False
for i, line in enumerate(f.readlines()):
	searchedstr = regex.findall(line)
	for word in searchedstr:
		layer_height=word
		found=True
		break
	if found:
		break
f.close()

print "Each Layer is",layer_height,"mm high"

output_path=svg_file+".out"
print ""
print " File Name:  ",svg_file
print " Output Path:",output_path
print "    Layer Height =",layer_height,"mm"
print "    DPI          =",options.dpi
print "    # of Layers  =",svg_layer_count
print ""
print " Inkscape: ",options.inkscape_path
print ""

if not options.nogen:
	input("Hit Enter to Begin Generation (Otherwise, hit CTRL-C)")

if not options.nogen:
	try:
		os.mkdir(output_path)
	except OSError:
		pass

	try:
		os.remove(".inkscapeBatch")
	except OSError:
		pass

	if options.batch_inkscape:
		f1=open('./.inkscapeBatch', 'w+')
	for layeri in range(svg_layer_count):
		p=str((float(layeri)/float(svg_layer_count))*100)+"%% "+str(layeri)+"/"+str(svg_layer_count)
		sys.stdout.write("\r%s     " %p)
		args="-j -i layer"+str(layeri)+" -e "+output_path+"/"+"layer"+str(layeri).zfill(4)+".png "+svg_file+" --export-background="+options.bgcolor+" --export-dpi="+str(options.dpi)
		cmd=""
		if options.batch_inkscape:
			f1.write(args+"\n")
		else:
			cmd=options.inkscape_path+" "+args
			subprocess.call(cmd)

	if options.batch_inkscape:
		f1.close()
	print ""
	input("Hit Enter to Begin Batch (Otherwise, hit CTRL-C)")

	if options.batch_inkscape:
		print "Doing a batch process of all inkscape commands... patience!"
		cmd=options.inkscape_path+" --shell < .inkscapeBatch"
		subprocess.call(cmd)
	
input("Hit Enter to start printing (Otherwise, hit CTRL-C)")
for layeri in range(svg_layer_count):
	vert="-v"
	sim=""
	lase=""
	if (layeri % 2) == 0:
		vert=""
	if options.simulate:
		sim="-p"
	if options.laser:
		lase="-l"
	p=str((float(layeri)/float(svg_layer_count))*100)+"%% "+str(layeri)+"/"+str(svg_layer_count)
	sys.stdout.write("\r%s     " %p)
	args=" --file="+output_path+"/"+"layer"+str(layeri).zfill(4)+".png "+vert+" "+sim+" "+lase
	subprocess.call("python png_scan.py"+args)

print ""

print "Done!"
