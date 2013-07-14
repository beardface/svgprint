#!/bin/bash
DOTS_PER_INCH=2540

LAYER_COUNT=`fgrep layer $1 | wc -l`
touch .layers
echo $LAYER_COUNT > .layers

LINE_HEIGHT=`fgrep "slic3r:z" $1 -m 1`

echo Found $LAYER_COUNT layers…
echo Each Layer is $LINE_HEIGHT mm high

rm -rf $1.out

mkdir $1.out

touch svg_export_$1_commands.txt
for ((i=0; i <$LAYER_COUNT; i++)); do
   echo -j -i layer$i -e $1.out/layer$i.png $1 -C --export-dpi $DOTS_PER_INCH  >> svg_export_$1_commands.txt
done

inkscape --shell < svg_export_$1_commands.txt

rm svg_export_$1_commands.txt

