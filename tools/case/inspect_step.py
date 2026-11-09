"""List the solids of a vendor STEP (bounding boxes, volumes) - read-only inspection helper."""
import sys
import cadquery as cq
shape = cq.importers.importStep(sys.argv[1])
bb = shape.val().BoundingBox()
print('ALL', [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
for i, s in enumerate(shape.solids().vals()):
    b = s.BoundingBox()
    print(i, round(s.Volume(), 1), [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
