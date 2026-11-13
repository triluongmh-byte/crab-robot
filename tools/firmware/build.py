#!/usr/bin/env python3
"""Compile named targets with the shared toolchain, all CPUs and verified cache.
No downloads, uploads, port enumeration or hardware access.
"""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
RECIPES = {'lilygo': ('flash.json', 'BUILD.json'),
           'integrated': ('flash-integrated.json', 'BUILD-integrated.json')}
RELEASE_TIP = '4cadb190eb0b3a92a9e7805c9956f41af7b085d71a2e18de54edbae19829277c'
IMPLEMENTED_NOTES = [10,11,12,13,14,15,16,17,18]

def release_metadata():
    return {'applicationProfile':'positional180-v13','releaseChainTip': RELEASE_TIP, 'implementedFirmwareNotes': IMPLEMENTED_NOTES,
            'ownerEvidence': 'firmware/OWNER-EVIDENCE.json'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build(target, toolchain):
    recipe_name, manifest_name = RECIPES[target]
    recipe_path = ROOT/'firmware'/recipe_name
    recipe = json.loads(recipe_path.read_text())
    paths = [p for p in (ROOT/'firmware/crab').glob('*') if p.is_file()] + [recipe_path]
    sources = {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}
    digest = hashlib.sha256(json.dumps({'sources': sources, 'toolchain': toolchain}, sort_keys=True).encode()).hexdigest()
    out = (ROOT/'firmware'/recipe['build']).resolve()
    assert out.is_relative_to(ROOT/'build/firmware')
    out.mkdir(parents=True, exist_ok=True)
    manifest = ROOT/'firmware'/manifest_name
    previous = json.loads(manifest.read_text()) if manifest.exists() else {}
    artifacts = previous.get('artifacts', {})
    unchanged = (previous.get('sourceDigest') == digest and 'crab.ino.bin' in artifacts
        and all((out/n).is_file() and (out/n).stat().st_size == r['bytes']
                and sha(out/n) == r['sha256'] for n, r in artifacts.items()))
    if unchanged:
        # Documentation-only notes change release authority, not compiled bytes.
        # Refresh only after every source/config/toolchain/binary hash matches.
        current = dict(previous, **release_metadata())
        if current != previous:
            manifest.write_text(json.dumps(current, indent=2)+'\n')
        print(f'SKIP {target}: sources/config/toolchain and all binary hashes unchanged', flush=True)
        return
    # Each compile uses all CPUs. Targets compile sequentially to avoid competing
    # for Arduino's shared core cache; no nested installation in the worktree.
    subprocess.run(['arduino-cli', 'compile', '--fqbn', recipe['fqbn'],
                    '--build-path', str(out), *recipe.get('compileArgs', ['--jobs', '0']),
                    str(ROOT/'firmware'/recipe['sketch'])], cwd=ROOT, check=True)
    artifacts = {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(out.glob('*.bin'))}
    assert all(n in artifacts for n in ['crab.ino.bin', 'crab.ino.bootloader.bin', 'crab.ino.partitions.bin'])
    manifest.write_text(json.dumps({'target': target, 'hardwareTested': False,
        **release_metadata(),
        'interfaceStatus': 'final SPI/OE interface; see BOARD-RECONCILIATION.json' if target == 'integrated' else 'LILYGO baseline',
        'sourceDigest': digest, 'sourceInputs': sources, 'toolchain': toolchain,
        'fqbn': recipe['fqbn'], 'compileArgs': recipe.get('compileArgs', []),
        'core': 'esp32 2.0.14', 'output': str(out.relative_to(ROOT)), 'artifacts': artifacts}, indent=2)+'\n')
    print(f'BUILT {target}: {artifacts["crab.ino.bin"]["bytes"]} bytes', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=[*RECIPES, 'all'], default='lilygo')
    args = parser.parse_args()
    platforms = json.loads(subprocess.check_output(['arduino-cli', 'core', 'list', '--format', 'json']))['platforms']
    installed = {p['id']: p['installed_version'] for p in platforms if p.get('installed_version')}
    if installed.get('esp32:esp32') != '2.0.14':
        raise SystemExit('Expected shared esp32 core 2.0.14; no automatic core installation')
    toolchain = {'cli': subprocess.check_output(['arduino-cli', 'version'], text=True).strip(), 'installedCores': installed}
    for target in RECIPES if args.target == 'all' else [args.target]:
        build(target, toolchain)

if __name__ == '__main__':
    main()
