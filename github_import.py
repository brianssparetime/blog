#!/usr/bin/env python3
"""Import a GitHub repo README as a blog post in content/posts/.

Usage:
    .venv/bin/python github_import.py <github-repo-url> [github-repo-url ...]

Takes a GitHub repo URL (e.g. https://github.com/user/repo), fetches the
README and all referenced images, and creates a blog post directory.
The first H1 heading becomes the post title. Images are downloaded and
paths are rewritten to local references.
"""

import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "content", "posts")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def fetch(url):
    """Fetch a URL and return the response body as bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def fetch_text(url):
    """Fetch a URL and return the response body as text."""
    return fetch(url).decode("utf-8")


def slugify(text, max_len=70):
    """Convert text to a URL-friendly slug."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s


def parse_repo_url(url):
    """Extract owner and repo name from a GitHub URL."""
    url = url.rstrip("/")
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if not match:
        raise ValueError(f"Not a GitHub repo URL: {url}")
    return match.group(1), match.group(2)


def process_repo(repo_url):
    """Fetch a GitHub repo README and create a blog post."""
    owner, repo = parse_repo_url(repo_url)
    print(f"Fetching: {owner}/{repo}")

    # Get repo metadata for the date
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    meta = json.loads(fetch_text(api_url))
    pushed = meta.get("pushed_at", meta.get("created_at", ""))
    date_str = pushed[:10] if pushed else ""
    default_branch = meta.get("default_branch", "main")

    # Fetch raw README
    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/README.md"
    readme = fetch_text(readme_url)

    # Extract title from first heading (H1 preferred, fall back to H2)
    title_match = re.search(r"^#\s+(.+)$", readme, re.MULTILINE)
    if not title_match:
        title_match = re.search(r"^##\s+(.+)$", readme, re.MULTILINE)
    if not title_match:
        raise ValueError("No H1 or H2 heading found in README")
    title = title_match.group(1).strip()

    slug = slugify(title)
    post_dir = os.path.join(POSTS_DIR, slug)
    os.makedirs(post_dir, exist_ok=True)

    # Find all image references and download them
    raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}"
    img_pattern = re.compile(
        r"!\[([^\]]*)\]\(([^)]+\.(?:jpg|jpeg|png|gif)(?:\?[^)]*)?)\)",
        re.IGNORECASE,
    )

    hero_image = ""
    path_to_local = {}

    for match in img_pattern.finditer(readme):
        img_ref = match.group(2)
        if img_ref in path_to_local:
            continue

        # Build download URL: absolute URLs used as-is, relative resolved
        if img_ref.startswith(("http://", "https://")):
            dl_url = img_ref
        else:
            dl_url = f"{raw_base}/{img_ref.lstrip('/')}"

        # Local filename from the last path component
        raw_name = img_ref.split("/")[-1].split("?")[0]
        local_name = re.sub(r"[^a-zA-Z0-9._-]", "_", raw_name)
        path_to_local[img_ref] = local_name

        if not hero_image:
            hero_image = local_name

        dest = os.path.join(post_dir, local_name)
        if os.path.exists(dest):
            print(f"  Already have {local_name}")
            continue
        print(f"  Downloading {local_name}...")
        try:
            data = fetch(dl_url)
            with open(dest, "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"  WARNING: Failed to download {dl_url}: {e}")

    # Rewrite image paths to local filenames
    body = readme
    for img_ref, local_name in path_to_local.items():
        body = body.replace(img_ref, local_name)

    # Convert ![alt](file) to <img> tags for consistency with rest of blog
    body = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1">',
        body,
    )

    # Remove the title heading line (it's in the frontmatter)
    body = re.sub(r"^#{1,2}\s+.+\n+", "", body, count=1, flags=re.MULTILINE)

    # Add link to the GitHub repo at the bottom
    body = body.rstrip() + f"\n\n*Source: [{owner}/{repo}]({repo_url})*\n"

    yaml_title = title.replace("\\", "\\\\").replace('"', '\\"')

    md = (
        f'---\ntitle: "{yaml_title}"\ndate: {date_str}\n'
        f'description: ""\nimage: "{hero_image}"\ntags:\n  - photography\n'
        f"---\n\n{body}"
    )

    index_path = os.path.join(post_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"  -> content/posts/{slug}/")
    return slug


def main():
    if len(sys.argv) < 2:
        print(f"Usage: .venv/bin/python {sys.argv[0]} <github-repo-url> [...]")
        print()
        print("Fetches a GitHub repo README and creates a blog post in content/posts/.")
        sys.exit(1)

    created = []
    for url in sys.argv[1:]:
        try:
            slug = process_repo(url)
            created.append(slug)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone. Created {len(created)} posts:")
    for slug in created:
        print(f"  content/posts/{slug}/")


if __name__ == "__main__":
    main()
