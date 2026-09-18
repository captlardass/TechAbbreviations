# TechAbbreviations

A man-page-style lookup tool for tech industry abbreviations, right from your terminal.

## Installation

```sh
git clone https://github.com/captlardass/TechAbbreviations.git
cd TechAbbreviations
```

### macOS / Linux

```sh
./install.sh
```

This symlinks `techabbr.py` to `~/.local/bin/abbr`. Pass a different directory as an argument if you'd rather install somewhere else, e.g. `./install.sh /usr/local/bin`. Make sure that directory is on your `PATH` (the script will tell you if it isn't).

If `./install.sh` fails with a "permission denied" error, the scripts lost their executable bit — this usually happens if you downloaded the repo as a ZIP instead of cloning it. Fix it with:

```sh
chmod +x install.sh techabbr.py
./install.sh
```

### Windows

Requires Python 3 installed and available as `python` or `py`. In PowerShell:

```powershell
.\install.ps1
```

This creates an `abbr.cmd` wrapper in `%USERPROFILE%\bin` that calls `techabbr.py` for you. Pass a different directory as an argument to install elsewhere, e.g. `.\install.ps1 -TargetDir C:\tools`. If that directory isn't already on your `PATH`, the script prints the exact command to add it.

If PowerShell blocks the script with an execution-policy error, run it once with:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

## Usage

```sh
abbr API
```

Or, without installing:

```sh
./techabbr.py API
```

Look up an abbreviation and see it rendered like a man page: name, category, description, example, and related terms.

### Other commands

```sh
abbr                     # list all abbreviations in a table
abbr -s cache            # search abbreviations, names, and descriptions
abbr -c Networking       # show only abbreviations in a category
abbr -l                  # list all categories
abbr --add               # add your own abbreviation (interactive)
abbr --tui               # launch the interactive full-screen browser
```

## TUI mode

```sh
abbr --tui
```

Opens a full-screen browser instead of printing to the terminal:

- Type to filter the list as you go.
- `↑` / `↓` to move the selection.
- `Enter` to open the man-page-style view for the selected entry (`↑` / `↓` scroll it, any other key goes back).
- `Backspace` to edit the search.
- `Esc` clears the search, or quits if the search is already empty.

TUI mode needs Python's `curses` module. It's built into Python on macOS and Linux. On Windows, install the missing piece with:

```powershell
pip install windows-curses
```

## Requirements

Python 3, no external dependencies (Windows TUI mode needs `windows-curses`, see above).

## Data

Abbreviations are stored in `abbreviations.json`, currently covering 340 terms across categories like Software, Networking, and Security.
