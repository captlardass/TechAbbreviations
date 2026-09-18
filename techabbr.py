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


def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")


def prompt(label, required=False):
    while True:
        value = input(f"{label}: ").strip()
        if value or not required:
            return value
        print(f"{label} is required.")


def add_entry_interactive(entries):
    print("Add a new abbreviation (Ctrl+C to cancel).\n")
    abbr = prompt("Abbreviation (e.g. API)", required=True)

    if find_exact(entries, abbr):
        print(f"'{abbr}' already exists. Run 'abbr {abbr}' to see it.")
        return

    full = prompt("Full name (e.g. Application Programming Interface)", required=True)
    category = prompt("Category (e.g. Software)", required=True)
    short = prompt("Short description (one line)", required=True)
    description = prompt("Full description")
    example = prompt("Example (optional)")
    see_also_raw = prompt("See also (comma-separated abbreviations, optional)")
    see_also = [s.strip() for s in see_also_raw.split(",") if s.strip()]

    entry = {
        "abbr": abbr,
        "full": full,
        "category": category,
        "short": short,
        "description": description or short,
        "example": example,
        "see_also": see_also,
    }
    entries.append(entry)
    save_entries(entries)
    print(f"\nAdded '{abbr}'. Run 'abbr {abbr}' to see it.")


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


def manpage_lines(entry, width):
    indent = " " * 7
    lines = []

    def wrapped(text):
        out = []
        for line in text.split("\n"):
            if line.strip():
                out.extend(
                    textwrap.wrap(
                        line, max(width - 7, 20), initial_indent=indent, subsequent_indent=indent
                    )
                )
            else:
                out.append("")
        return out

    lines.append(f"{entry['abbr'].upper()}(1)".ljust(30) + "Tech Abbreviations Manual")
    lines.append("")
    lines.append("NAME")
    lines.append(f"{indent}{entry['abbr']} - {entry['full']}")
    lines.append("")
    lines.append("CATEGORY")
    lines.append(f"{indent}{entry['category']}")
    lines.append("")
    lines.append("DESCRIPTION")
    lines.extend(wrapped(entry["description"]))
    lines.append("")
    if entry.get("example"):
        lines.append("EXAMPLE")
        lines.extend(wrapped(entry["example"]))
        lines.append("")
    if entry.get("see_also"):
        lines.append("SEE ALSO")
        lines.append(f"{indent}{', '.join(entry['see_also'])}")
        lines.append("")
    return lines


def print_manpage(entry):
    width = min(term_width(), 90)
    for line in manpage_lines(entry, width):
        print(line)


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


def tui_filter(entries, query):
    if not query:
        return entries
    q = query.lower()
    return [
        e
        for e in entries
        if q in e["abbr"].lower()
        or q in e["full"].lower()
        or q in e["short"].lower()
        or q in e["description"].lower()
    ]


def tui_draw_list(stdscr, entries, selected, query, offset):
    import curses

    stdscr.erase()
    height, width = stdscr.getmaxyx()

    header = f"TechAbbreviations — search: {query}"
    stdscr.addstr(0, 0, header[: width - 1], curses.A_BOLD)
    stdscr.addstr(1, 0, "-" * min(width - 1, 60))

    list_top = 2
    list_height = max(height - list_top - 2, 1)

    if selected < offset:
        offset = selected
    elif selected >= offset + list_height:
        offset = selected - list_height + 1

    visible = entries[offset : offset + list_height]
    for i, e in enumerate(visible):
        row = list_top + i
        line = f"{e['abbr']:<12} {e['category']:<14} {e['short']}"
        attr = curses.A_REVERSE if offset + i == selected else curses.A_NORMAL
        stdscr.addstr(row, 0, line[: width - 1], attr)

    if not entries:
        stdscr.addstr(list_top, 0, "No matches.")

    footer = f"{len(entries)} match(es)  |  ↑/↓ move  Enter view  Backspace edit  Esc clear/quit"
    stdscr.addstr(height - 1, 0, footer[: width - 1], curses.A_DIM)
    stdscr.refresh()
    return offset


def tui_show_detail(stdscr, entry):
    import curses

    top = 0
    while True:
        height, width = stdscr.getmaxyx()
        lines = manpage_lines(entry, width - 1)
        visible_height = max(height - 1, 1)
        top = max(0, min(top, max(len(lines) - visible_height, 0)))

        stdscr.erase()
        for i, line in enumerate(lines[top : top + visible_height]):
            stdscr.addstr(i, 0, line[: width - 1])
        footer = "↑/↓ scroll  any other key: back"
        stdscr.addstr(height - 1, 0, footer[: width - 1], curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_DOWN:
            top += 1
        elif key == curses.KEY_UP:
            top -= 1
        else:
            return


def tui_main(stdscr, entries):
    import curses

    curses.curs_set(0)
    stdscr.keypad(True)

    all_entries = sorted(entries, key=lambda e: e["abbr"].upper())
    query = ""
    selected = 0
    offset = 0

    while True:
        filtered = tui_filter(all_entries, query)
        selected = max(0, min(selected, len(filtered) - 1)) if filtered else 0
        offset = tui_draw_list(stdscr, filtered, selected, query, offset)

        key = stdscr.getch()

        if key == 27:  # Esc
            if query:
                query = ""
                selected = 0
            else:
                return
        elif key in (curses.KEY_ENTER, 10, 13) and filtered:
            tui_show_detail(stdscr, filtered[selected])
        elif key == curses.KEY_UP:
            selected -= 1
        elif key == curses.KEY_DOWN:
            selected += 1
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            query = query[:-1]
            selected = 0
        elif 32 <= key <= 126:
            query += chr(key)
            selected = 0


def run_tui(entries):
    try:
        import curses
    except ImportError:
        print("The TUI needs Python's 'curses' module, which isn't available here.")
        print("On Windows, install it with: pip install windows-curses")
        sys.exit(1)

    try:
        curses.wrapper(tui_main, entries)
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(
        prog="abbr",
        description="Look up tech industry abbreviations, man-page style.",
        epilog=(
            "Adding your own abbreviations:\n"
            "  abbr --add\n"
            "      Starts an interactive prompt asking for the abbreviation,\n"
            "      full name, category, short description, full description,\n"
            "      an optional example, and optional 'see also' terms.\n"
            "      The entry is saved straight into abbreviations.json.\n"
            "\n"
            "Browsing interactively:\n"
            "  abbr --tui\n"
            "      Opens a full-screen browser. Type to search, ↑/↓ to move,\n"
            "      Enter to view an entry, Backspace to edit the search, and\n"
            "      Esc to clear the search or quit. Requires Python's 'curses'\n"
            "      module; on Windows, install it with: pip install windows-curses"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    parser.add_argument(
        "-a", "--add", action="store_true", help="add a new abbreviation (interactive)"
    )
    parser.add_argument(
        "-t", "--tui", action="store_true", help="launch interactive full-screen browser"
    )
    args = parser.parse_args()

    entries = load_entries()

    if args.add:
        add_entry_interactive(entries)
        return

    if args.tui:
        run_tui(entries)
        return

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
