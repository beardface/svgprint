#!/bin/bash
#./svg_export.sh $1

python zero_pad.py -p $1.out

ffmpeg -f image2 -r 30/1 -i $1.out/layer%04d.png -vf "crop=in_w-1:in_h-1" -vcodec libx264 -y $1.mp4

LAYER_COUNT=`cat .layers`

echo $LAYER_COUNT

#for f in `ls -1 $1.out`
#do
#  python png_print.py -f $1.out/layer$i.png
#done