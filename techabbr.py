#!/usr/bin/env python3
"""abbr - a man-page-style lookup tool for tech industry abbreviations."""

import argparse
import json
import shutil
import sys
import textwrap
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "abbreviations.json"


def load_entries():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def term_width():
    return shutil.get_terminal_size(fallback=(100, 24)).columns


def print_table(entries, title=None):
    if not entries:
        print("No matching abbreviations found.")
        return

    entries = sorted(entries, key=lambda e: e["abbr"].upper())
    width = term_width()

    abbr_w = max(len(e["abbr"]) for e in entries) + 2
    abbr_w = max(abbr_w, len("ABBR") + 2)
    cat_w = max(len(e["category"]) for e in entries) + 2
    cat_w = max(cat_w, len("CATEGORY") + 2)
    desc_w = max(width - abbr_w - cat_w - 4, 20)

    if title:
        print(title)
        print()

    header = f"{'ABBR':<{abbr_w}}{'CATEGORY':<{cat_w}}{'DESCRIPTION'}"
    print(header)
    print("-" * min(len(header) + desc_w - len('DESCRIPTION'), width))

    for e in entries:
        desc_lines = textwrap.wrap(e["short"], desc_w) or [""]
        print(f"{e['abbr']:<{abbr_w}}{e['category']:<{cat_w}}{desc_lines[0]}")
        for line in desc_lines[1:]:
            print(f"{'':<{abbr_w}}{'':<{cat_w}}{line}")

    print()
    print(f"{len(entries)} abbreviation(s). Run 'abbr <TERM>' for full details.")


def print_manpage(entry):
    width = min(term_width(), 90)
    indent = " " * 7

    def wrapped(text):
        out = []
        for line in text.split("\n"):
            if line.strip():
                out.extend(
                    textwrap.wrap(
                        line, width - 7, initial_indent=indent, subsequent_indent=indent
                    )
                )
            else:
                out.append("")
        return "\n".join(out)

    print(f"{entry['abbr'].upper()}(1)".ljust(30) + "Tech Abbreviations Manual")
    print()
    print("NAME")
    print(f"{indent}{entry['abbr']} - {entry['full']}")
    print()
    print("CATEGORY")
    print(f"{indent}{entry['category']}")
    print()
    print("DESCRIPTION")
    print(wrapped(entry["description"]))
    print()
    if entry.get("example"):
        print("EXAMPLE")
        print(wrapped(entry["example"]))
        print()
    if entry.get("see_also"):
        print("SEE ALSO")
        print(f"{indent}{', '.join(entry['see_also'])}")
        print()


def find_exact(entries, term):
    for e in entries:
        if e["abbr"].lower() == term.lower():
            return e
    return None


def find_close(entries, term):
    term = term.lower()
    return [e for e in entries if term in e["abbr"].lower()]


def list_categories(entries):
    cats = sorted({e["category"] for e in entries})
    print("Categories:")
    for c in cats:
        count = sum(1 for e in entries if e["category"] == c)
        print(f"  {c} ({count})")


def main():
    parser = argparse.ArgumentParser(
        prog="abbr",
        description="Look up tech industry abbreviations, man-page style.",
    )
    parser.add_argument(
        "term", nargs="?", help="abbreviation to look up, e.g. 'API'"
    )
    parser.add_argument(
        "-c", "--category", help="show only abbreviations in this category"
    )
    parser.add_argument(
        "-s", "--search", help="search abbreviations, names and descriptions"
    )
    parser.add_argument(
        "-l", "--list-categories", action="store_true", help="list all categories"
    )
    args = parser.parse_args()

    entries = load_entries()

    if args.list_categories:
        list_categories(entries)
        return

    if args.category:
        matches = [
            e for e in entries if args.category.lower() in e["category"].lower()
        ]
        print_table(matches, title=f"Category: {args.category}")
        return

    if args.search:
        q = args.search.lower()
        matches = [
            e
            for e in entries
            if q in e["abbr"].lower()
            or q in e["full"].lower()
            or q in e["short"].lower()
            or q in e["description"].lower()
        ]
        print_table(matches, title=f"Search: {args.search}")
        return

    if args.term:
        exact = find_exact(entries, args.term)
        if exact:
            print_manpage(exact)
            return

        close = find_close(entries, args.term)
        if len(close) == 1:
            print_manpage(close[0])
        elif close:
            print(f"No exact match for '{args.term}'. Did you mean:")
            print_table(close)
        else:
            print(f"No abbreviation found matching '{args.term}'.")
            print("Try 'abbr -s <keyword>' to search descriptions instead.")
            sys.exit(1)
        return

    print_table(entries)


if __name__ == "__main__":
    main()
