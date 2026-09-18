# TechAbbreviations

A man-page-style lookup tool for tech industry abbreviations, right from your terminal.

## Installation

Add `abbr` to your PATH with the install script:

```sh
./install.sh
```

This symlinks `techabbr.py` to `~/.local/bin/abbr`. Pass a different directory as an argument if you'd rather use somewhere else, e.g. `./install.sh /usr/local/bin`. Make sure that directory is on your `PATH` (the script will tell you if it isn't).

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
```

## Requirements

Python 3, no external dependencies.

## Data

Abbreviations are stored in `abbreviations.json`, currently covering 340 terms across categories like Software, Networking, and Security.
