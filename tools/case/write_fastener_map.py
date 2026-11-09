"""case/fastener_map.csv from case/hardware.py (the same instances the checks and overview use)."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'case'))
import hardware as HW
with open(ROOT / 'case/fastener_map.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'size', 'owned_type', 'nut', 'step', 'head_x', 'head_y', 'head_z', 'entry', 'joins', 'tool', 'action'])
    for h in HW.instances():
        w.writerow([h['id'], h['size'], 'M3 (bộ vít của chủ)' if h['kind'] == 'M3' else 'vít trong túi SG90',
                    'tán M3' if h.get('nut') else '', h['step'] if h['kind'] == 'M3' else h['step'],
                    *[f'{v:.1f}' for v in h['head']], h['entry'], ' + '.join(h['parts']),
                    'tua vít PH1/lục giác 2.5' if h['kind'] == 'M3' else 'tua vít PH0 nhỏ', h['action']])
print('wrote case/fastener_map.csv')
