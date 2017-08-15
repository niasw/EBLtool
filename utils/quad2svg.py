#!/usr/bin/python3
# Generate svg rectangles from coordinate quadruples
# author: Sun Smallwhite <sun.niasw@gmail.com>
# usage: python3 quad2svg.py [-s SHIFTX SHIFTY -d DELIMITER] RECTCOORDFILENAME > OUTPUTRECT.svgfrac
# svgfrac is incomplete svg file, they should be appended in the <g></g> tag in a svg file.
# SHIFTX & SHIFTY : shift position, default (0,0).
# DELIMITER : seperator of data, default ','.
# structure:
#   box1_x_min,box1_y_min,box1_x_max,box1_y_max
#   box2_x_min,box2_y_min,box2_x_max,box2_y_max
#   ...

import csv
import codecs
import argparse
parser = argparse.ArgumentParser(description="Generate svg rectangles from coordinate quadruples.\nstructure:\n    box1_x_min,box1_y_min,box1_x_max,box1_y_max\n   box2_x_min,box2_y_min,box2_x_max,box2_y_max\n   ...");
parser.add_argument("RECTCOORDFILENAME", help="the data file which stores coordinates of rectangles");
parser.add_argument("-s", "--shift", nargs=2, metavar=('SHIFTX', 'SHIFTY'), dest='shift', type=float, default=[0.,0.], help="SHIFTX & SHIFTY : shift position, default (0,0).");
parser.add_argument("-d", "--delimiter", metavar=('DELIMITER'), dest='inputdelimiter', default=',', help="delimiter to seperate coordinates, default ','.");
parser.add_argument("-i", "--idstart", type=int, metavar=('IDSTART'), dest='idstart', default=0, help="start id, default 0.");

args = parser.parse_args();
delimiter=codecs.escape_decode(bytes(args.inputdelimiter, "utf-8"))[0].decode("utf-8"); # http://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python#answer-37059682
inputfileobj=open(args.RECTCOORDFILENAME,'r');
filereader=csv.reader(inputfileobj, delimiter=delimiter);
linenum=0;
for coordquad in filereader:
  linenum+=1;
  if (len(coordquad)<4):
    raise(Exception("Error: incomplete quadruple detected at line %d." % linenum));
  else:
    x=float(coordquad[0])-args.shift[0];
    y=1052.3622047-float(coordquad[1])+args.shift[1];
    width=abs(float(coordquad[0])-float(coordquad[2]));
    xmin=min(x,float(coordquad[2])-args.shift[0]);
    height=abs(float(coordquad[1])-float(coordquad[3]));
    ymin=min(y,1052.3622047-float(coordquad[3])+args.shift[1]);
    print("<rect id=\"rectgen%d\" style=\"opacity:0.5;fill:#ff7f2a\" width=\"%.7f\" height=\"%.7f\" x=\"%.7f\" y=\"%.7f\" />" % (linenum+args.idstart-1,width,height,xmin,ymin));
