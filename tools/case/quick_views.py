"""Shaded orthographic PNG views of the assembled STL set (inspection + overview images).
usage: quick_views.py OUT.png [part-name-substring ...]"""
import sys, json, math
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/robot'
COL = {'frame_lower': '#d6cfc1', 'frame_upper': '#eee9df', 'thigh': '#9ebcca', 'foot': '#7fa3b4',
       'electronics': '#4c806c', 'servos': '#5a7fb0', 'hardware': '#596872', 'coupon': '#e0a060', 'MATING': '#9ebcca'}

def load(name):
    d = (OUT / f'{name}.stl').read_bytes(); n = int.from_bytes(d[80:84], 'little')
    a = np.frombuffer(d[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n)
    return a['v'].reshape(-1, 3, 3).astype(float)

def color(name):
    for k, v in COL.items():
        if k in name: return v
    return '#cccccc'

def view(ax, tris_by, R, title):
    polys, cols, depth = [], [], []
    L = np.array([0.3, -0.5, 0.8]); L /= np.linalg.norm(L)
    for name, T in tris_by:
        P = T @ R.T
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); nn = np.linalg.norm(n, axis=1); ok = nn > 1e-9
        n = n[ok] / nn[ok, None]; P = P[ok]
        front = n[:, 2] > 0
        P, n = P[front], n[front]
        shade = 0.45 + 0.55 * np.clip(n @ (R @ L), 0, 1)
        base = np.array(matplotlib.colors.to_rgb(color(name)))
        polys += list(P[:, :, :2]); cols += list(np.clip(base[None, :] * shade[:, None], 0, 1)); depth += list(P[:, :, 2].mean(1))
    o = np.argsort(depth)
    ax.add_collection(PolyCollection([polys[i] for i in o], facecolors=[cols[i] for i in o], edgecolors='none'))
    ax.autoscale(); ax.set_aspect('equal'); ax.set_title(title); ax.axis('off')

def rot(yaw, pitch):
    a, b = math.radians(yaw), math.radians(pitch)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    return Rx @ Rz

if __name__ == '__main__':
    man = json.loads((OUT / 'parts.json').read_text())
    sel = sys.argv[2:]
    names = [p['name'] for p in man['parts'] if p['role'] != 'coupon' and (not sel or any(s in p['name'] for s in sel))]
    tb = [(n, load(n)) for n in names]
    fig, axs = plt.subplots(1, 3, figsize=(21, 7))
    view(axs[0], tb, np.eye(3), 'Từ trên (top)')
    view(axs[1], tb, np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]]), 'Từ trước (front, nhìn theo -X)')
    view(axs[2], tb, rot(-35, -60), 'Iso')
    plt.tight_layout(); plt.savefig(sys.argv[1], dpi=70)
