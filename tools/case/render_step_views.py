"""Quick orthographic depth renders of a STEP (top/bottom/side) for inspection. Read-only."""
import sys, numpy as np
import cadquery as cq
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
shape = cq.importers.importStep(sys.argv[1]); out = sys.argv[2]
tris = []
for si, s in enumerate(shape.solids().vals()):
    vs, ts = s.tessellate(0.05, 0.2)
    V = np.array([(v.x, v.y, v.z) for v in vs])
    for t in ts:
        tris.append((si, V[list(t)]))
fig, axs = plt.subplots(1, 3, figsize=(18, 8))
cols = ['tab:gray', 'tab:blue', 'tab:green', 'tab:red', 'tab:orange']
for ax, (name, a, b, d, sgn) in zip(axs, [('top +Z', 0, 1, 2, 1), ('bottom -Z', 0, 1, 2, -1), ('side +X', 1, 2, 0, 1)]):
    polys, colors, depth = [], [], []
    for si, T in tris:
        n = np.cross(T[1] - T[0], T[2] - T[0]); nn = np.linalg.norm(n)
        if nn == 0: continue
        n /= nn
        if n[d] * sgn <= 0: continue
        polys.append(T[:, [a, b]] * ([-1, 1] if sgn < 0 and d == 2 else [1, 1]))
        shade = 0.4 + 0.6 * abs(n[d])
        c = np.array(matplotlib.colors.to_rgb(cols[si % 5])) * shade
        colors.append(c); depth.append(T[:, d].mean() * sgn)
    order = np.argsort(depth)
    ax.add_collection(PolyCollection([polys[i] for i in order], facecolors=[colors[i] for i in order], edgecolors='none'))
    ax.autoscale(); ax.set_aspect('equal'); ax.set_title(name); ax.grid(True, lw=0.3)
plt.tight_layout(); plt.savefig(out, dpi=80)
