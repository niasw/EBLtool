#!/usr/bin/python3
# Generate coordinate quadruples from svg rectangles
# author: Sun Smallwhite <sun.niasw@gmail.com>
# usage: python3 svg2quad.py [-s SHIFTX SHIFTY -d DELIMITER] SVGFILENAME > OUTPUTQUAD.csv
# SHIFTX & SHIFTY : shift position, default (0,0).
# DELIMITER : seperator of data, default ','.

import xml.dom.minidom
import codecs
import argparse
parser = argparse.ArgumentParser(description="Generate coordinate quadruples from svg rectangles.");
parser.add_argument("SVGFILENAME", help="the vector graph (.svg) contains rectangles");
parser.add_argument("-s", "--shift", nargs=2, metavar=('SHIFTX', 'SHIFTY'), dest='shift', type=float, default=[0.,0.], help="SHIFTX & SHIFTY : shift position, default (0,0).");
parser.add_argument("-d", "--delimiter", metavar=('DELIMITER'), dest='inputdelimiter', default=',', help="delimiter to seperate coordinates, default ','.");

args = parser.parse_args();

delimiter=codecs.escape_decode(bytes(args.inputdelimiter, "utf-8"))[0].decode("utf-8"); # http://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python#answer-37059682
dom = xml.dom.minidom.parse(args.SVGFILENAME.replace("\n",""));
root = dom.documentElement;
rts = root.getElementsByTagName('rect');
for rt in rts:
  rtx=float(rt.getAttribute("x"));
  rty=float(rt.getAttribute("y"));
  rtw=float(rt.getAttribute("width"));
  rth=float(rt.getAttribute("height"));
  rid=rt.getAttribute("id");
  if (rid=='mainarea'): # 900 x 900 box
    continue;
  if ('corner' in rid): # corner mark for area border
    continue;
  if ('patch' in rid): # patches are not kernel infomation
    continue;
  # Fix svg cood: (1,-1) * All cood + (0,1052.3622)
  rty=1052.3622047-rty-rth;
  # rotate 180: (900,900) - All cood
  #rtx=900.-rtx-rtw;
  #rty=900.-rty-rth;
  # add shift
  rtxmin=rtx+args.shift[0];
  rtymin=rty+args.shift[1];
  rtxmax=rtxmin+rtw;
  rtymax=rtymin+rth;
  # output
  print(("%.7f"+delimiter+"%.7f"+delimiter+"%.7f"+delimiter+"%.7f\x0D") % (rtxmin,rtymin,rtxmax,rtymax));

