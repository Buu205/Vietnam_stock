#!/usr/bin/env python3
"""
Plans cleanup utility - Rename and/or delete old report files.

Usage:
    cd plans/
    python3 cleanup.py --rename          # Rename files to add date prefix
    python3 cleanup.py --delete          # Delete old files per retention policy
    python3 cleanup.py --all             # Rename + delete
    python3 cleanup.py --rename --force  # Force re-date even if already has date

Retention policy:
- scout/scout-external: 30 days
- brainstorm: 90 days
- docs-manager: 7 days
- audit: keep forever
- Others: 30 days
"""

import os
import re
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
REPORTS_DIR = Path("reports")
ARCHIVE_DIR = Path("archive")
DATE_FORMAT = "%y%m%d"  # YYMMDD

# Retention policies (in days)
RETENTION = {
    "scout": 30,
    "scout-external": 30,
    "brainstorm": 90,
    "docs-manager": 7,
    "audit": 99999,  # Keep forever
    "default": 30,
}

# Known patterns that should have date
PREFIX_PATTERNS = [
    r"scout-external-",
    r"scout-",
    r"brainstorm-",
    r"docs-manager-",
    r"audit-",
    r"fullstack-dev-",
    r"plan-",
]

# ============================================================================
# RENAME FUNCTIONS
# ============================================================================

def has_date_prefix(filename: str) -> bool:
    """Check if filename already has date prefix (YYMMDD or YYYY-MM-DD)"""
    # Check for YYYY-MM-DD format (e.g., 2025-12-21-...)
    if re.match(r'^(?:\w+-)?\d{4}-\d{2}-\d{2}', filename):
        return True
    # Check for YYMMDD format at start (e.g., 251228-...)
    if re.match(r'^\d{6}-', filename):
        return True
    # Check for prefix-YYMMDD format (e.g., scout-251225-...)
    for pattern in PREFIX_PATTERNS:
        match = re.match(pattern + r'(\d{6})', filename)
        if match:
            return True
    return False

def extract_prefix(filename: str) -> str:
    """Extract prefix from filename (before any date)"""
    for pattern in PREFIX_PATTERNS:
        match = re.match(pattern, filename)
        if match:
            return pattern.rstrip("-")
    return ""

def generate_new_name(old_path: Path, force: bool = False) -> tuple[bool, str, str]:
    """Generate new filename with date prefix. Returns: (should_rename, old_name, new_name)"""
    filename = old_path.name

    if has_date_prefix(filename) and not force:
        return False, filename, filename

    mtime = os.path.getmtime(old_path)
    file_date = datetime.fromtimestamp(mtime)
    date_str = file_date.strftime(DATE_FORMAT)

    prefix = extract_prefix(filename)
    stem = old_path.stem
    suffix = old_path.suffix

    if prefix:
        rest = stem.replace(prefix + "-", "").replace(prefix, "")
        rest = re.sub(r'^\d{6}-', '', rest)
        rest = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', rest)
        new_name = f"{prefix}-{date_str}-{rest}{suffix}"
    else:
        new_name = f"{date_str}-{filename}"

    return True, filename, new_name

def rename_files(dry_run: bool = False, force: bool = False) -> int:
    """Rename files to add date prefix. Returns count of renamed files."""
    if not REPORTS_DIR.exists():
        print(f"Error: Reports directory not found: {REPORTS_DIR}")
        return 0

    files = sorted(REPORTS_DIR.glob("*.md"))
    print(f"Found {len(files)} report files\n")

    to_rename = []
    already_ok = []

    for filepath in files:
        should_rename, old_name, new_name = generate_new_name(filepath, force)
        if should_rename:
            to_rename.append((filepath, old_name, new_name))
        else:
            already_ok.append((old_name, new_name))

    if to_rename:
        print("=== FILES TO RENAME ===")
        for filepath, old_name, new_name in to_rename:
            print(f"  {old_name:50s} → {new_name}")
        print(f"\nTotal to rename: {len(to_rename)} files\n")

    if already_ok:
        print("=== FILES ALREADY OK ===")
        for old_name, _ in already_ok[:10]:
            print(f"  ✓ {old_name}")
        if len(already_ok) > 10:
            print(f"  ... and {len(already_ok) - 10} more")
        print(f"\nTotal already OK: {len(already_ok)} files\n")

    if to_rename and not dry_run:
        response = input(f"Rename {len(to_rename)} files? (y/N): ")
        if response.lower() == 'y':
            for filepath, old_name, new_name in to_rename:
                new_path = filepath.parent / new_name
                filepath.rename(new_path)
                print(f"  Renamed: {old_name} → {new_name}")
            print("\nRename complete!")
            return len(to_rename)
    elif dry_run:
        print("[DRY RUN] No files renamed.")

    return 0

# ============================================================================
# DELETE FUNCTIONS
# ============================================================================

def parse_date_from_filename(filename: str) -> datetime | None:
    """Extract date from filename like scout-251225-*.md or scout-2025-12-21-*.md"""
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return datetime(year, month, day)

    match = re.search(r'(\d{6})', filename)
    if match:
        date_str = match.group(1)
        if int(date_str[:2]) < 32:
            year = 2000 + int(date_str[:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(year, month, day)

    return None

def get_report_type(filename: str) -> str:
    """Determine report type from filename"""
    if filename.startswith("scout-external-"):
        return "scout-external"
    for prefix in ["scout-", "brainstorm-", "docs-manager-", "audit-"]:
        if filename.startswith(prefix):
            return prefix.replace("-", "")
    return "default"

def should_delete(filename: str, filepath: Path) -> tuple[bool, str]:
    """Determine if file should be deleted"""
    report_type = get_report_type(filename)
    retention_days = RETENTION.get(report_type, RETENTION["default"])

    if report_type == "audit":
        return False, f"audit file (keep forever)"

    file_date = parse_date_from_filename(filename)
    if not file_date:
        return False, f"no date found"

    age = datetime.now() - file_date
    if age.days > retention_days:
        return True, f"{report_type} file, {age.days} days old (retention: {retention_days})"

    return False, f"{report_type} file, {age.days} days old (retention: {retention_days})"

def delete_old_files(dry_run: bool = False) -> int:
    """Delete old files per retention policy. Returns count of deleted files."""
    if not REPORTS_DIR.exists():
        print(f"Error: Reports directory not found: {REPORTS_DIR}")
        return 0

    files = list(REPORTS_DIR.glob("*.md"))
    print(f"Found {len(files)} report files")

    to_delete = []
    to_keep = []

    for filepath in files:
        filename = filepath.name
        should_del, reason = should_delete(filename, filepath)
        if should_del:
            to_delete.append((filepath, reason))
        else:
            to_keep.append((filepath, reason))

    to_delete.sort(key=lambda x: x[1])
    to_keep.sort(key=lambda x: x[1])

    print("\n=== FILES TO DELETE ===")
    for filepath, reason in to_delete:
        print(f"  [DELETE] {filepath.name:50s} | {reason}")
    print(f"\nTotal to delete: {len(to_delete)} files")

    print("\n=== FILES TO KEEP ===")
    for filepath, reason in to_keep[:10]:
        print(f"  [KEEP]   {filepath.name:50s} | {reason}")
    if len(to_keep) > 10:
        print(f"  ... and {len(to_keep) - 10} more")
    print(f"\nTotal to keep: {len(to_keep)} files")

    if not dry_run and to_delete:
        response = input(f"\nDelete {len(to_delete)} files? (y/N): ")
        if response.lower() == 'y':
            for filepath, _ in to_delete:
                filepath.unlink()
                print(f"  Deleted: {filepath.name}")
            print("\nCleanup complete!")
            return len(to_delete)
    elif dry_run:
        print("\n[DRY RUN] No files deleted.")

    return 0

# ============================================================================
# ORGANIZE BY MODULE FUNCTIONS
# ============================================================================

# Module folders mapping
MODULE_FOLDERS = {
    "scout": "scout",
    "scout-external": "scout",
    "brainstorm": "brainstorm",
    "docs-manager": "docs-manager",
    "audit": "audit",
    "fullstack-dev": "fullstack-dev",
    "plan": "plans",
    "mcp-manager": "mcp",
    "debugger": "debugger",
    "tester": "tester",
    "researcher": "researcher",
    "planner": "planner",
}

def get_module_folder(filename: str) -> str:
    """Determine which module folder a file belongs to."""
    # Check known prefixes
    for prefix, folder in MODULE_FOLDERS.items():
        if filename.startswith(prefix + "-"):
            return folder
        # Also check if prefix appears after date (e.g., 251228-scout-...)
        if re.search(rf'^\d{{6}}-{prefix}-', filename):
            return folder
        if re.search(rf'^\d{{4}}-\d{{2}}-\d{{2}}-{prefix}', filename):
            return folder

    # Check content-based patterns
    lower_name = filename.lower()
    if "scout" in lower_name:
        return "scout"
    if "brainstorm" in lower_name:
        return "brainstorm"
    if "audit" in lower_name:
        return "audit"
    if "docs" in lower_name or "documentation" in lower_name:
        return "docs-manager"

    return "misc"


def organize_by_module(dry_run: bool = False) -> int:
    """Organize report files into module-based subfolders."""
    if not REPORTS_DIR.exists():
        print(f"Error: Reports directory not found: {REPORTS_DIR}")
        return 0

    files = list(REPORTS_DIR.glob("*.md"))
    print(f"Found {len(files)} report files\n")

    # Group files by target folder
    moves: dict[str, list[tuple[Path, str]]] = {}

    for filepath in files:
        folder = get_module_folder(filepath.name)
        if folder not in moves:
            moves[folder] = []
        moves[folder].append((filepath, filepath.name))

    # Display plan
    total_moves = 0
    print("=== ORGANIZATION PLAN ===\n")
    for folder in sorted(moves.keys()):
        file_list = moves[folder]
        print(f"📁 {folder}/ ({len(file_list)} files)")
        for filepath, filename in file_list[:5]:
            print(f"    └── {filename}")
        if len(file_list) > 5:
            print(f"    └── ... and {len(file_list) - 5} more")
        total_moves += len(file_list)
        print()

    print(f"Total: {total_moves} files across {len(moves)} folders\n")

    if dry_run:
        print("[DRY RUN] No files moved.")
        return 0

    # Confirm and execute
    response = input(f"Organize {total_moves} files into folders? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    moved = 0
    for folder, file_list in moves.items():
        target_dir = REPORTS_DIR / folder
        target_dir.mkdir(exist_ok=True)

        for filepath, filename in file_list:
            target_path = target_dir / filename
            if target_path.exists():
                print(f"  Skip (exists): {filename}")
                continue
            filepath.rename(target_path)
            print(f"  Moved: {filename} → {folder}/")
            moved += 1

    print(f"\n✓ Organized {moved} files into {len(moves)} folders")
    return moved


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Plans cleanup utility - Rename, organize and/or delete old report files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--rename", action="store_true", help="Rename files to add date prefix")
    parser.add_argument("--delete", action="store_true", help="Delete old files per retention policy")
    parser.add_argument("--organize", action="store_true", help="Organize files into module-based folders")
    parser.add_argument("--all", action="store_true", help="Run rename + organize + delete")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--force", action="store_true", help="Force re-date even if file already has date")

    args = parser.parse_args()

    # If no action specified, show help
    if not any([args.rename, args.delete, args.organize, args.all]):
        parser.print_help()
        return

    renamed = 0
    organized = 0
    deleted = 0

    if args.rename or args.all:
        print("=" * 60)
        print("RENAME FILES")
        print("=" * 60)
        renamed = rename_files(dry_run=args.dry_run, force=args.force)
        print()

    if args.organize or args.all:
        print("=" * 60)
        print("ORGANIZE BY MODULE")
        print("=" * 60)
        organized = organize_by_module(dry_run=args.dry_run)
        print()

    if args.delete or args.all:
        print("=" * 60)
        print("DELETE OLD FILES")
        print("=" * 60)
        deleted = delete_old_files(dry_run=args.dry_run)
        print()

    if args.all and not args.dry_run:
        print("=" * 60)
        print(f"SUMMARY: {renamed} renamed, {organized} organized, {deleted} deleted")
        print("=" * 60)

if __name__ == "__main__":
    main()
