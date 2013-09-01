from PIL import Image
from optparse import OptionParser
import sys, re, time
import subprocess
import os, glob
import printcore

try:
    input= raw_input
except NameError:
    pass
usage = "usage: %prog [--svg | --stl --slic3r=(path to slic3r)] [--inkscape=(path to inkscape)] [--laser | --simulate] [--movie] [--dpi=<DPI (defaults to 2540)>] [--bgcolor=<bgcolor ex. #000000>] --file <FILE_TO_PRINT> [--batch]"
parser = OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="printfile", help="File to Print")
parser.add_option("", "--svg", action="store_true", dest="svg", default=False,
                  help="Input File is SVG")
parser.add_option("","--stl", action="store_true", dest="stl", default=False,
                  help="Input File is an STL file")
parser.add_option("", "--laser", action="store_true", dest="laser", default=False,
                  help="LASER!")
parser.add_option("-z", "--layer-height", dest="layer_height", default=0.1, help="Layer Height")
parser.add_option("", "--simulate", action="store_true", dest="simulate", default=False,
                  help="Preview Scan")
parser.add_option("", "--png", action="store_true", dest="nogen", default=False,
                  help="Do Not Generate PNG files, they are ready")
parser.add_option("", "--movie", action="store_true", dest="movie", default=False, help="Output FFMPEG Movie instead of printing")
parser.add_option("-d", "--dpi", dest="dpi", default=2540, help="Print DPI")
parser.add_option("-j", "--jump", dest="jump", default=0, help="For Debugging, how many layers to jump before printing")
parser.add_option("-r", "--slic3r", dest="slic3r_path", help="full path to Slic3r executable (if printing in --stl mode)")
parser.add_option("-i", "--inkscape", dest="inkscape_path", help="full path to inkscape executable")
parser.add_option("-b", "--bgcolor", dest="bgcolor", default="#000000", help="Background Color for Resulting PNG images")
parser.add_option("", "--batch", action="store_true", dest="batch_inkscape", default=False,
                  help="Batch Inkscape Commands (faster, but not supported everywhere)")
parser.add_option("", "--power", dest="power", default=1000, help="Laser Power (20-1000)")
parser.add_option("", "--xscale", dest="xscale", default=0.999, help="X Scale for Laser Scan (0.001-0.999)")
parser.add_option("", "--yscale", dest="yscale", default=0.999, help="Y Scale for Laser Scan (0.001-0.999)")
parser.add_option("", "--baud", dest="baud", default=250000, help="Serial Baud Rate")
parser.add_option("", "--port", dest="port", default="COM5", help="Serial Port")
parser.add_option("", "--tilt", dest="tilt", default=5.0, help="Z Tilt Distance (Default 5.0mm)")
parser.add_option("", "--tilt_speed", dest="tilt_speed", default=300, help="Z Tilt Distance (Default 300mm/min)")
parser.add_option("", "--tilt_hold_ms", dest="tilt_hold_ms", default=500, help="ms to wait between each z move")
(options, args) = parser.parse_args()

if options.printfile == None:
    sys.exit("Missing an Input File!")

printerSerial=printcore.printcore()

if options.simulate == False:
   print "Connecting to printer... (Port: ",options.port," Baud: ",options.baud,")"
   printerSerial.connect(options.port, options.baud)
    
if options.stl and options.slic3r_path != None:
    #Generate SVG File from Slic3r
    cmd=options.slic3r_path+" --export-svg --layer-height "+str(options.layer_height)+" --first-layer-height "+str(options.layer_height)+" "+options.printfile
    svg_file=options.printfile.replace(".stl",".svg")
    svg_file=svg_file.replace(".STL",".svg")
    if os.name == "nt":
        subprocess.call(cmd)
    else:
        os.system(cmd)

input("Hit Enter to Continue...")

if options.svg or options.nogen:
    svg_file=options.printfile

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

layer_move=options.tilt-float(layer_height)

output_path=svg_file+".out"
print ""
print " File Name:  ",svg_file
print " Output Path:",output_path
print "    Layer Height =",layer_height,"mm"
print "    Layer Move =",layer_move,"mm"
print "    DPI          =",options.dpi
print "    # of Layers  =",svg_layer_count
print ""
print " Inkscape: ",options.inkscape_path
print ""

if not options.nogen:
    input("Hit Enter to Begin Generation (Otherwise, hit CTRL-C)")

if not options.nogen and options.inkscape_path != None:
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
        args="-j -i layer"+str(layeri)+" -e "+output_path+"/"+"layer"+str(layeri).zfill(4)+".png "+svg_file+" -C --export-background="+options.bgcolor+" --export-dpi="+str(options.dpi)
        cmd=""
        if options.batch_inkscape:
            f1.write(args+"\n")
        else:
            cmd=options.inkscape_path+" "+args
            print cmd
            if os.name == "nt":
                subprocess.call(cmd)
            else:
                os.system(cmd)

    if options.batch_inkscape:
        f1.close()
        print ""
        input("Hit Enter to Begin Batch (Otherwise, hit CTRL-C)")

    if options.batch_inkscape:
        print "Doing a batch process of all inkscape commands... patience!"
        cmd=options.inkscape_path+" --shell < .inkscapeBatch"
        if os.name == "nt":
            subprocess.call(cmd)
        else:
            os.system(cmd)
    
input("Hit Enter to start printing (Otherwise, hit CTRL-C)")

printerSerial.send("G21", options.simulate)
printerSerial.send("G28", options.simulate)
input("Printer is now at Home Position, Hit Enter to REALLY start printing. (Otherwise, hit CTRL-C)")

for layeri in range(svg_layer_count-int(options.jump)):
    tlayer=layeri+int(options.jump)
    vert="-v"
    sim=""
    lase=""
    if (tlayer % 2) == 0:
        vert=""
    if options.simulate:
        sim="--preview"
    if options.laser:
        lase="--laser"
    p=str((float(layeri)/float(svg_layer_count))*100)+"%% "+str(layeri)+"/"+str(svg_layer_count)
    sys.stdout.write("\r%s     " %p)
    args=" --file="+output_path+"/"+"layer"+str(tlayer).zfill(4)+".png "+vert+" "+sim+" "+lase+" --power="+str(options.power)+" --xscale="+str(options.xscale)+" --yscale="+str(options.yscale)
    cmd = "python png_scan.py"+args
    if os.name == "nt":
        subprocess.call(cmd)
    else:
        os.system(cmd)

    # Do Layer Z Move
    printerSerial.send("G91", options.simulate) # Relative Pos
    printerSerial.send("G1 L"+str(options.tilt)+" F"+str(options.tilt_speed), options.simulate) #Left side up 5mm
    printerSerial.send("G4 P"+str(options.tilt_hold_ms), options.simulate) # Wait 500 ms
    printerSerial.send("G1 R"+str(options.tilt)+" F"+str(options.tilt_speed), options.simulate) # Right side up 5 mm
    printerSerial.send("G4 P"+str(options.tilt_hold_ms), options.simulate) # Wait 500 ms
    printerSerial.send("G1 Z-"+str(layer_move)+" F"+str(options.tilt_speed), options.simulate) # Z down 5 mm
    printerSerial.send("G4 P1000", options.simulate) # Wait 1 Second
    time.sleep(5) #Sleep for 10 seconds
    printerSerial.send("M84", options.simulate) # Motors Off

# Do Layer Z Move
printerSerial.send("G91", options.simulate)
printerSerial.send("G1 Z30.0 E30.0 F100.0", options.simulate) # Z axis up 30
time.sleep(5)
printerSerial.send("M84", options.simulate) # Motors Off
printerSerial.disconnect()
print ""

print "Done!"
