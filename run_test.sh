#!/bin/bash
# Transfer all svg rectangles to LEdit commands (.tco)
# by Sun Smallwhite <sun.niasw@gmail.com>

# origin of C Area (left down corner) is at global coordinate (680,680), the global origin is the left down corner of the thick L shape
# area period is 1570
# therefore shift coordinates should be (680,680)+1570x(m,n)
# A area (m,n)=(2,0)
# B area (m,n)=(1,0)
# C area (m,n)=(0,0)
# D area (m,n)=(2,1)
# E area (m,n)=(1,1)
# F area (m,n)=(0,1)
# G area (m,n)=(2,2)
# H area (m,n)=(1,2)
# I area (m,n)=(0,2)

# WFSPS = Writing Field Start Point Shift, default (-50,-50), which means margin = 100
# eg. If C area's local origin (0,0) is at global (680,680), 
#     and we set writing field to [680-marginLeft, 680-marginBottom, 1580+marginRight, 1580+marginTop]
#     (where marginLeft+marginRight+900 & marginBottom+marginTop+900 should be a multiply of 100),
#     then Writing Field Start Point Shift X is 50-marginLeft,
#     and Writing Field Start Point Shift Y is 50-marginBottom.
#     It is the C area local coordinate of the center of the first Writing Field
#     (global at the center of [680-marginLeft,680-marginBottom,780-marginLeft,780-marginBottom])

# Reduce accumulating error:
#   [adjust astigmatism for each area to reduce accumulating error] (it is not convenient,
#    you can use All-area coordinates for convenience, which I will talk about later)

# Default Writing Field: (Global) 
# A: 3670 530 4870 1730
# B: 2100 530 3300 1730
# C: 530 530 1730 1730
# D: 3670 2100 4870 3300
# E: 2100 2100 3300 3300
# F: 530 2100 1730 3300
# G: 3670 3670 4870 4870
# H: 2100 3670 3300 4870
# I: 530 3670 1730 4870
# Writing Field Start Point: -100 -100 (Local)

# 100 Margin Writing Field: (Global)
# A: 3720 580 4820 1680
# B: 2150 580 3250 1680
# C: 580 580 1680 1680
# D: 3720 2150 4820 3250
# E: 2150 2150 3250 3250
# F: 580 2150 1680 3250
# G: 3720 3720 4820 4820
# H: 2150 3720 3250 4820
# I: 580 3720 1680 4820
# Writing Field Start Point: -50 -50 (Local)

# Integer Writing Field: (compatible with writing field auxiliary lines in the software for EBL)
# Area: Writing Field (Global), WFSP: Start Point (Local)
# A: 3700 500 4900 1700 WFSP: -70 -130
# B: 2100 500 3300 1700 WFSP: -100 -130
# C: 500 500 1700 1700 WFSP: -130 -130
# D: 3700 2100 4900 3300 WFSP: -70 -100
# E: 2100 2100 3300 3300 WFSP: -100 -100
# F: 500 2100 1700 3300 WFSP: -130 -100
# G: 3700 3700 4900 4900 WFSP: -70 -70
# H: 2100 3700 3300 4900 WFSP: -100 -70
# I: 500 3700 1700 4900 WFSP: -130 -70 

# patch all areas
insfile=""

python3 patchedges_svg.py -s -100 -100 test.svg > test_Patches.svg.cache
insfile="$(<test_Patches.svg.cache)"
awk -v insfile="$insfile" '/<\/g>/{print insfile;print;next}1' test.svg > test_Patched.svg

# convert to commands
python3 svg2tco.py -s 2250 2250 test_Patched.svg > maskE.txt
# remove the first line (900 x 900 square for area calibration)
sed -ne '1d;p;' < maskE.txt > maskE.cache
# link all areas
rm -f mask.tco
cat maskE.cache | sed -ne '/ 0.000/d;p;' | unique mask.tco
# clean
rm -f *.cache
