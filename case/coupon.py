"""C01 TEST ONLY coupon: one real hip servo pocket (cut from P01), its M3x12 hole + nut slot,
the hip horn groove (same profile as the femur) and the slimmest post (LED bridge pillar)."""
import cadquery as cq
import geometry as g


def coupon():
    chunk = g.bottom().intersect(g.box(40.6, 63.0, 0.0, 37.5, g.SHELF_Z0, g.TAB_Z1))
    plate = g.box(14.0, 40.7, 2.0, 37.5, g.SHELF_Z0, g.SHELF_Z0 + 8.0)
    # horn groove on top of the plate, same outline/depth as the leg parts
    plate = plate.cut(g.horn_outline(g.GROOVE).translate((19.0, 12.0, g.SHELF_Z0 + 8.0 - g.GROOVE)))
    plate = plate.cut(g.cyl(19.0, 12.0, g.SHELF_Z0 - 1, g.SHELF_Z0 + 9, 6.0))
    for d in (10.0, 15.0):
        plate = plate.cut(g.cyl(19.0 + d, 12.0, g.SHELF_Z0 + 2.0, g.SHELF_Z0 + 9, 1.6))
    # slimmest post of the kit: LED bridge pillar 8 x 10.85, same height, standing in print direction
    pillar = g.rbox(16.0, 24.0, 22.0, 32.85, g.SHELF_Z0 + 7.99, g.SHELF_Z0 + 8.0 + 18.85, 2.0)
    c = chunk.union(plate).union(pillar)
    try:
        txt = (cq.Workplane('XY').text('TEST ONLY', 4.0, 0.8, kind='bold')
               .translate((27.0, 32.0, g.SHELF_Z0 + 8.0)))
        c = c.union(txt)
    except Exception:
        c = c.cut(g.box(25.0, 39.0, 30.0, 34.0, g.SHELF_Z0 + 7.4, g.SHELF_Z0 + 8.1))
    return c
