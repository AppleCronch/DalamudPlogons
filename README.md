# DalamudPlogons

Custom Dalamud plugin repository.

## Install

1. In game, open `/xlsettings` → **Experimental** → **Custom Plugin Repositories**.
2. Add this URL, tick **Enabled**, and save:

   ```
   https://raw.githubusercontent.com/AppleCronch/DalamudPlogons/main/pluginmaster.json
   ```

3. Open `/xlplugins` → **All Plugins** and install from the list.

## Plugins

| Plugin | Source |
| --- | --- |
| AnoMech (Elemental strats fork) | [AppleCronch/AnoMechElementalStrats](https://github.com/AppleCronch/AnoMechElementalStrats) |

## How it works

`update_pluginmaster.py` reads each plugin's `<InternalName>.json` out of the latest GitHub release's
`latest.zip`, rewrites `RepoUrl`/`IconUrl` to the release's repo, and regenerates `pluginmaster.json`.
The `Update pluginmaster` workflow runs it every 6 hours and on demand. To add a plugin, add it to
`SOURCES` in the script and commit a seed manifest at `plugins/<Name>/<Name>.json`.
