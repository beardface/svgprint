#!/bin/bash
ffmpeg -f image2 -r 30/1 -i $1/layer%04d.png -vf "crop=in_w-1:in_h-1" -vcodec libx264 -y $1.mp4
