"""case/overview.html: self-contained WebGL overview built from the exported case/out STL files.

  "$KICAD_CASE_PYTHON" tools/case/render_overview.py
Moving legs use the same pivots as case/geometry.py (hip axis = shaft, knee axis = SG90 shaft).
"""
import base64, hashlib, json, math, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/out'
sys.path.insert(0, str(ROOT / 'case'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plates import read_stl  # noqa: E402

Q = 0.02  # mm per int16 unit


def enc(tris):
    q = np.clip(np.round(tris.reshape(-1, 3) / Q), -32767, 32767).astype('<i2')
    return base64.b64encode(q.tobytes()).decode()


def edges(tris, deg=35.0):
    """Feature edges (crease > deg or boundary) as int16 segment pairs."""
    t = np.round(tris, 4)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1; n = n / ln
    em = {}
    for i, tri in enumerate(t):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            k = tuple(sorted((tuple(tri[a]), tuple(tri[b]))))
            em.setdefault(k, []).append(i)
    segs = []
    c = math.cos(math.radians(deg))
    for k, fs in em.items():
        if len(fs) == 1 or (len(fs) == 2 and float(np.dot(n[fs[0]], n[fs[1]])) < c):
            segs.append(k)
    return enc(np.array(segs, dtype=float)) if segs else ''


def tess(w):
    import cadquery as cq
    import tempfile, os
    fd, p = tempfile.mkstemp(suffix='.stl'); os.close(fd)
    cq.exporters.export(w, p, tolerance=0.08, angularTolerance=0.3)
    t = read_stl(p); os.unlink(p)
    return t


def main():
    import geometry as g, refs
    manifest = json.loads((OUT / 'parts.json').read_text())
    meshes = []

    def add(mid, tris, role, label, group, leg=None, link=None):
        meshes.append(dict(id=mid, role=role, label=label, group=group, leg=leg, link=link, tri=enc(tris), edge=edges(tris)))

    prod = {p['name']: p for p in manifest['parts']}
    add('P01_day', read_stl(OUT / 'P01_day.stl'), 'frame', 'P01 Đáy', 'body')
    add('P02_nap', read_stl(OUT / 'P02_nap.stl'), 'cover', 'P02 Nắp', 'lid')
    add('P03_thanh_de_truoc', read_stl(OUT / 'P03_thanh_de_truoc.stl'), 'frame2', 'P03 Thanh đè trước', 'body')
    add('P04_thanh_de_sau', read_stl(OUT / 'P04_thanh_de_sau.stl'), 'frame2', 'P04 Thanh đè sau', 'body')
    num = {'FL': (5, 9), 'FR': (6, 10), 'RL': (7, 11), 'RR': (8, 12)}
    for leg, (a, b) in num.items():
        add(f'P0{a}_dui_{leg}', read_stl(OUT / f'P0{a}_dui_{leg}.stl'), 'moving', f'P0{a} Đùi {leg}', 'leg', leg, 'femur')
        add(f'P{b:02d}_cang_{leg}', read_stl(OUT / f'P{b:02d}_cang_{leg}.stl'), 'moving2', f'P{b:02d} Cẳng {leg}', 'leg', leg, 'tibia')
    for k, w in refs.hip_servos().items():
        add('SG90_' + k, tess(w), 'servo', f'SG90 hông {k[:2]}', 'servo')
    for k, w in refs.knee_servos().items():
        add('SG90_' + k, tess(w), 'servo', f'SG90 gối {k[:2]}', 'servo', k[:2], 'femur')
    for k, w in refs.horns().items():
        add('HORN_' + k, tess(w), 'horn', f'horn {k}', 'servo', k[:2], 'femur' if 'hip' in k else 'tibia')
    for k, w in g.modules_ref().items():
        add(k, tess(w), 'elec' if k != 'POWER_BANK' else 'pack', k, 'elec')
    legs = {n: dict(hip=[v[2][0], v[2][1]], ang=v[3], sx=v[0], sy=v[1]) for n, v in g.LEGS.items()}
    fast = g.fasteners()
    data = dict(q=Q, meshes=meshes, legs=legs, knee=dict(r=g.LEG_R_KNEE, z=g.KNEE_AXIS_Z), fasteners=fast,
                range=dict(hip=30, knee=30),
                wires=[
                    dict(id='W1', label='Cáp L USB-A→USB-C (cổng 1 → LILYGO)', color='#1d1d1d', pts=[[-45, 19, 10], [-44, 19, 20], [-44, 19, 36], [-36, 19, 36]]),
                    dict(id='W2', label='Cáp USB-A→2 dây (cổng 2 → terminal PCA)', color='#c62828', pts=[[-45, -19, 10], [-44, -19, 20], [-44, -19, 26], [-30, -6, 26], [0, -6, 26]]),
                    dict(id='W3', label='Dupont I²C + 3V + GND (LILYGO → PCA)', color='#1565c0', pts=[[0, 7.5, 21], [0, 7.5, 19.5], [33, 7.5, 19.5], [36, 7.5, 24], [36, -10, 26], [31, -12, 26]]),
                    dict(id='W4', label='Dây servo hông (→ PCA ch0/2/4/6)', color='#ef6c00', pts=[[50, 5, 23], [40, 0, 23], [20, -1, 23], [10, -9, 28]]),
                    dict(id='W5', label='Dây servo gối, vòng dư qua khớp hông', color='#ef6c00', pts=[[72, 42, 26], [60, 40, 40], [45, 37, 42], [36, 36, 41], [20, -12, 40]]),
                ])
    steps = [
        dict(t='Bước 1 — Pin dự phòng vào hầm', show=['body0', 'pack'], parts=['P01_day', 'POWER_BANK'], hw=[],
             act='Đẩy pin từ đầu trước (+X) vào hầm dưới kệ, cổng USB quay về đầu sau. Luồn dây rút/dây dán qua 2 khe đáy (x≈52) và rãnh dưới kệ, siết vừa tay.'),
        dict(t='Bước 2 — 4 servo hông vào hốc', show=['body0', 'pack', 'hips'], parts=['P01_day', 'SG90_FL_hip', 'SG90_FR_hip', 'SG90_RL_hip', 'SG90_RR_hip'], hw=[],
             act='Thả mỗi SG90 vào hốc, trục quay lên trên và ra mép ngoài, tai nằm lên vách. Dây luồn qua khe dưới vách trong.'),
        dict(t='Bước 3 — Thanh đè trước + sau (4 vít M3×12)', show=['body0', 'pack', 'hips', 'bars'], parts=['P03_thanh_de_truoc', 'P04_thanh_de_sau'], hw=['S01', 'S02', 'S03', 'S04'],
             act='Đẩy 4 tán M3 vào khe ngang ở vách trong (từ phía giữa thân). Đặt thanh đè lên tai servo, vặn 4 vít M3×12 từ trên xuống.'),
        dict(t='Bước 4 — LILYGO, PCA9685, đèn LED', show=['body0', 'pack', 'hips', 'bars', 'elec'], parts=['LILYGO_TDISPLAY_S3', 'PCA9685', 'LED_BAR_WS2812_KK10'], hw=[],
             act='PCA vào ô viền (hàng chân servo về phía ngoài, terminal xanh vào trong). Cắm sẵn dây Dupont vào LILYGO, dây đi xuống rãnh của kệ rồi ra đầu trước (x≈33). Úp LILYGO lên sống đỡ, cổng USB-C về sau, đầu trước chạm gờ chặn; nắp sẽ ép board xuống. Thanh LED vào rãnh trên cầu, 1 dây rút nhỏ ở giữa.'),
        dict(t='Bước 5 — Cắm dây (xem firmware/WIRING.md)', show=['body0', 'pack', 'hips', 'bars', 'elec', 'wires'], parts=[], hw=[],
             act='Cắm cáp L vào LILYGO, cáp 2 dây vào terminal PCA (đỏ V+, đen GND), Dupont I²C/3V/GND, đèn, 8 giắc servo. Không cắm pin lúc này.'),
        dict(t='Bước 6 — Đóng nắp (4 vít M3×20)', show=['body', 'pack', 'hips', 'elec', 'lid'], parts=['P02_nap'], hw=['S05', 'S06', 'S07', 'S08'],
             act='Đặt 4 tán vào khe còn lại. Đặt nắp (cửa sổ màn hình trên LILYGO). Vặn 4 vít M3×20 xuyên nắp + thanh đè vào tán.'),
        dict(t='Bước 7 — Servo gối vào đùi', show=['body', 'pack', 'hips', 'elec', 'lid', 'femur'], parts=['P05_dui_FL', 'P06_dui_FR', 'P07_dui_RL', 'P08_dui_RR'], hw=['FT'],
             act='Đẩy SG90 vào hộp của đùi từ phía có horn, trục nằm ngang ở phía trên. Bắt 2 vít tai đi kèm túi SG90.'),
        dict(t='Bước 8 — Về 90° (trang /rap), gắn đùi lên horn hông', show=['body', 'pack', 'hips', 'elec', 'lid', 'femur', 'horns'], parts=['P05_dui_FL', 'P06_dui_FR', 'P07_dui_RL', 'P08_dui_RR'], hw=['FH'],
             act='Mở trang Ráp, bấm "về giữa". Ép horn vào rãnh dưới đùi, chân nằm chéo 45°. Cắm horn lên trục, vặn vít tâm horn qua lỗ Ø6.'),
        dict(t='Bước 9 — Gắn cẳng vào horn gối', show=['all'], parts=['P09_cang_FL', 'P10_cang_FR', 'P11_cang_RL', 'P12_cang_RR'], hw=['FK'],
             act='Ép horn gối vào rãnh cẳng, cẳng chĩa xuống ra ngoài. Cắm lên trục gối, vặn vít tâm. Để vòng dây dư quanh khớp hông.'),
    ]
    factory = {
        'FT': dict(id='FT01–FT08', size='vít tai SG90 (túi servo, ~M2 tự ren)', n=8, nut='không', entry='ngang, từ phía horn (+t)', note='2 vít mỗi servo gối'),
        'FH': dict(id='FH1–FH4', size='vít tâm horn SG90 (túi servo)', n=4, nut='không', entry='từ trên xuống qua lỗ Ø6 của đùi', note='horn hông'),
        'FK': dict(id='FK1–FK4', size='vít tâm horn SG90 (túi servo)', n=4, nut='không', entry='ngang qua lỗ Ø6 của cẳng', note='horn gối'),
    }
    data.update(steps=steps, factory=factory, revision=manifest['revision'])
    html = (Path(__file__).resolve().parent / 'overview_template.html').read_text()
    html = html.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    (ROOT / 'case/overview.html').write_text(html)
    print('overview.html', round(len(html) / 1e6, 2), 'MB', len(meshes), 'meshes')


if __name__ == '__main__':
    main()
