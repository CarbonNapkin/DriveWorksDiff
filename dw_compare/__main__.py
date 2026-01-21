#!/usr/bin/env python3
"""
DriveWorks Project Comparison Tool - CLI Entry Point
"""

import sys
import argparse
import webbrowser
from pathlib import Path

from .parsers import load_project
from .report import generate_html_report


def find_project_folders() -> tuple[Path, Path] | None:
    """Auto-detect two project folders in current directory"""
    cwd = Path.cwd()
    
    # Get all subdirectories (excluding hidden)
    subdirs = sorted([d for d in cwd.iterdir() if d.is_dir() and not d.name.startswith('.')])
    
    # Look for common naming patterns
    patterns = [
        ('old', 'new'),
        ('prod', 'dev'),
        ('production', 'development'),
        ('master', 'branch'),
        ('v1', 'v2'),
        ('before', 'after'),
    ]
    
    for old_name, new_name in patterns:
        old_matches = [d for d in subdirs if old_name in d.name.lower()]
        new_matches = [d for d in subdirs if new_name in d.name.lower()]
        if old_matches and new_matches:
            return old_matches[0], new_matches[0]
    
    # If exactly two folders, use them (sorted alphabetically = old, new)
    if len(subdirs) == 2:
        return subdirs[0], subdirs[1]
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Compare two DriveWorks project folders and generate HTML report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python -m dw_compare old_project/ new_project/ -o comparison.html
    
    # Or just run in a folder containing two project folders:
    python -m dw_compare
        ''')
    
    parser.add_argument('old_folder', type=Path, nargs='?', help='Path to old project folder')
    parser.add_argument('new_folder', type=Path, nargs='?', help='Path to new project folder')
    parser.add_argument('-o', '--output', type=Path, default=Path('dw_comparison.html'),
                       help='Output HTML file (default: dw_comparison.html)')
    parser.add_argument('--no-open', action='store_true',
                       help='Do not auto-open report in browser')
    
    args = parser.parse_args()
    
    # Auto-detect folders if not provided
    if args.old_folder is None or args.new_folder is None:
        print("No folders specified, looking for project folders...")
        found = find_project_folders()
        if found:
            args.old_folder, args.new_folder = found
            print(f"  Found: {args.old_folder.name} → {args.new_folder.name}")
        else:
            print("Error: Could not auto-detect project folders.")
            print("Either provide two folder arguments, or place exactly two project folders")
            print("in the same directory as this script.")
            sys.exit(1)
    
    if not args.old_folder.is_dir():
        print(f"Error: {args.old_folder} is not a directory")
        sys.exit(1)
    if not args.new_folder.is_dir():
        print(f"Error: {args.new_folder} is not a directory")
        sys.exit(1)
    
    print(f"Loading old project: {args.old_folder}")
    old_proj = load_project(args.old_folder)
    
    print(f"Loading new project: {args.new_folder}")
    new_proj = load_project(args.new_folder)
    
    print("Generating comparison report...")
    html = generate_html_report(old_proj, new_proj, args.old_folder.name, args.new_folder.name)
    
    args.output.write_text(html, encoding='utf-8')
    print(f"✅ Report saved to: {args.output}")
    
    # Auto-open in browser
    if not args.no_open:
        webbrowser.open(f'file://{args.output.resolve()}')


if __name__ == '__main__':
    main()
