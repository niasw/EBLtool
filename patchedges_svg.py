#!/usr/bin/python3
# Read vector graph (.svg), add patches at the edges of writing fields,
# then output the patches as svg rectangles
# author: Sun Smallwhite <sun.niasw@gmail.com>
# usage: python3 patchedges_svg.py [-s WFSPSX WFSPSY -w WIDTH -e EXTRUSION -i IDSTART] MASKFILENAME > OUTPUTPATCHES.svgfrac
# svgfrac is incomplete svg file, they should be appended in the <g></g> tag in a svg file.
# NOTICE: Currently, only boxes(rectangles) and polygons will work.
# WFSPS = Writing Field Start Point Shift, default (-100,-100), which means margin = 150
# eg. If C area's local origin (0,0) is at global (680,680), 
#     and we set writing field to [680-marginLeft, 680-marginBottom, 1580+marginRight, 1580+marginTop]
#     (where marginLeft+marginRight+900 & marginBottom+marginTop+900 should be a multiply of 100),
#     then Writing Field Start Point Shift X is 50-marginLeft,
#     and Writing Field Start Point Shift Y is 50-marginBottom.
#     It is the C area local coordinate of the center of the first Writing Field
#     (global at the center of [680-marginLeft,680-marginBottom,780-marginLeft,780-marginBottom])
# WIDTH = width of patch, default 2
# EXTRUSION = (height of patch - box height) / 2, default 0. (currently only available in rectangles)
# IDSTART = start id, info of svg rectangle, default 0

import xml.dom.minidom
import math
import numpy
import argparse
parser = argparse.ArgumentParser(description="Read vector graph (.svg), add patches at the edges of writing fields,\n# then output the patches as svg rectangles.");
parser.add_argument("MASKFILENAME", help="the vector graph (.svg) to be patched");
parser.add_argument("-s", "--shift", nargs=2, metavar=('WFSPSX', 'WFSPSY'), dest='shift', type=float, default=[-100.,-100.], help="WFSPS = Writing Field Start Point Shift, default (-100,-100), which means margin = 150.");
parser.add_argument("-w", "--width", metavar=('WIDTH'), dest='width', type=float, default=2., help="WIDTH = width of patch, default 2.");
parser.add_argument("-e", "--extrusion", metavar=('EXTRUSION'), dest='extrusion', type=float, default=0., help="EXTRUSION = (height of patch - box height) / 2, default 0. (currently only available in rectangles)");
parser.add_argument("-i", "--idstart", type=int, metavar=('IDSTART'), dest='idstart', default=0, help="start id, default 0.");

args = parser.parse_args();

dom = xml.dom.minidom.parse(args.MASKFILENAME.replace("\n",""));
root = dom.documentElement;
rts = root.getElementsByTagName('rect');
pgs = root.getElementsByTagName('polygon');
pts = root.getElementsByTagName('path');
patchnum = 0;

def linearInterpolate(x,x1,x2,y1,y2):
  if (x1!=x2):
    return (y2-y1)/(x2-x1)*(x-x1)+y1;
  else:
    return (y1+y2)/2.;

import sys

def polygonProcess(pgpcps,patchnum):
  # since codes about polygon and path share the patch generating part, so I put them here.
  # return new patchnum
  pgpnum=int(len(pgpcps)/2); # number of points
  pgpcs=numpy.array(pgpcps);
  pgpcs=numpy.reshape(pgpcs,(pgpnum,2));
  pgpcs=pgpcs.transpose();
  pgpcx=pgpcs[0];
  pgpcy=pgpcs[1];
  # Fix svg cood: (1,-1) * All cood + (0,1052.3622)
  pgpcy=[1052.3622047-float(it) for it in pgpcy];
  # rotate 180: (900,900) - All cood
  #pgpcx=[900.-float(it) for it in pgpcx];
  #pgpcy=[900.-float(it) for it in pgpcy];
  # writing field coordinates
  pgpcx=[float(it)-args.shift[0]+50. for it in pgpcx];
  pgpcy=[float(it)-args.shift[1]+50. for it in pgpcy];
  # determine start and final writing field
  pgpcxmin=min(pgpcx);
  pgpcymin=min(pgpcy);
  pgpcxmax=max(pgpcx);
  pgpcymax=max(pgpcy);
  startx=int(math.floor((pgpcxmin-args.width/2.)/100.));
  finalx=int(math.ceil((pgpcxmax+args.width/2.)/100.));
  starty=int(math.floor((pgpcymin-args.width/2.)/100.));
  finaly=int(math.ceil((pgpcymax+args.width/2.)/100.));
  # generate patches
  patchedgex=[[] for it in range(startx+1,finalx)]; # patch edge coordinates
  patchedgey=[[] for it in range(starty+1,finaly)]; # patch edge coordinates
  for pgit in range(0,pgpnum):
    # collect x patch edges
    if (pgpcx[pgit]<pgpcx[(pgit+1)%pgpnum]): # positive x direction
      lstartx=int(math.floor((pgpcx[pgit]-args.width/2.)/100.));
      lfinalx=int(math.ceil((pgpcx[(pgit+1)%pgpnum]+args.width/2.)/100.));
      for wfx in range(lstartx+1,lfinalx):
        # print("-> "+str(wfx));
        patchxstart=max(100.*wfx-args.width/2,pgpcx[pgit]); # at edge: do not exceed origin polygon
        patchxfinal=min(100.*wfx+args.width/2,pgpcx[(pgit+1)%pgpnum]); # at edge: do not exceed origin polygon
        patchystart=linearInterpolate(patchxstart,pgpcx[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[pgit],pgpcy[(pgit+1)%pgpnum])-args.extrusion;
        patchyfinal=linearInterpolate(patchxfinal,pgpcx[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[pgit],pgpcy[(pgit+1)%pgpnum])+args.extrusion;
        patchedgex[wfx-startx-1].append([patchxstart,patchystart,patchxfinal,patchyfinal]); # record edge with direction
    elif (pgpcx[pgit]>pgpcx[(pgit+1)%pgpnum]): # negative x direction
      lstartx=int(math.ceil((pgpcx[pgit]+args.width/2.)/100.));
      lfinalx=int(math.floor((pgpcx[(pgit+1)%pgpnum]-args.width/2.)/100.));
      for wfx in range(lfinalx+1,lstartx):
        # print("<- "+str(wfx));
        patchxstart=min(100.*wfx+args.width/2,pgpcx[pgit]); # at edge: do not exceed origin polygon
        patchxfinal=max(100.*wfx-args.width/2,pgpcx[(pgit+1)%pgpnum]); # at edge: do not exceed origin polygon
        patchystart=linearInterpolate(patchxstart,pgpcx[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[pgit],pgpcy[(pgit+1)%pgpnum])-args.extrusion;
        patchyfinal=linearInterpolate(patchxfinal,pgpcx[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[pgit],pgpcy[(pgit+1)%pgpnum])+args.extrusion;
        patchedgex[wfx-startx-1].append([patchxstart,patchystart,patchxfinal,patchyfinal]); # record edge with direction
    else: # constant x
      lstartx=int(math.floor((pgpcx[pgit]-args.width/2.)/100.));
      lfinalx=int(math.ceil((pgpcx[(pgit+1)%pgpnum]+args.width/2.)/100.));
      if (lstartx+1==lfinalx-1): # at edge, wfx==lstartx+1==lfinalx-1
        # print(" | "+str(lstartx+1));
        patchedgex[lstartx-startx].append([pgpcx[pgit],pgpcy[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[(pgit+1)%pgpnum]]);
    # collect y patch edges
    if (pgpcy[pgit]<pgpcy[(pgit+1)%pgpnum]): # positive y direction
      lstarty=int(math.floor((pgpcy[pgit]-args.width/2.)/100.));
      lfinaly=int(math.ceil((pgpcy[(pgit+1)%pgpnum]+args.width/2.)/100.));
      for wfy in range(lstarty+1,lfinaly):
        # print("-> "+str(wfy));
        patchystart=max(100.*wfy-args.width/2,pgpcy[pgit]); # at edge: do not exceed origin polygon
        patchyfinal=min(100.*wfy+args.width/2,pgpcy[(pgit+1)%pgpnum]); # at edge: do not exceed origin polygon
        patchxstart=linearInterpolate(patchystart,pgpcy[pgit],pgpcy[(pgit+1)%pgpnum],pgpcx[pgit],pgpcx[(pgit+1)%pgpnum])-args.extrusion;
        patchxfinal=linearInterpolate(patchyfinal,pgpcy[pgit],pgpcy[(pgit+1)%pgpnum],pgpcx[pgit],pgpcx[(pgit+1)%pgpnum])+args.extrusion;
        patchedgey[wfy-starty-1].append([patchxstart,patchystart,patchxfinal,patchyfinal]); # record edge with direction
    elif (pgpcy[pgit]>pgpcy[(pgit+1)%pgpnum]): # negative y direction
      lstarty=int(math.ceil((pgpcy[pgit]+args.width/2.)/100.));
      lfinaly=int(math.floor((pgpcy[(pgit+1)%pgpnum]-args.width/2.)/100.));
      for wfy in range(lfinaly+1,lstarty):
        # print("<- "+str(wfy));
        patchystart=min(100.*wfy+args.width/2,pgpcy[pgit]); # at edge: do not exceed origin polygon
        patchyfinal=max(100.*wfy-args.width/2,pgpcy[(pgit+1)%pgpnum]); # at edge: do not exceed origin polygon
        patchxstart=linearInterpolate(patchystart,pgpcy[pgit],pgpcy[(pgit+1)%pgpnum],pgpcx[pgit],pgpcx[(pgit+1)%pgpnum])-args.extrusion;
        patchxfinal=linearInterpolate(patchyfinal,pgpcy[pgit],pgpcy[(pgit+1)%pgpnum],pgpcx[pgit],pgpcx[(pgit+1)%pgpnum])+args.extrusion;
        patchedgey[wfy-starty-1].append([patchxstart,patchystart,patchxfinal,patchyfinal]); # record edge with direction
    else: # constant y
      lstarty=int(math.floor((pgpcy[pgit]-args.width/2.)/100.));
      lfinaly=int(math.ceil((pgpcy[(pgit+1)%pgpnum]+args.width/2.)/100.));
      if (lstarty+1==lfinaly-1): # at edge, wfy==lstarty+1==lfinaly-1
        # print(" | "+str(lstarty+1));
        patchedgey[lstarty-starty].append([pgpcx[pgit],pgpcy[pgit],pgpcx[(pgit+1)%pgpnum],pgpcy[(pgit+1)%pgpnum]]);
  patchx=[]; # patch coordinates
  patchy=[]; # patch coordinates
  # parse known x patches edges, group continuous edges
  for ptch in patchedgex:
    edgenum=len(ptch);
    if (edgenum==0):
      raise(Exception("Patch Error: empty patchedge group found in x patches => polygon incontinuous."));
    patchedgep=[]; # edge groups in positive direction
    patchedgen=[]; # edge groups in negative direction
    patchedgei=[]; # independent edge groups, they are complete polygons already
    sortedpatchedgep=[]; # edge groups in positive direction sorted by value in the other axis
    sortedpatchedgen=[]; # edge groups in negative direction sorted by value in the other axis
    minxindex=-1;
    minxcache=float('Inf'); # search boundary of edges
    maxxindex=-1;
    maxxcache=-float('Inf'); # search boundary of edges
    for it in range(0,edgenum): # calculation complexity cost: edgenum, benefit: compatible when polygon is inside patch area
      if (ptch[it][0]<minxcache):
        minxindex=it;
        minxcache=ptch[it][0];
      if (ptch[it][0]>maxxcache):
        maxxindex=it;
        maxxcache=ptch[it][0];
    if (minxindex==-1):
      raise(Exception("Patch Error: no minimum x found in patchedges. position around x="+str(ptch[0][0])));
    if (maxxindex==-1):
      raise(Exception("Patch Error: no maximum x found in patchedges. position around x="+str(ptch[0][0])));
    posDirect=True; # start in positive direction
    thepatch=[]; # currently weaving patch
    for it in range(0,edgenum): # pack each patch and submit
      theit=(it+minxindex)%edgenum;
      if (len(thepatch)==0): # initialize
        thepatch=[[ptch[theit][2],ptch[theit][3]],[ptch[theit][0],ptch[theit][1]]]; # currently weaving patchedge group
      else: # parse a new edge
        if (thepatch[0][1]!=ptch[theit][1]): # incontinuous known edges
          # submit patch
          if (posDirect):
            if (thepatch[0][0]==maxxcache):
              posDirect=False;
              patchedgep.append(thepatch);
            else:
              assert thepatch[0][0]==minxcache,"Broken Patch Edge in x Patch Area! Impossible!";
              patchedgei.append(thepatch);
          else:
            if (thepatch[0][0]==minxcache):
              posDirect=True;
              patchedgen.append(thepatch);
            else:
              assert thepatch[0][0]==maxxcache,"Broken Patch Edge in x Patch Area! Impossible!";
              patchedgei.append(thepatch);
          thepatch=[[ptch[theit][2],ptch[theit][3]],[ptch[theit][0],ptch[theit][1]]]; # initialize the next patchedge group
        else:
          thepatch.insert(0,[ptch[theit][2],ptch[theit][3]]); # add known edge
    if (len(thepatch)>0): # submit the rest patch
      if (posDirect):
        if (thepatch[0][0]==maxxcache):
          posDirect=False;
          patchedgep.append(thepatch);
        else:
          assert thepatch[0][0]==minxcache,"Broken Patch Edge in x Patch Area! Impossible!";
          patchedgei.append(thepatch);
      else:
        if (thepatch[0][0]==minxcache):
          posDirect=True;
          patchedgen.append(thepatch);
        else:
          assert thepatch[0][0]==maxxcache,"Broken Patch Edge in x Patch Area! Impossible!";
          patchedgei.append(thepatch);
      thepatch=[];
    sortedpatchedgep=sorted(patchedgep,key=lambda element: element[0][1]);
    sortedpatchedgen=sorted(patchedgen,key=lambda element: element[0][1]);
    assert len(sortedpatchedgep)==len(sortedpatchedgen),"Unpaired Patch Edge! Impossible!";
    for it in range(0,len(sortedpatchedgep)):
      thepolygon=[];
      thepolygon.extend(sortedpatchedgep[it]);
      thepolygon.extend(sortedpatchedgen[it]);
      patchx.append(thepolygon);
    patchx.extend(patchedgei);
  # parse known y patches edges, group continuous edges
  for ptch in patchedgey:
    edgenum=len(ptch);
    if (edgenum==0):
      raise(Exception("Patch Error: empty patchedge group found in y patches => polygon incontinuous."));
    patchedgep=[]; # edge groups in positive direction
    patchedgen=[]; # edge groups in negative direction
    patchedgei=[]; # independent edge groups, they are complete polygons already
    sortedpatchedgep=[]; # edge groups in positive direction sorted by value in the other axis
    sortedpatchedgen=[]; # edge groups in negative direction sorted by value in the other axis
    minyindex=-1;
    minycache=float('Inf'); # search boundary of edges
    maxyindex=-1;
    maxycache=-float('Inf'); # search boundary of edges
    for it in range(0,edgenum): # calculation complexity cost: edgenum, benefit: compatible when polygon is inside patch area
      if (ptch[it][1]<minycache):
        minyindex=it;
        minycache=ptch[it][1];
      if (ptch[it][1]>maxycache):
        maxyindex=it;
        maxycache=ptch[it][1];
    if (minyindex==-1):
      raise(Exception("Patch Error: no minimum y found in patchedges. position around y="+str(ptch[0][1])));
    if (maxyindex==-1):
      raise(Exception("Patch Error: no maximum y found in patchedges. position around y="+str(ptch[0][1])));
    posDirect=True; # start in positive direction
    thepatch=[]; # currently weaving patch
    for it in range(0,edgenum): # pack each patch and submit
      theit=(it+minyindex)%edgenum;
      if (len(thepatch)==0): # initialize
        thepatch=[[ptch[theit][2],ptch[theit][3]],[ptch[theit][0],ptch[theit][1]]]; # currently weaving patchedge group
      else: # parse a new edge
        if (thepatch[0][0]!=ptch[theit][0]): # incontinuous known edges
          # submit patch
          if (posDirect):
            if (thepatch[0][1]==maxycache):
              posDirect=False;
              patchedgep.append(thepatch);
            else:
              assert thepatch[0][1]==minycache,"Broken Patch Edge in y Patch Area! Impossible!";
              patchedgei.append(thepatch);
          else:
            if (thepatch[0][1]==minycache):
              posDirect=True;
              patchedgen.append(thepatch);
            else:
              assert thepatch[0][1]==maxycache,"Broken Patch Edge in y Patch Area! Impossible!";
              patchedgei.append(thepatch);
          thepatch=[[ptch[theit][2],ptch[theit][3]],[ptch[theit][0],ptch[theit][1]]]; # initialize the next patchedge group
        else:
          thepatch.insert(0,[ptch[theit][2],ptch[theit][3]]); # add known edge
    if (len(thepatch)>0): # submit the rest patch
      if (posDirect):
        if (thepatch[0][1]==maxycache):
          posDirect=False;
          patchedgep.append(thepatch);
        else:
          assert thepatch[0][1]==minycache,"Broken Patch Edge in y Patch Area! Impossible!";
          patchedgei.append(thepatch);
      else:
        if (thepatch[0][1]==minycache):
          posDirect=True;
          patchedgen.append(thepatch);
        else:
          assert thepatch[0][1]==maxycache,"Broken Patch Edge in y Patch Area! Impossible!";
          patchedgei.append(thepatch);
      thepatch=[];
    sortedpatchedgep=sorted(patchedgep,key=lambda element: element[0][0]);
    sortedpatchedgen=sorted(patchedgen,key=lambda element: element[0][0]);
    assert len(sortedpatchedgep)==len(sortedpatchedgen),"Unpaired Patch Edge! Impossible!";
    for it in range(0,len(sortedpatchedgep)):
      thepolygon=[];
      thepolygon.extend(sortedpatchedgep[it]);
      thepolygon.extend(sortedpatchedgen[it]);
      patchy.append(thepolygon);
    patchy.extend(patchedgei);
  # output
  for ptch in patchx:
    print("<polygon id=\"patch%d\" style=\"opacity:0.5;fill:#ff7f2a\" points=\"" % (patchnum+args.idstart),end='');
    # return to area coordinates
    ptch=[[float(it[0])+args.shift[0]-50.,float(it[1])+args.shift[1]-50.] for it in ptch];
    # return to svg coordinates
    ptch=[[float(it[0]),1052.3622047-float(it[1])] for it in ptch];
    print(' '.join([','.join([str(it[0]),str(it[1])]) for it in ptch]),end='');
    print("\" />");
    patchnum+=1;
  for ptch in patchy:
    print("<polygon id=\"patch%d\" style=\"opacity:0.5;fill:#ff7f2a\" points=\"" % (patchnum+args.idstart),end='');
    # return to area coordinates
    ptch=[[float(it[0])+args.shift[0]-50.,float(it[1])+args.shift[1]-50.] for it in ptch];
    # return to svg coordinates
    ptch=[[float(it[0]),1052.3622047-float(it[1])] for it in ptch];
    print(' '.join([','.join([str(it[0]),str(it[1])]) for it in ptch]),end='');
    print("\" />");
    patchnum+=1;
  return patchnum;

for rt in rts:
  rtx=float(rt.getAttribute("x"));
  rty=float(rt.getAttribute("y"));
  rtw=float(rt.getAttribute("width"));
  rth=float(rt.getAttribute("height"));
  rid=rt.getAttribute("id");
  if (rid=='mainarea'): # 900 x 900 area
    continue;
  if ('corner' in rid): # corner mark for area border
    continue;
  if ('patch' in rid): # patches do not want to be patched again
    continue;
  # Fix svg cood: (1,-1) * All cood + (0,1052.3622)
  rty=1052.3622047-rty-rth;
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
    patchy=patchymax+args.shift[1]-50.;
    # return to svg coordinates
    patchy=1052.3622047-patchy;
    # output
    print("<rect id=\"patch%d\" style=\"opacity:0.5;fill:#ff7f2a\" width=\"%.7f\" height=\"%.7f\" x=\"%.7f\" y=\"%.7f\" />" % (patchnum+args.idstart,patchwidth,patchheight,patchx,patchy));
    patchnum+=1;
  for wfy in range(starty+1,finaly):
    patchymin=max(100.*wfy-args.width/2,rtymin); # at edge: do not exceed origin rectangle
    patchymax=min(100.*wfy+args.width/2,rtymax); # at edge: do not exceed origin rectangle
    patchxmin=rtxmin-args.extrusion;
    patchxmax=rtxmax+args.extrusion;
    patchwidth=patchxmax-patchxmin;
    patchheight=patchymax-patchymin;
    # return to area coordinates
    patchx=patchxmin+args.shift[0]-50.;
    patchy=patchymax+args.shift[1]-50.;
    # return to svg coordinates
    patchy=1052.3622047-patchy;
    # output
    print("<rect id=\"patch%d\" style=\"opacity:0.5;fill:#ff7f2a\" width=\"%.7f\" height=\"%.7f\" x=\"%.7f\" y=\"%.7f\" />" % (patchnum+args.idstart,patchwidth,patchheight,patchx,patchy));
    patchnum+=1;
for pg in pgs: # polygons
  pgid=pg.getAttribute("id");
  if ('patch' in pgid): # patches do not want to be patched again
    continue;
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
  patchnum=polygonProcess(pgpcps,patchnum);
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
    patchnum=polygonProcess(pgpcps,patchnum);
