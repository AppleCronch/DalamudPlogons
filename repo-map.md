# Repo map

- `README.md` — Install URL for Dalamud and how the repo works
- `pluginmaster.json` — Generated plugin list Dalamud reads; do not edit by hand
- `update_pluginmaster.py` — Pulls manifests from release zips and regenerates pluginmaster.json
- `plugins/AnoMech/AnoMech.json` — Seed/synced manifest for AnoMech
- `.github/workflows/update.yml` — Runs the update script every 6h, on demand and on push
