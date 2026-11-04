# TrackerProject (transitional)

This tree is the legacy header-bidding crawl and ML orchestration layer.
Do not add new research features here. New measurement code belongs in
`openwpm/` and `hb/`. `CODEOWNERS` still assigns the directory to
`@code4johnm` so changes stay reviewed.

## Paths

Set `HB_TRACKER_ROOT` to the directory that should hold profiles, results,
and archives. When it is unset, the default is `TrackerProject/var/` inside
the repository checkout. That directory is created on first use and is
gitignored.

Optional overrides for the old archive layout:

- `HB_ARCHIVE_DIR` — parent of `ml_training/` and `ml_testing/`. When unset, that parent is the tracker root. It is not prefixed with an extra `archive/` directory.
- `HB_TRAINING_MANIFEST` — JSON manifest of training profiles. When unset, the file is `ml_testing/training_manifest.json` under the tracker root.

There is no default under a researcher home directory and no default under
`/mnt/hgfs`.

## Coordination

Bid JSON is updated through `TrackerProject/src/coord.py`. Each update holds
an exclusive `fcntl` lock for the read, mutation, and replace. The old
`writing.json` file is not a lock.

The Python 2-era `os.system` calls that remain in the ML scripts are residual
risk. They are not a supported interface for new work.
