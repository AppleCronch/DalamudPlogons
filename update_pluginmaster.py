import json
import os
import urllib.error
import urllib.request
import zipfile
import io
from datetime import datetime, timezone
from time import time

TOKEN = os.environ.get('GITHUB_TOKEN', '')
ASSET = 'latest.zip'

# InternalName -> GitHub repo whose latest release carries <InternalName>/latest.zip
SOURCES = {
    'AnoMech': 'AppleCronch/AnoMechElementalStrats',
}

DEFAULTS = {'IsHide': False, 'IsTestingExclusive': False, 'ApplicableVersion': 'any'}
TRIMMED_KEYS = [
    'Author', 'Name', 'Punchline', 'Description', 'Changelog', 'InternalName', 'AssemblyVersion',
    'RepoUrl', 'ApplicableVersion', 'Tags', 'DalamudApiLevel', 'IconUrl', 'ImageUrls',
]


def get(url, accept=None):
    req = urllib.request.Request(url)
    if accept:
        req.add_header('Accept', accept)
    if TOKEN and 'api.github.com' in url:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def sync_manifest(name, repo):
    path = os.path.join('plugins', name, f'{name}.json')
    try:
        data = get(f'https://github.com/{repo}/releases/latest/download/{ASSET}')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            manifest = json.loads(z.read(f'{name}.json').decode('utf-8-sig'))
    except (urllib.error.URLError, KeyError, zipfile.BadZipFile) as e:
        print(f'{name}: no usable release in {repo} ({e}); keeping committed manifest')
        return
    manifest['RepoUrl'] = f'https://github.com/{repo}'
    manifest['IconUrl'] = f'https://raw.githubusercontent.com/{repo}/master/images/icon.png'
    manifest.pop('Changelog', None)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4)
        f.write('\n')
    print(f'{name}: synced v{manifest.get("AssemblyVersion")} from {repo}')


def release_stats(repo):
    count, last = 0, 0
    try:
        releases = json.loads(get(f'https://api.github.com/repos/{repo}/releases?per_page=100',
                                  'application/vnd.github+json'))
    except urllib.error.URLError:
        return 0, 0
    for rel in releases:
        for asset in rel.get('assets', []):
            if asset.get('name') == ASSET:
                count = max(count, int(asset.get('download_count', 0)))
        if rel.get('published_at'):
            ts = datetime.strptime(rel['published_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            last = max(last, int(ts.timestamp()))
    return count, last


def main():
    master = []
    for name, repo in sorted(SOURCES.items()):
        sync_manifest(name, repo)
        with open(os.path.join('plugins', name, f'{name}.json'), encoding='utf-8') as f:
            manifest = {k: v for k, v in json.load(f).items() if k in TRIMMED_KEYS}
        url = f'https://github.com/{repo}/releases/latest/download/{ASSET}'
        for k, v in DEFAULTS.items():
            manifest.setdefault(k, v)
        manifest['DownloadLinkInstall'] = manifest['DownloadLinkTesting'] = manifest['DownloadLinkUpdate'] = url
        count, last = release_stats(repo)
        manifest['DownloadCount'] = count
        manifest['LastUpdate'] = str(last or int(time()))
        master.append(manifest)
    with open('pluginmaster.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=4)
        f.write('\n')


if __name__ == '__main__':
    main()
