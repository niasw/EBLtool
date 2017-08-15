#!/usr/bin/python3
# Transfer vector graph (.svg) into LEdit code (.tco)
# usage: python3 svg2tco.py [-s SHIFTX SHIFTY] MASKFILENAME > OUTPUTCODE.tco
# NOTICE: Currently, only boxes(rectangles) & polygons will work.

import xml.dom.minidom
import sys

def polygonProcess(pgpcps): # since codes about polygon and path share the drawing part, so I put them here.
  pgpnum=int(len(pgpcps)/2); # number of points
  # output
  print("polygon ",end=''); # LEDIT command
  for pgpit in range(0,pgpnum):
    pgx=float(pgpcps[pgpit*2]);
    pgy=float(pgpcps[pgpit*2+1]);
    # Fix svg cood: (1,-1) * All cood + (0,1052.3622)
    pgy=1052.3622-pgy;
    # rotate 180: (900,900) - All cood
    #pgx=900.-pgx;
    #pgy=900.-pgy;
    # add shift
    pgx=pgx+shiftx;
    pgy=pgy+shifty;
    # output
    print("!%.3f !%.3f " % (pgx,pgy),end=''); # LEDIT script
  print("\x0D");

if len(sys.argv)<2:
  raise(Exception('Error: no input'));

shiftx=0.;
shifty=0.;

if sys.argv[1].startswith('-'):
  option=sys.argv[1][1];
  if option=='s':
    if len(sys.argv)<5:
      raise(Exception('Error: not enough coordinate parameters to shift'));
    shiftx=float(sys.argv[2]);
    shifty=float(sys.argv[3]);
    svgFileName=sys.argv[4];
  elif option=='h':
    print('# Transfer vector graph (.svg) into LEdit code (.tco)\n# usage: python3 svg2tco.py [-s SHIFTX SHIFTY] MASKFILENAME > OUTPUTCODE.tco\n# NOTICE: Currently, only boxes(rectangles) & polygons will work.');
    sys.exit();
  else:
    raise(Exception('Error: unknown option.'));
    sys.exit();
else:
  svgFileName=sys.argv[1];

dom = xml.dom.minidom.parse(svgFileName.replace("\n",""));
root = dom.documentElement;
rts = root.getElementsByTagName('rect');
pgs = root.getElementsByTagName('polygon');
pts = root.getElementsByTagName('path');
for rt in rts: # rectangles
  rtx=float(rt.getAttribute("x"));
  rty=float(rt.getAttribute("y"));
  rtw=float(rt.getAttribute("width"));
  rth=float(rt.getAttribute("height"));
  # Fix svg cood: (1,-1) * All cood + (0,1052.3622)
  rty=1052.3622-rty-rth;
  # rotate 180: (900,900) - All cood
  #rtx=900.-rtx-rtw;
  #rty=900.-rty-rth;
  # add shift
  rtx=rtx+shiftx;
  rty=rty+shifty;
  # use box center as (x,y)
  rtx=rtx+rtw/2.;
  rty=rty+rth/2.;
  # output
  print("box %.3f %.3f !%.3f !%.3f\x0D" % (rtw,rth,rtx,rty)); # LEDIT script
for pg in pgs: # polygons
  pgps=pg.getAttribute("points");
  pgps=pgps.replace(","," "); # polygon points
  pgpcps=pgps.split(); # polygon points coordinate pairs
  if (len(pgpcps)%2!=0): # unpaired coordinates of points
    pgid="";
    try:
      pgid=pg.getAttribute("id");
    except Exception:
      noop;
    raise(Exception("Error at polygon "+pgid+": unpaired coordinates."));
  polygonProcess(pgpcps);
for pt in pts: # paths (currently polygon only)
  ptps=pt.getAttribute("d");
  paras=ptps.split(); # commands and parameters
  pgset=[]; # set of polygons
  pgpcps=[]; # current polygon (described by polygon points coordinate pairs)
  paranum=len(paras);
  paraiter=0;
  com=''; # current command
  pos=[0.,0.]; # current position
  try:
    while (paraiter<paranum):
      if (len(paras[paraiter])==1): # command
        com=paras[paraiter];
        if (com=='z' or com=='Z'): # close path
          if (len(pgpcps)>0): # save polygon
            pgset.append(pgpcps);
          pgpcps=[];
      else: # coords
        tmpcoord=paras[paraiter].split(',');
        if (com=='m'): # move to relative position
          if (len(tmpcoord)!=2):
            raise(Exception('Error: 2D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos=[float(tmpcoord[0])+pos[0],float(tmpcoord[1])+pos[1]];
          if (len(pgpcps)>0): # save the last one (this should be done by command 'Z' or 'z'. but for now we treat all paths as polygons. maybe we should not do this here in future versions.)
            pgset.append(pgpcps);
          pgpcps=pos;
          com='l';
        elif (com=='M'): # move to absolute position
          if (len(tmpcoord)!=2):
            raise(Exception('Error: 2D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos=[float(tmpcoord[0]),float(tmpcoord[1])];
          if (len(pgpcps)>0): # save the last one (this should be done by command 'Z' or 'z'. but for now we treat all paths as polygons. maybe we should not do this here in future versions.)
            pgset.append(pgpcps);
          pgpcps=pos;
          com='L';
        elif (com=='l'): # line to relative position
          if (len(tmpcoord)!=2):
            raise(Exception('Error: 2D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos=[float(tmpcoord[0])+pos[0],float(tmpcoord[1])+pos[1]];
          pgpcps.extend(pos);
        elif (com=='L'): # line to absolute position
          if (len(tmpcoord)!=2):
            raise(Exception('Error: 2D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos=[float(tmpcoord[0]),float(tmpcoord[1])];
          pgpcps.extend(pos);
        elif (com=='v'): # vertical line to relative position
          if (len(tmpcoord)!=1):
            raise(Exception('Error: 1D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos[1]=float(tmpcoord[1])+pos[1];
          pgpcps.extend(pos);
        elif (com=='V'): # vertical line to absolute position
          if (len(tmpcoord)!=1):
            raise(Exception('Error: 1D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos[1]=float(tmpcoord[1]);
          pgpcps.extend(pos);
        elif (com=='h'): # horizontal line to relative position
          if (len(tmpcoord)!=1):
            raise(Exception('Error: 1D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos[0]=float(tmpcoord[0])+pos[0];
          pgpcps.extend(pos);
        elif (com=='H'): # horizontal line to absolute position
          if (len(tmpcoord)!=1):
            raise(Exception('Error: 1D coordinate needed, '+str(len(tmpcoord))+'D inputed.'));
          pos[0]=float(tmpcoord[0]);
          pgpcps.extend(pos);
        elif (com=='z' or com=='Z'): # close path
          raise(Exception('Error: Z command need no coordinates, '+str(len(tmpcoord))+'D inputed.'));
        else: # curves are not supported yet.
          raise(Exception('Error: unsupported command '+com+', '+str(len(tmpcoord))+'D coordinate inputed.'));
      paraiter+=1;
  except Exception as e:
    print(str(e),file=sys.stderr);
  for pgpcps in pgset: # polygon points coordinate pairs
    if (len(pgpcps)%2!=0): # unpaired coordinates of points
      raise(Exception("Internal Error: unpaired coordinates. -> This should never happen. If it happens, then there is a bug."));
    polygonProcess(pgpcps);

