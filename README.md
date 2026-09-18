# TechAbbreviations

A man-page-style lookup tool for tech industry abbreviations, right from your terminal.

## Usage

```sh
./techabbr.py API
```

Look up an abbreviation and see it rendered like a man page: name, category, description, example, and related terms.

### Other commands

```sh
./techabbr.py                     # list all abbreviations in a table
./techabbr.py -s cache            # search abbreviations, names, and descriptions
./techabbr.py -c Networking       # show only abbreviations in a category
./techabbr.py -l                  # list all categories
```

## Requirements

Python 3, no external dependencies.

## Data

Abbreviations are stored in `abbreviations.json`, currently covering 340 terms across categories like Software, Networking, and Security.
