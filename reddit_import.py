#!/usr/bin/env python3
"""Import Reddit posts as blog entries in content/posts/.

Usage:
    .venv/bin/python reddit_import.py <html-file-or-dir> [html-file-or-dir ...]

Save Reddit posts via browser "Save As" (complete page) using old.reddit.com,
then point this script at the saved .html files (or a directory containing them).
It parses the HTML for title, date, body text, and image URLs, downloads
full-resolution images from i.redd.it, and creates blog post directories.
"""

import html as html_mod
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "content", "posts")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def download(url, dest):
    """Download a URL to a local file."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


def slugify(text, max_len=70):
    """Convert text to a URL-friendly slug."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s


def html_to_markdown(html_str):
    """Convert simple HTML (from Reddit post body) to markdown."""
    text = html_str

    # Paragraphs
    text = re.sub(r"<p>", "", text)
    text = re.sub(r"</p>", "\n\n", text)

    # Line breaks
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Bold
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text)

    # Italic
    text = re.sub(r"<em>(.*?)</em>", r"*\1*", text)
    text = re.sub(r"<i>(.*?)</i>", r"*\1*", text)

    # Links
    text = re.sub(r'<a\s+href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", text)

    # Blockquotes
    text = re.sub(r"<blockquote>\s*", "\n> ", text)
    text = re.sub(r"\s*</blockquote>", "\n", text)

    # Headers
    for i in range(1, 7):
        prefix = "#" * i
        text = re.sub(rf"<h{i}[^>]*>(.*?)</h{i}>", rf"{prefix} \1\n", text)

    # Lists
    text = re.sub(r"<ul>\s*", "\n", text)
    text = re.sub(r"</ul>\s*", "\n", text)
    text = re.sub(r"<ol>\s*", "\n", text)
    text = re.sub(r"</ol>\s*", "\n", text)
    text = re.sub(r"<li>\s*", "- ", text)
    text = re.sub(r"\s*</li>", "\n", text)

    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = html_mod.unescape(text)

    # Clean up excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_op_top_comments(content, op_author):
    """Extract top-level comments by the OP from old.reddit.com HTML.

    Splits at each comment thing div. For each chunk by the OP, checks
    the section before the child div for a "parent" link -- if absent,
    it's a top-level comment. Returns a list of markdown strings.
    """
    # Split at each comment thing boundary
    parts = re.split(r'(?=<div class=" thing id-t1_)', content)
    comments = []

    for part in parts:
        # Check if this chunk is a comment by the OP
        author_match = re.search(r'data-type="comment"[^>]*data-author="([^"]*)"', part)
        if not author_match or author_match.group(1) != op_author:
            continue

        # Look at the flat section before any child div
        child_pos = part.find('class="child"')
        if child_pos == -1:
            child_pos = len(part)
        flat_section = part[:child_pos]

        # Top-level comments have no parent link
        if 'data-event-action="parent"' in flat_section:
            continue

        # Extract the comment body
        body_match = re.search(
            r'class="usertext-body may-blank-within md-container\s*">'
            r'\s*<div class="md">(.*?)</div>\s*</div>',
            flat_section,
            re.DOTALL,
        )
        if body_match:
            text = html_to_markdown(body_match.group(1))
            if text:
                comments.append(text)

    return comments


def parse_html(html_path):
    """Parse a saved Reddit HTML file, return post data dict."""
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Title: from <title> tag, strip " : SubredditName" suffix
    title_match = re.search(r"<title>([^<]+)</title>", content)
    if not title_match:
        raise ValueError("Could not find title")
    raw_title = html_mod.unescape(title_match.group(1))
    # Strip subreddit suffix
    title = re.sub(r"\s*:\s*\w+\s*$", "", raw_title).strip()

    # Date: first datetime attribute
    date_match = re.search(r'datetime="(\d{4}-\d{2}-\d{2})T', content)
    if not date_match:
        raise ValueError("Could not find date")
    date_str = date_match.group(1)

    # Post author: from the link thing's data-author
    author_match = re.search(r'data-type="link"[^>]*data-author="([^"]*)"', content)
    op_author = author_match.group(1) if author_match else ""

    # Post body: try the gallery-style "usertext usertext-body" div first
    # (unique to the OP post), then fall back to "may-blank-within" matches
    selftext = ""
    gallery_body = re.search(
        r'class="usertext usertext-body">\s*<div class="md">(.*?)</div>\s*</div>',
        content,
        re.DOTALL,
    )
    if gallery_body:
        selftext = html_to_markdown(gallery_body.group(1))
    else:
        body_matches = re.findall(
            r'class="usertext-body may-blank-within md-container\s*">\s*<div class="md">(.*?)</div>\s*</div>',
            content,
            re.DOTALL,
        )
        # The post body is typically the second match (first is sidebar)
        # but for image-only posts there may be no body
        if len(body_matches) >= 2:
            selftext = html_to_markdown(body_matches[1])
        elif len(body_matches) == 1:
            # Could be the post body or sidebar; check if it looks like sidebar
            candidate = body_matches[0]
            if "Welcome" not in candidate[:50]:
                selftext = html_to_markdown(candidate)

    # Top-level comments by OP (excluding any that duplicate the selftext)
    op_comments = []
    if op_author:
        for comment in extract_op_top_comments(content, op_author):
            if selftext and comment == selftext:
                continue
            op_comments.append(comment)

    # Image URLs: extract media IDs from preview.redd.it URLs
    preview_urls = re.findall(
        r"https://preview\.redd\.it/([a-zA-Z0-9_]+)\.(jpg|png|gif)",
        content,
    )
    # Deduplicate while preserving order
    seen = set()
    images = []
    for media_id, ext in preview_urls:
        if media_id not in seen:
            seen.add(media_id)
            images.append({
                "url": f"https://i.redd.it/{media_id}.{ext}",
                "filename": f"{media_id}.{ext}",
            })

    # Find the original Reddit URL
    reddit_url = ""
    url_match = re.search(
        r'https://old\.reddit\.com/r/\w+/comments/[a-z0-9]+/[^"&\s]*',
        content,
    )
    if url_match:
        reddit_url = url_match.group(0).rstrip("/")

    return {
        "title": title,
        "date": date_str,
        "selftext": selftext,
        "op_comments": op_comments,
        "images": images,
        "reddit_url": reddit_url,
    }


def process_html(html_path):
    """Parse saved HTML and create a blog post directory."""
    print(f"Parsing: {os.path.basename(html_path)}")
    post = parse_html(html_path)

    slug = slugify(post["title"])
    post_dir = os.path.join(POSTS_DIR, slug)
    os.makedirs(post_dir, exist_ok=True)

    # Download full-res images from i.redd.it
    for img in post["images"]:
        dest = os.path.join(post_dir, img["filename"])
        if os.path.exists(dest):
            print(f"  Already have {img['filename']}")
            continue
        print(f"  Downloading {img['filename']}...")
        try:
            download(img["url"], dest)
        except Exception as e:
            print(f"  WARNING: Failed to download {img['url']}: {e}")

    # Build markdown body
    body_parts = []
    if post["selftext"]:
        body_parts.append(post["selftext"])
        body_parts.append("")

    if post["op_comments"]:
        for comment in post["op_comments"]:
            body_parts.append(comment)
            body_parts.append("")

    for img in post["images"]:
        safe_alt = post["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        body_parts.append(f'<img src="{img["filename"]}" alt="{safe_alt}">')


    body = "\n".join(body_parts)

    yaml_title = post["title"].replace("\\", "\\\\").replace('"', '\\"')
    hero = post["images"][0]["filename"] if post["images"] else ""

    md = (
        f'---\ntitle: "{yaml_title}"\ndate: {post["date"]}\n'
        f'description: ""\nimage: "{hero}"\ntags:\n  - photography\n'
        f"---\n\n{body}\n"
    )

    index_path = os.path.join(post_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"  -> content/posts/{slug}/")
    return slug


def collect_html_files(paths):
    """Expand arguments: files are used directly, directories are scanned."""
    html_files = []
    for path in paths:
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                if name.endswith(".html"):
                    html_files.append(os.path.join(path, name))
        elif path.endswith(".html"):
            html_files.append(path)
        else:
            print(f"Skipping non-HTML: {path}")
    return html_files


def main():
    if len(sys.argv) < 2:
        print(f"Usage: .venv/bin/python {sys.argv[0]} <html-file-or-dir> [...]")
        print()
        print("Save Reddit posts via old.reddit.com 'Save As' (complete page),")
        print("then point this script at the .html files or containing directory.")
        print("Full-res images will be downloaded from i.redd.it.")
        sys.exit(1)

    html_files = collect_html_files(sys.argv[1:])
    if not html_files:
        print("No .html files found.")
        sys.exit(1)

    created = []
    for html_path in html_files:
        try:
            slug = process_html(html_path)
            created.append(slug)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone. Created {len(created)} posts:")
    for slug in created:
        print(f"  content/posts/{slug}/")


if __name__ == "__main__":
    main()
