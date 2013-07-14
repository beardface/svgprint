#!/bin/bash
./svg_export.sh $1

LAYER_COUNT=`cat .layers`

echo $LAYER_COUNT

for ((i=0; i <$LAYER_COUNT; i++)); do
  python png_print.py -f $1.out/layer$i.png
done
