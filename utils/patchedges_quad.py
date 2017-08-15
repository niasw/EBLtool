#!/usr/bin/python3
# Read quadruples of rectangle coordinates (.csv), add patches at the edges of writing fields,
# then output the patches as rectangle quadruples (.csv)
# author: Sun Smallwhite <sun.niasw@gmail.com>
# usage: python3 patchedges_quad.py [-s WFSPSX WFSPSY -w WIDTH -e EXTRUSION -d DELIMITER] MASKFILENAME > OUTPUTPATCHES.csv
# NOTICE: Currently, only boxes(rectangles) will work.
# WFSPS = Writing Field Start Point Shift, default (-100,-100), which means margin = 150
# eg. If C area's local origin (0,0) is at global (680,680), 
#     and we set writing field to [680-marginLeft, 680-marginBottom, 1580+marginRight, 1580+marginTop]
#     (where marginLeft+marginRight+900 & marginBottom+marginTop+900 should be a multiply of 100),
#     then Writing Field Start Point Shift X is 50-marginLeft,
#     and Writing Field Start Point Shift Y is 50-marginBottom.
#     It is the C area local coordinate of the center of the first Writing Field
#     (global at the center of [680-marginLeft,680-marginBottom,780-marginLeft,780-marginBottom])
# WIDTH = width of patch, default 6
# EXTRUSION = (height of patch - box height) / 2, default 0
# DELIMITER : seperator of data, default ','.

import csv
import math
import codecs
import argparse
parser = argparse.ArgumentParser(description="Read quadruples of rectangle coordinates (.csv), add patches at the edges of writing fields,\n# then output the patches as rectangle quadruples (.csv).");
parser.add_argument("MASKFILENAME", help="the quadruples of rectangle coordinates (.csv) to be patched");
parser.add_argument("-s", "--shift", nargs=2, metavar=('WFSPSX', 'WFSPSY'), dest='shift', type=float, default=[-100.,-100.], help="WFSPS = Writing Field Start Point Shift, default (-100,-100), which means margin = 150.");
parser.add_argument("-w", "--width", metavar=('WIDTH'), dest='width', type=float, default=6., help="WIDTH = width of patch, default 6.");
parser.add_argument("-e", "--extrusion", metavar=('EXTRUSION'), dest='extrusion', type=float, default=0., help="EXTRUSION = (height of patch - box height) / 2, default 0.");
parser.add_argument("-d", "--delimiter", metavar=('DELIMITER'), dest='inputdelimiter', default=',', help="delimiter to seperate coordinates, default ','.");

args = parser.parse_args();

delimiter=codecs.escape_decode(bytes(args.inputdelimiter, "utf-8"))[0].decode("utf-8"); # http://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python#answer-37059682
inputfileobj=open(args.MASKFILENAME,'r');
filereader=csv.reader(inputfileobj, delimiter=delimiter);
linenum=0;
for coordquad in filereader:
  linenum+=1;
  if (len(coordquad)<4):
    raise(Exception("Error: incomplete quadruple detected at line %d." % linenum));
  else:
    rtx=min(float(coordquad[0]),float(coordquad[2]));
    rty=min(float(coordquad[1]),float(coordquad[3]));
    rtw=abs(float(coordquad[0])-float(coordquad[2]));
    rth=abs(float(coordquad[1])-float(coordquad[3]));
    # rotate 180: (900,900) - All cood
    #rtx=900.-rtx-rtw;
    #rty=900.-rty-rth;
    # writing field coordinates
    rtxmin=rtx-args.shift[0]+50.;
    rtymin=rty-args.shift[1]+50.;
    rtxmax=rtxmin+rtw;
    rtymax=rtymin+rth;
    # determine start and final writing field
    startx=int(math.floor((rtxmin-args.width/2.)/100.));
    finalx=int(math.ceil((rtxmax+args.width/2.)/100.));
    starty=int(math.floor((rtymin-args.width/2.)/100.));
    finaly=int(math.ceil((rtymax+args.width/2.)/100.));
    # generate patches
    for wfx in range(startx+1,finalx):
      patchxmin=max(100.*wfx-args.width/2,rtxmin); # at edge: do not exceed origin rectangle
      patchxmax=min(100.*wfx+args.width/2,rtxmax); # at edge: do not exceed origin rectangle
      patchymin=rtymin-args.extrusion;
      patchymax=rtymax+args.extrusion;
      patchwidth=patchxmax-patchxmin;
      patchheight=patchymax-patchymin;
      # return to area coordinates
      patchx=patchxmin+args.shift[0]-50.;
      patchy=patchymin+args.shift[1]-50.;
      # output
      print(("%.7f"+delimiter+"%.7f"+delimiter+"%.7f"+delimiter+"%.7f\x0D") % (patchx,patchy,patchx+patchwidth,patchy+patchheight));
    for wfy in range(starty+1,finaly):
      patchymin=max(100.*wfy-args.width/2,rtymin); # at edge: do not exceed origin rectangle
      patchymax=min(100.*wfy+args.width/2,rtymax); # at edge: do not exceed origin rectangle
      patchxmin=rtxmin-args.extrusion;
      patchxmax=rtxmax+args.extrusion;
      patchwidth=patchxmax-patchxmin;
      patchheight=patchymax-patchymin;
      # return to area coordinates
      patchx=patchxmin+args.shift[0]-50.;
      patchy=patchymin+args.shift[1]-50.;
      # output
      print(("%.7f"+delimiter+"%.7f"+delimiter+"%.7f"+delimiter+"%.7f\x0D") % (patchx,patchy,patchx+patchwidth,patchy+patchheight));

