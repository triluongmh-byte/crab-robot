"""Orthographic assembly PNGs from the current exported STL geometry; no UI or network."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/case'))
from plates import read_stl

OUT = ROOT/'case/images'
PALETTE = {'P01':(157,171,182),'P02':(70,131,159),'P03':(88,117,135),'P04':(88,117,135),
           'REF_servos':(45,85,155),'REF_modules':(57,119,88),'REF_hardware':(116,123,135)}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest=json.loads((ROOT/'case/out/parts.json').read_text())
    parts=[]
    hashes={}
    for p in manifest['parts']:
        if p['role']=='coupon':continue
        f=ROOT/'case/out'/p['stl']
        hashes[p['stl']]=hashlib.sha256(f.read_bytes()).hexdigest()
        name=p['name']; color=next((v for k,v in PALETTE.items() if name.startswith(k)),(199,146,77))
        parts.append((name,read_stl(f),np.array(color)))
    for view in ['assembled','exploded','top','front']:
        direction={'top':[0,0,1],'front':[1,0,0],
                   'assembled':[1,-1,0.75],'exploded':[1,-1,0.75]}[view]
        z=np.array(direction,dtype=float); z/=np.linalg.norm(z)
        up=np.array([0.,1.,0.]) if view=='top' else np.array([0.,0.,1.])
        x=np.cross(up,z);x/=np.linalg.norm(x); y=np.cross(z,x)
        basis=np.stack([x,y,z],axis=1)
        triangles=[];colors=[]
        for name,t,c in parts:
            t=t.copy()
            if view=='exploded':
                if name.startswith('P02'):t[:,:,2]+=70
                elif name.startswith(('P03','P04')):t[:,:,2]+=30
            q=t@basis
            normals=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
            norms=np.linalg.norm(normals,axis=1)
            mask=(norms>1e-9)&(normals[:,2]>=-1e-8)
            q=q[mask]; normals=normals[mask];norms=norms[mask]
            n=normals/norms[:,None]
            light=np.array([-.25,.4,.88]);light/=np.linalg.norm(light)
            shade=np.clip(.55+.45*np.maximum(0,n@light),.4,1)
            colors.extend(np.clip(c[None,:]*shade[:,None],0,255).astype('uint8').tolist())
            triangles.extend(q)
        t=np.array(triangles); c=np.array(colors)
        xy=t[:,:,:2];lo=xy.reshape(-1,2).min(0);hi=xy.reshape(-1,2).max(0)
        scale=min(1400/(hi-lo)[0],1000/(hi-lo)[1])
        xy=(xy-(lo+hi)/2)*scale
        xy[:,:,0]+=800;xy[:,:,1]=630-xy[:,:,1]
        pixels=np.full((1250,1600,3),(242,245,247),dtype=np.uint8)
        depth=np.full((1250,1600),-np.inf)
        for i,tri in enumerate(xy):
            lo=np.maximum(np.floor(tri.min(0)).astype(int),[0,0])
            hi=np.minimum(np.ceil(tri.max(0)).astype(int),[1599,1249])
            if np.any(hi<lo):continue
            a,b,cc=tri
            den=(b[1]-cc[1])*(a[0]-cc[0])+(cc[0]-b[0])*(a[1]-cc[1])
            if abs(den)<1e-8:continue
            X,Y=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
            u=((b[1]-cc[1])*(X-cc[0])+(cc[0]-b[0])*(Y-cc[1]))/den
            v=((cc[1]-a[1])*(X-cc[0])+(a[0]-cc[0])*(Y-cc[1]))/den
            w=1-u-v
            zval=u*t[i,0,2]+v*t[i,1,2]+w*t[i,2,2]
            region=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
            mask=(u>=0)&(v>=0)&(w>=0)&(zval>region)
            region[mask]=zval[mask]
            pixels[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=c[i]
        im=Image.fromarray(pixels);d=ImageDraw.Draw(im)
        title={'assembled':'ASSEMBLED / neutral','exploded':'EXPLODED / lid +70 mm, clamps +30 mm',
               'top':'TOP / neutral mirror symmetry','front':'FRONT (+X) / neutral'}[view]
        d.text((35,25),'ROBOT CUA A1 V4 - '+title,fill=(25,40,55))
        d.text((35,1210),'Actual final exported meshes. CAD only; physical fit and walking untested.',fill=(25,40,55))
        im.save(OUT/(view+'.png'))
    (OUT/'manifest.json').write_text(json.dumps({'sourceSTLSha256':hashes,'hardwareTested':False},indent=2)+'\n')
    print('Rendered assembled / exploded / top / front from final exported STL geometry.')

if __name__=='__main__':main()
