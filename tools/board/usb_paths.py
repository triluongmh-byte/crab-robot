#!/usr/bin/env python3
"""Host numpy: local A* search against actual pad polygons, fixed tracks and holes.

Independent obstacle rasters use every CPU; routing is sequential because new
paths become obstacles. This is a repair helper, not a substitute for native DRC.
"""
import concurrent.futures,heapq,json,math,os,pathlib
import numpy as np
R=pathlib.Path(__file__).resolve().parents[2];C=R/'build/board/usb-relocation'
obs=json.loads((C/'obstacles.json').read_text());step=.15
xs=np.arange(-43.3,43.31,step);ys=np.arange(-30.3,30.31,step)
nx,ny=len(xs),len(ys)
def raster(net,rad,layer):
 blocked=np.zeros((ny,nx),bool)
 for o in obs:
  if o['layer']!=layer or o['net']==net:continue
  pts=o.get('poly',o.get('line'));r=rad+.2+.08+o.get('radius',0)
  if o['net']=='HOLE':r=rad+.25+.08
  if o['net']=='KEEPOUT':r=rad+.08
  pts=np.array(pts);left,bottom=pts.min(axis=0)-r;right,top=pts.max(axis=0)+r
  ix0=max(0,int((left-xs[0])/step));ix1=min(nx,int((right-xs[0])/step)+2)
  iy0=max(0,int((bottom-ys[0])/step));iy1=min(ny,int((top-ys[0])/step)+2)
  if ix1<=ix0 or iy1<=iy0:continue
  X,Y=np.meshgrid(xs[ix0:ix1],ys[iy0:iy1]);hit=np.zeros_like(X,bool);inside=np.zeros_like(X,bool)
  edges=list(zip(pts,np.roll(pts,-1,axis=0))) if 'poly' in o else [(pts[0],pts[1])]
  for a,z in edges:
   dx,dy=z-a;den=dx*dx+dy*dy
   u=np.clip(((X-a[0])*dx+(Y-a[1])*dy)/max(den,1e-20),0,1)
   hit|=(X-a[0]-u*dx)**2+(Y-a[1]-u*dy)**2<=r*r
   if 'poly' in o and abs(dy)>1e-10:
    inside^=((a[1]>Y)!=(z[1]>Y))&(X<(dx*(Y-a[1])/dy+a[0]))
  blocked[iy0:iy1,ix0:ix1]|=hit|inside
 return blocked
def route(net,a,z,width):
 tasks=[(width/2,l) for l in [0,2]]+[(.3,l) for l in [0,2]]
 with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
  masks=list(ex.map(lambda t:raster(net,*t),tasks))
 # Via sites require both copper layers to have a full 0.6 mm clearance disc.
 via=~(masks[2]|masks[3]);bad=masks[:2]
 def node(q):return (q[2],int(round((q[1]-ys[0])/step)),int(round((q[0]-xs[0])/step)))
 start,goal=node(a),node(z)
 for q in [start,goal]:
  assert not bad[q[0]][q[1],q[2]],(net,'endpoint blocked',q)
 def h(q):return math.hypot(q[1]-goal[1],q[2]-goal[2])*step
 todo=[(h(start),0,start)];cost={start:0};prev={};n=0
 dirs=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
 while todo:
  _,g,q=heapq.heappop(todo)
  if g!=cost[q]:continue
  if q==goal:break
  l,y,x=q;n+=1
  options=[]
  for dy,dx in dirs:
   yy,xx=y+dy,x+dx
   if 0<=yy<ny and 0<=xx<nx and not bad[l][yy,xx]:
    if dy and dx and (bad[l][y,xx] or bad[l][yy,x]):continue
    options.append(((l,yy,xx),step*math.hypot(dx,dy)))
  if via[y,x]:options.append(((1-l,y,x),5.0))
  for w,dc in options:
   ng=g+dc
   if ng<cost.get(w,math.inf):cost[w]=ng;prev[w]=q;heapq.heappush(todo,(ng+h(w),ng,w))
 else:raise RuntimeError((net,'no path',n))
 path=[goal]
 while path[-1]!=start:path.append(prev[path[-1]])
 path.reverse();simple=[path[0]]
 for i in range(1,len(path)-1):
  d0=tuple(path[i][j]-path[i-1][j] for j in range(3));d1=tuple(path[i+1][j]-path[i][j] for j in range(3))
  if d0!=d1:simple.append(path[i])
 simple.append(path[-1]);pts=[[round(float(xs[x]),5),round(float(ys[y]),5),l] for l,y,x in simple]
 pts=[list(a)]+pts+[list(z)]
 for aa,zz in zip(pts,pts[1:]):
  if aa[2]==zz[2]:obs.append({'net':net,'layer':[0,2][aa[2]],'line':[aa[:2],zz[:2]],'radius':width/2})
  else:
   for lay in [0,2]:obs.append({'net':net,'layer':lay,'line':[aa[:2],aa[:2]],'radius':.3})
 print(net,'route',round(cost[goal],2),'mm + via penalty;',n,'nodes;',len(pts),'corners',flush=True)
 return {'net':net,'width':width,'points':pts}
paths=[]
for args in [
 ('USB_DM',(22.2,-25.1921,1),(-36.3307,-8.51,1),.2),
 ('USB_CC2',(19.7,-25.1974,1),(-34.8493,2.961,1),.2),
 ('PB1_5V',(19,-22.5,1),(23.8505,-22.6746,1),.6),
]:
 paths.append(route(*args))
 (C/'paths.json').write_text(json.dumps(paths,indent=2)+'\n')
(C/'paths.json').write_text(json.dumps(paths,indent=2)+'\n')
