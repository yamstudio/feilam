# feilam

Personal CLI that reads a hand-maintained photography log (Excel spreadsheet: one row per frame, with camera, lens, exposure and GPS data) and produces EXIF metadata for the scanned/exported JPEGs. It exists so the owner doesn't have to pay for a commercial tool. Single-user hobby project; the GitHub repo is public.

## Layout

- `src/feilam/cli.py`: the whole app. A `click` group `main` with one command, `sync`. It reads the spreadsheet with polars (`read_excel`, fastexcel backend), derives columns (combined date/time, GPS ref letters, GPS in degrees/minutes/seconds, `BBBBSSSS.JPG` file name from Batch + Seq), and currently **prints one `exiftool` shell command per row to stdout**. It does not touch any photo.
- `pyproject.toml` / `pdm.lock`: PDM project, `requires-python >=3.14`, `distribution = false`. Script alias `cli` is defined under `[tool.pdm.scripts]`.
- No tests, no CI, no README.

## Environment

- Runs on the owner's WSL2 machine only. Shell scripts should be zsh.
- Python 3.14 in a local `.venv` (gitignored); deps managed by PDM.
- `exiftool` is installed on the machine, but the direction is to stop depending on it (see below).

## Commands

Verified:
- `.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from src.feilam.cli import main; main(['sync','--help'])"` works and prints help.
- `pdm --version` works (2.29.7).

Unverified (not run):
- `pdm run cli sync -s <file.xlsx>`: the documented script alias; the `src.feilam.cli:main` path in pyproject looks odd, check it before relying on it.
- Tests and lint: none exist.

## Spreadsheet format (inferred from the code, no sample in the repo)

Columns: Date, Time, F Number, Exposure Time, Focal Length, GPS Latitude, GPS Longitude, GPS Altitude, Lens Make, Lens Model, Lens Info, ISO, Time Zone, Batch, Seq, Notes. `--model` and `--make` default to a film camera; they apply to every row. Never commit real photo logs or location data; use small synthetic fixtures for tests.

## Long-term vision (far off)

An iOS app for use while shooting on a film camera (the owner's Nikon F2). At the moment of each frame the owner taps to snap the parameters on the spot (the phone supplies time, time zone and GPS; the owner enters aperture, shutter speed, ISO, lens) and saves them. At home they export the log, then apply it to the developed, scanned photos. This CLI is the "apply" half and today stands in for the whole pipeline, with a hand-maintained spreadsheet as the interchange format. We are a long way from the app; don't start building it unprompted. Do keep the spreadsheet schema and the pure derivation logic in the CLI stable and well-defined, since an app export would likely have to feed it.

## Direction (near term)

- The `TODO` in `sync` says to write EXIF directly from Python instead of generating `exiftool` commands. The owner confirmed this is the intended direction. Pick and justify a library with the owner before adding a dependency.
- The uncommitted `.filter(col("Batch") == 1081)` and the zero-pad change (8 to 4) in `cli.py` are a temporary hack for one roll. The filter should become a CLI option (e.g. `--batch`) rather than a hardcoded value.

## Conventions

- Existing style: 2-space indent, single-file module, polars expression pipelines, `click` decorators. This is early code, not a strict style guide; keep it consistent within a file but improve where sensible (type hints, splitting pure functions out of the click command so they can be tested).
- Keep column-derivation logic as pure functions/expressions so it can be unit tested without photos.

## Known deficiencies

- No tests, README, or CI. `pyproject.toml` references `README.md`, which doesn't exist.
- `numpy` is declared as a dependency but isn't used by the code and isn't installed in `.venv` or in `pdm.lock`; lock and manifest are out of sync.
- Generated shell commands interpolate values inside single quotes with no escaping, so an apostrophe in any cell (for example a lens name) breaks or injects into the command. Moot once EXIF is written in Python.
- `sync`'s docstring mentions a "target file" that doesn't exist; `Notes` is read but unused.
- `--model` and `--make` are marked `required=True` but also have defaults.
- Hardcoded `.JPG` extension and file-name scheme; no check that the target files exist.
- Dependencies are current (locked Sept 2026) but Python 3.14 is required, so older interpreters won't work.

## Git workflow

Single `master` branch, merged via PRs (history shows "Add sync script (#1)"). Work on a feature branch and open a PR; don't merge without the owner saying so. Don't commit `.venv`, `.pdm-python`, or `__pycache__` (already gitignored).
