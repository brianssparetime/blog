#!/usr/bin/env python3
"""Remove unused binary files from git history permanently.

Compares every file that has ever appeared in any commit against the
current HEAD.  Files that no longer exist in HEAD and have a known
binary extension are removed from all historical commits using
git-filter-repo.

Prerequisites:
    pip install git-filter-repo

Usage:
    python cleanup-history.py --dry-run   # list what would be removed
    python cleanup-history.py             # actually rewrite history
"""

import argparse
import os
import subprocess
import sys
import tempfile

BINARY_EXTENSIONS = {
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif", ".ico",
    # Video
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv",
    # Audio
    ".mp3", ".wav", ".flac", ".ogg", ".aac",
    # Documents
    ".pdf",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # Design
    ".psd", ".ai",
}


def run_git(*args):
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error: git {' '.join(args)}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_all_historical_files():
    """Every file path that has ever appeared in any commit."""
    output = run_git("log", "--all", "--pretty=format:", "--name-only")
    return {line.strip() for line in output.splitlines() if line.strip()}


def get_head_files():
    """Every file path currently in HEAD."""
    output = run_git("ls-tree", "-r", "--name-only", "HEAD")
    return {line.strip() for line in output.splitlines() if line.strip()}


def main():
    parser = argparse.ArgumentParser(
        description="Remove unused binary files from git history permanently.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List files that would be removed without making changes.",
    )
    args = parser.parse_args()

    # Must be inside a git repo
    check = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True, text=True,
    )
    if check.returncode != 0:
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)

    # Check for git-filter-repo unless this is just a dry run
    if not args.dry_run:
        check = subprocess.run(
            ["git", "filter-repo", "--version"],
            capture_output=True, text=True,
        )
        if check.returncode != 0:
            print(
                "Error: git-filter-repo is not installed.\n"
                "Install with:  pip install git-filter-repo",
                file=sys.stderr,
            )
            sys.exit(1)

    print("Scanning history...")
    historical = get_all_historical_files()
    current = get_head_files()
    deleted = historical - current

    to_remove = sorted(
        f for f in deleted
        if os.path.splitext(f)[1].lower() in BINARY_EXTENSIONS
    )

    if not to_remove:
        print("No unused binary files found in history.")
        return

    print(f"Found {len(to_remove)} unused binary file(s) in history:\n")
    for path in to_remove:
        print(f"  {path}")

    if args.dry_run:
        print(
            f"\nDry run complete. {len(to_remove)} file(s) would be removed "
            f"from all commits.\n"
            f"Run without --dry-run to rewrite history."
        )
        return

    # Write paths to a temp file for --paths-from-file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False,
    ) as tmp:
        for path in to_remove:
            tmp.write(path + "\n")
        paths_file = tmp.name

    # Save remote URL before filter-repo strips it
    try:
        remote_url = run_git("remote", "get-url", "origin").strip()
    except SystemExit:
        remote_url = None

    print(f"\nRemoving {len(to_remove)} file(s) from history...")
    subprocess.run(
        [
            "git", "filter-repo",
            "--invert-paths",
            "--paths-from-file", paths_file,
            "--force",
        ],
        check=True,
    )
    os.unlink(paths_file)

    # Re-add remote (filter-repo removes it by default)
    if remote_url:
        subprocess.run(
            ["git", "remote", "add", "origin", remote_url],
            capture_output=True,
        )

    print("\nDone. History has been rewritten.")
    print("\nTo push the cleaned history to GitHub, run:")
    print(f"  git push origin --force --all")
    print(f"  git push origin --force --tags")
    print("\nAll other clones of this repo will need to be re-cloned.")


if __name__ == "__main__":
    main()
