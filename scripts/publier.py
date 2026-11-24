#!/usr/bin/env python3
"""Construit les modules et les manifestes de dist/, et publie une release GitHub.

Usage :
  python3 scripts/publier.py 1.0.0                     construit dist/ (rien n'est publié)
  python3 scripts/publier.py 1.0.0 --pdf CHEMIN.pdf    ajoute un PDF aux assets (répétable)
  python3 scripts/publier.py 1.0.0 --publier           crée le tag et la release avec gh (demande confirmation)

Une release contient, pour chaque module présent (fr/, en/) : <slug>.module et <slug>.json (manifeste, adresse de téléchargement du tag), plus les PDF.
Le recommends du système pointe vers https://github.com/BriocheMasquee/sotdl-help/releases/latest/download/<slug>.json
Tags : X.X.X, sans « v ». La version doit être celle de module.json."""
import argparse, json, os, re, subprocess, sys, zipfile
RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEPOT = 'BriocheMasquee/sotdl-help'
MODULES = {'fr': 'aide-osd', 'en': 'help-sotdl'}   # dossier -> slug (= id du module)
a = argparse.ArgumentParser(); a.add_argument('version'); a.add_argument('--pdf', action='append', default=[]); a.add_argument('--publier', action='store_true')
o = a.parse_args()
if not re.fullmatch(r'\d+\.\d+\.\d+', o.version): sys.exit('Version attendue : X.X.X (sans « v »)')
dist = os.path.join(RACINE, 'dist'); os.makedirs(dist, exist_ok=True)
for f in os.listdir(dist): os.remove(os.path.join(dist, f))
assets = []; erreurs = []
for dossier, slug in MODULES.items():
    d = os.path.join(RACINE, dossier, 'module.json')
    if not os.path.isfile(d): print(f'  {dossier}/ : absent, ignoré'); continue
    m = json.load(open(d, encoding='utf-8'))
    if m.get('id') != slug: erreurs.append(f'{dossier}/module.json : id « {m.get("id")} » (attendu « {slug} »)')
    if m.get('version') != o.version: erreurs.append(f'{dossier}/module.json : version « {m.get("version")} » (attendue « {o.version} »)')
    if erreurs: continue
    archive = os.path.join(dist, slug + '.module')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, ds, fs in os.walk(os.path.join(RACINE, dossier)):
            ds[:] = [x for x in ds if not x.startswith('.')]
            for fn in fs:
                if fn.startswith('.') or re.search(r' \d+(\.[^.]+)?$', fn): continue   # fichiers dupliqués par la synchronisation iCloud (« nom 2.ext »)
                p = os.path.join(r, fn); z.write(p, os.path.relpath(p, os.path.join(RACINE, dossier)))
    manifeste = {'id': slug, 'name': m['name'], 'type': 'module', 'version': o.version, 'description': m.get('descr') or m.get('shortDescr', ''),
                 'download': f'https://github.com/{DEPOT}/releases/download/{o.version}/{slug}.module', 'compatibility': {'minimum': '5.2.0'}}
    mf = os.path.join(dist, slug + '.json'); open(mf, 'w', encoding='utf-8').write(json.dumps(manifeste, ensure_ascii=False, indent=2) + '\n')
    assets += [archive, mf]; print(f'  {slug} : {os.path.getsize(archive) // 1024} Ko')
if erreurs: sys.exit('\n'.join(erreurs))
if not assets: sys.exit('Aucun module à publier.')
for p in o.pdf:
    if not os.path.isfile(p): sys.exit('PDF introuvable : ' + p)
    import shutil; shutil.copy(p, dist); assets.append(os.path.join(dist, os.path.basename(p)))
print('dist/ :', ', '.join(os.path.basename(x) for x in assets))
if not o.publier: print('Rien publié (ajoutez --publier).'); sys.exit(0)
if subprocess.run(['git', '-C', RACINE, 'status', '--porcelain'], capture_output=True, text=True).stdout.strip(): sys.exit('Des modifications ne sont pas commitées : commitez et poussez avant de publier.')
if input(f'Créer le tag et la release {o.version} sur {DEPOT} avec {len(assets)} fichier(s) ? [oui/N] ').strip().lower() != 'oui': sys.exit('Abandon.')
subprocess.run(['git', '-C', RACINE, 'tag', o.version], check=True); subprocess.run(['git', '-C', RACINE, 'push', 'origin', o.version], check=True)
subprocess.run(['gh', 'release', 'create', o.version, *assets, '--repo', DEPOT, '--title', o.version, '--notes', f'Version {o.version}'], check=True)
