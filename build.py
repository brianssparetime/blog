#!/usr/bin/env python3
"""Static site generator for BST blog."""

import html as html_mod
import json
import os
import re
import shutil
from urllib.parse import quote, unquote

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")
DIST_DIR = os.path.join(ROOT, "dist")
STATIC_DIR = os.path.join(ROOT, "static")
TEMPLATES_DIR = os.path.join(ROOT, "templates")
IMAGE_CACHE_DIR = os.path.join(ROOT, ".image-cache")

SITE_URL = "https://brianssparetime.com"
SITE_TITLE = "Brian's Spare Time"
SITE_DESCRIPTION = "I'm Brian and this is some stuff I've done in my spare time..."

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".svg"}
# Copied through untouched; everything else gets resized JPEG versions.
PASSTHROUGH_EXTS = {".gif", ".svg"}
MEDIA_EXTS = {".mp4", ".webm", ".mov"}
OPTIMIZED_WIDTHS = [400, 1000, 2000]
JPEG_QUALITY = 80


def clean_dist():
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)


def parse_frontmatter(text):
    """Split text on --- delimiters, return (metadata dict, body string)."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1])
    body = parts[2]
    return meta or {}, body


def convert_v_img_tags(text):
    """Replace <v-img src="X" alt="Y" :dirp="dir"></v-img> with <img src="X" alt="Y">."""
    pattern = r'<v-img\s+src="([^"]*?)"\s+alt="([^"]*?)"[^>]*></v-img>'
    return re.sub(pattern, r'<img src="\1" alt="\2">', text)

GALLERY_BLOCK_RE = re.compile(r"^```gallery(?:[ \t]+(.*?))?[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
GALLERY_IMAGE_RE = re.compile(r"!\[(.*?)\]\((.+?)\)")

CHEVRON_LEFT = (
    '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">'
    '<path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
CHEVRON_RIGHT = (
    '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">'
    '<path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def expand_galleries(text):
    """Turn fenced ```gallery blocks into gallery HTML.

    A gallery block holds one ![caption](file.jpg) per line. It becomes a
    main image with prev/next buttons and a strip of thumbnails beneath.
    Text after "gallery" on the opening fence is an optional title shown
    above the main image. Without JavaScript the figures simply stack, so
    nothing is lost.

    Returns (text, found) where found says whether any gallery was expanded.
    """
    found = False

    def build(match):
        nonlocal found
        title = (match.group(1) or "").strip()
        images = GALLERY_IMAGE_RE.findall(match.group(2))
        if not images:
            return match.group(0)
        found = True

        slides = []
        thumbs = []
        for i, (caption, src) in enumerate(images):
            alt = html_mod.escape(caption, quote=True)
            src = html_mod.escape(src, quote=True)
            cap = f"<figcaption>{html_mod.escape(caption)}</figcaption>" if caption else ""
            slides.append(
                f'<figure class="gallery-slide"><img src="{src}" alt="{alt}">{cap}</figure>'
            )
            thumbs.append(
                f'<button type="button" class="gallery-thumb-btn" '
                f'aria-label="Show image {i + 1} of {len(images)}">'
                f'<img class="gallery-thumb" src="{src}" alt=""></button>'
            )

        out = ['<div class="gallery">']
        if title:
            out.append(f'<div class="gallery-title">{html_mod.escape(title)}</div>')
        out += [
            '<div class="gallery-main">',
            f'<button type="button" class="gallery-prev" aria-label="Previous image" disabled>{CHEVRON_LEFT}</button>',
            '<div class="gallery-slides">',
            *slides,
            "</div>",
            f'<button type="button" class="gallery-next" aria-label="Next image">{CHEVRON_RIGHT}</button>',
            "</div>",
            '<div class="gallery-thumbs">',
            *thumbs,
            "</div>",
            "</div>",
        ]
        # Blank lines around the block keep Markdown from wrapping it in <p>.
        return "\n\n" + "\n".join(out) + "\n\n"

    return GALLERY_BLOCK_RE.sub(build, text), found


CAPTION_IMG_RE = re.compile(r"<p>\s*(<img\b[^>]*\balt=\"([^\"]+)\"[^>]*>)\s*</p>")


def add_captions(html):
    """Show each standalone image's alt text as a caption beneath it.

    Applies to posts with `captions: true` in their frontmatter. A paragraph
    holding nothing but an image with alt text becomes a figure with a
    figcaption, so the same ![caption](file.jpg) line serves both purposes,
    as it does inside a gallery block.
    """
    return CAPTION_IMG_RE.sub(
        lambda m: f'<figure class="captioned">{m.group(1)}<figcaption>{m.group(2)}</figcaption></figure>',
        html,
    )


def render_markdown(text):
    md = markdown.Markdown(extensions=["extra", "mdx_linkify"])
    return md.convert(text)


def collect_pages(subdir, page_type):
    """Walk content/{subdir}/, find dirs with index.md, parse and render each."""
    pages = []
    base = os.path.join(CONTENT_DIR, subdir)
    if not os.path.isdir(base):
        return pages

    for name in sorted(os.listdir(base)):
        page_dir = os.path.join(base, name)
        index_file = os.path.join(page_dir, "index.md")
        if not os.path.isfile(index_file):
            continue

        with open(index_file, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)

        if meta.get("draft"):
            print(f"  skipping draft: {name}")
            continue

        if not meta.get("date"):
            raise ValueError(
                f"{subdir}/{name}/index.md has no date. "
                "Published pages are sorted by date, so it is required. "
                "Set one, or mark the page draft: true."
            )

        body = convert_v_img_tags(body)
        body, has_gallery = expand_galleries(body)
        html = render_markdown(body)
        if meta.get("captions"):
            html = add_captions(html)

        files = list_page_files(page_dir)
        images = [fn for fn in files if os.path.splitext(fn)[1].lower() in IMAGE_EXTS]
        media = [fn for fn in files if os.path.splitext(fn)[1].lower() in MEDIA_EXTS]

        output_dir = os.path.join(subdir, name)

        pages.append({
            "title": meta.get("title", name),
            "date": meta.get("date", ""),
            "description": meta.get("description", ""),
            "image": meta.get("image", ""),
            "tags": meta.get("tags", []),
            "html": html,
            "has_gallery": has_gallery,
            "images": images,
            "media": media,
            "source_dir": page_dir,
            "output_dir": output_dir,
            "page_type": page_type,
        })

    return pages


def list_page_files(page_dir):
    """Return every file under page_dir as a path relative to it, using '/'.

    Images may live in subfolders (one folder per gallery, say). Hidden files
    and folders are skipped.
    """
    found = []
    for dirpath, dirnames, filenames in os.walk(page_dir):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), page_dir)
            found.append(rel.replace(os.sep, "/"))
    return found


def copy_page_media(page):
    """Copy video/audio files referenced by a page straight through to dist."""
    if not page["media"]:
        return
    dest_dir = os.path.join(DIST_DIR, page["output_dir"])
    os.makedirs(dest_dir, exist_ok=True)
    for fn in page["media"]:
        dest = os.path.join(dest_dir, fn)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(page["source_dir"], fn), dest)


def process_images(page):
    """Generate optimized JPEG versions of all images for a page.

    Uses .image-cache/ to avoid re-encoding unchanged images.
    Returns a dict mapping original filename to version info.
    """
    dest_dir = os.path.join(DIST_DIR, page["output_dir"])
    cache_dir = os.path.join(IMAGE_CACHE_DIR, page["output_dir"])
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    image_info = {}

    for img_name in page["images"]:
        src_path = os.path.join(page["source_dir"], img_name)
        stem = os.path.splitext(img_name)[0]
        ext = os.path.splitext(img_name)[1].lower()

        # img_name may include a subfolder; mirror it in dist and the cache.
        os.makedirs(os.path.dirname(os.path.join(dest_dir, img_name)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.join(cache_dir, img_name)), exist_ok=True)

        if ext in PASSTHROUGH_EXTS:
            shutil.copy2(src_path, os.path.join(dest_dir, img_name))
            continue

        src_mtime = os.path.getmtime(src_path)
        meta_path = os.path.join(cache_dir, img_name + ".json")

        # Try cache: metadata file must exist and be newer than source
        if os.path.exists(meta_path) and os.path.getmtime(meta_path) >= src_mtime:
            try:
                with open(meta_path) as f:
                    versions = {int(k): v for k, v in json.load(f).items()}
                all_exist = all(
                    os.path.exists(os.path.join(cache_dir, v["filename"]))
                    for v in versions.values()
                )
                if all_exist:
                    for v in versions.values():
                        shutil.copy2(
                            os.path.join(cache_dir, v["filename"]),
                            os.path.join(dest_dir, v["filename"]),
                        )
                    image_info[img_name] = versions
                    continue
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # Cache miss -- generate optimized versions
        try:
            im = Image.open(src_path)
            im = ImageOps.exif_transpose(im)

            if im.mode in ("RGBA", "LA", "PA"):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")

            orig_w, orig_h = im.size
            versions = {}

            for target_w in OPTIMIZED_WIDTHS:
                native = orig_w <= target_w
                if native:
                    out_w, out_h = orig_w, orig_h
                    resized = im
                else:
                    ratio = target_w / orig_w
                    out_w = target_w
                    out_h = round(orig_h * ratio)
                    resized = im.resize((out_w, out_h), Image.LANCZOS)

                out_name = f"{stem}-{target_w}w.jpg"
                resized.save(
                    os.path.join(cache_dir, out_name), "JPEG", quality=JPEG_QUALITY,
                )
                shutil.copy2(
                    os.path.join(cache_dir, out_name),
                    os.path.join(dest_dir, out_name),
                )
                versions[target_w] = {
                    "filename": out_name,
                    "width": out_w,
                    "height": out_h,
                }

                # Wider targets would be byte-identical copies carrying the same
                # srcset width descriptor, so stop at the first native-size one.
                if native:
                    break

            with open(meta_path, "w") as f:
                json.dump(versions, f)

            image_info[img_name] = versions
            im.close()
        except Exception:
            shutil.copy2(src_path, os.path.join(dest_dir, img_name))

    return image_info


def rewrite_post_images(html, image_info):
    """Rewrite <img> tags in rendered HTML to use optimized versions with srcset."""

    def replace_img(match):
        tag = match.group(0)
        src = unquote(match.group(1))

        if src not in image_info:
            return tag

        versions = image_info[src]

        class_match = re.search(r'class="([^"]*)"', tag)
        cls = class_match.group(1) if class_match else ""
        is_thumb = "gallery-thumb" in cls.split()

        if is_thumb:
            # Thumbnails are small, so the 400w version alone is enough.
            default = versions.get(400) or versions[min(versions)]
            srcset_parts = []
        else:
            default = versions.get(1000) or versions[max(versions)]
            srcset_parts = []
            for w in [1000, 2000]:
                if w in versions:
                    v = versions[w]
                    srcset_parts.append(f"{quote(v['filename'])} {v['width']}w")

        alt_match = re.search(r'alt="([^"]*)"', tag)
        alt = alt_match.group(1) if alt_match else ""

        new_tag = f'<img src="{quote(default["filename"])}" alt="{alt}"'
        if cls:
            new_tag += f' class="{cls}"'
        if srcset_parts:
            new_tag += f' srcset="{", ".join(srcset_parts)}"'
            new_tag += ' sizes="(max-width: 1000px) 100vw, 1000px"'
        new_tag += f' width="{default["width"]}" height="{default["height"]}"'
        new_tag += ' loading="lazy">'
        return new_tag

    return re.sub(r'<img\s[^>]*?src="([^"]*?)"[^>]*/?>', replace_img, html)


def attach_thumbnail(page, image_info):
    """Point the page's card at the 400w copy of its hero image, if it has one."""
    hero = page.get("image", "")
    if hero and hero in image_info:
        tn = image_info[hero][400]
        page["thumbnail"] = quote(tn["filename"])
        page["thumb_width"] = tn["width"]
        page["thumb_height"] = tn["height"]
    else:
        page["thumbnail"] = quote(hero)
        page["thumb_width"] = ""
        page["thumb_height"] = ""


def copy_static_assets():
    dest = os.path.join(DIST_DIR, "static")
    shutil.copytree(STATIC_DIR, dest)


def site_context():
    return {"url": SITE_URL, "title": SITE_TITLE, "description": SITE_DESCRIPTION}


def render_page(page, env):
    template_name = page["page_type"] + ".html"
    template = env.get_template(template_name)
    html = template.render(page=page, site=site_context())

    out_dir = os.path.join(DIST_DIR, page["output_dir"])
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "index.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)


def render_index(posts, interests, env):
    template = env.get_template("index.html")
    visible_posts = [
        p for p in posts
        if not ({"work-in-progress", "hidden"} & set(p.get("tags", [])))
    ]
    sorted_posts = sorted(visible_posts, key=lambda p: p["date"], reverse=True)
    html = template.render(posts=sorted_posts, interests=interests, site=site_context())

    out_file = os.path.join(DIST_DIR, "index.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)


def render_tags(posts, env):
    # Hidden posts are excluded from all tag views.
    # work-in-progress posts are excluded from the home page (in render_index)
    # but still appear on tag pages, matching the old blog's behavior.
    non_hidden = [p for p in posts if "hidden" not in p.get("tags", [])]

    tag_map = {}
    for post in non_hidden:
        for tag in post.get("tags", []):
            if tag != "hidden":
                tag_map.setdefault(tag, []).append(post)

    for tag_posts in tag_map.values():
        tag_posts.sort(key=lambda p: p["date"], reverse=True)

    # Render per-tag pages
    tag_template = env.get_template("tag.html")
    for tag, tag_posts in tag_map.items():
        out_dir = os.path.join(DIST_DIR, "tags", tag)
        os.makedirs(out_dir, exist_ok=True)
        html = tag_template.render(tag=tag, posts=tag_posts, site=site_context())
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # Render tag index page
    tags_template = env.get_template("tags.html")
    out_dir = os.path.join(DIST_DIR, "tags")
    os.makedirs(out_dir, exist_ok=True)
    html = tags_template.render(tags=sorted(tag_map.keys()), site=site_context())
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    return tag_map


def render_search(posts, env):
    non_hidden = [p for p in posts if "hidden" not in p.get("tags", [])]
    sorted_posts = sorted(non_hidden, key=lambda p: p["date"], reverse=True)

    index = []
    for p in sorted_posts:
        date = p["date"]
        if hasattr(date, "strftime"):
            date_str = date.strftime("%B %-d, %Y")
        else:
            date_str = str(date)
        index.append({
            "title": p["title"],
            "description": p.get("description") or "",
            "tags": p.get("tags", []),
            "date": date_str,
            "url": "/" + p["output_dir"] + "/",
            "image": ("/" + p["output_dir"] + "/" + p.get("thumbnail", p.get("image", ""))) if p.get("thumbnail") or p.get("image") else "",
        })

    with open(os.path.join(DIST_DIR, "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f)

    template = env.get_template("search.html")
    out_dir = os.path.join(DIST_DIR, "search")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(template.render(site=site_context()))


def render_sitemap(posts, interests, tag_map):
    """Generate sitemap.xml listing all pages."""
    urls = [SITE_URL + "/"]
    urls.append(SITE_URL + "/search/")
    urls.append(SITE_URL + "/tags/")
    for tag in sorted(tag_map.keys()):
        urls.append(SITE_URL + "/tags/" + tag + "/")
    for p in posts:
        urls.append(SITE_URL + "/" + p["output_dir"] + "/")
    for p in interests:
        urls.append(SITE_URL + "/" + p["output_dir"] + "/")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        lines.append(f"  <url><loc>{url}</loc></url>")
    lines.append("</urlset>")

    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_rss(posts):
    """Generate an RSS 2.0 feed of recent posts."""
    from xml.sax.saxutils import escape

    non_hidden = [
        p for p in posts
        if not ({"hidden"} & set(p.get("tags", [])))
    ]
    sorted_posts = sorted(non_hidden, key=lambda p: p["date"], reverse=True)[:20]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    lines.append("  <channel>")
    lines.append(f"    <title>{escape(SITE_TITLE)}</title>")
    lines.append(f"    <link>{SITE_URL}</link>")
    lines.append(f"    <description>{escape(SITE_DESCRIPTION)}</description>")
    lines.append(f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>')

    for p in sorted_posts:
        url = SITE_URL + "/" + p["output_dir"] + "/"
        date = p["date"]
        if hasattr(date, "strftime"):
            pub_date = date.strftime("%a, %d %b %Y 00:00:00 GMT")
        else:
            pub_date = str(date)

        lines.append("    <item>")
        lines.append(f"      <title>{escape(p['title'])}</title>")
        lines.append(f"      <link>{url}</link>")
        lines.append(f"      <guid>{url}</guid>")
        if p.get("description"):
            lines.append(f"      <description>{escape(p['description'])}</description>")
        lines.append(f"      <pubDate>{pub_date}</pubDate>")
        if p.get("thumbnail"):
            img_url = SITE_URL + "/" + p["output_dir"] + "/" + p["thumbnail"]
            lines.append(f'      <enclosure url="{img_url}" type="image/jpeg"/>')
        lines.append("    </item>")

    lines.append("  </channel>")
    lines.append("</rss>")

    with open(os.path.join(DIST_DIR, "feed.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_robots_txt():
    content = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(content)


def build():
    print("Cleaning dist/...")
    clean_dist()

    print("Copying static assets...")
    copy_static_assets()

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    env.filters["format_date"] = lambda d: d.strftime("%B %-d, %Y") if hasattr(d, "strftime") else str(d)

    print("Collecting posts...")
    posts = collect_pages("posts", "post")
    for p in posts:
        print(f"  {p['title']} ({len(p['images'])} images)")
        image_info = process_images(p)
        copy_page_media(p)
        p["html"] = rewrite_post_images(p["html"], image_info)
        attach_thumbnail(p, image_info)
        render_page(p, env)

    print("Collecting interests...")
    interests = collect_pages("interests", "interest")
    for p in interests:
        print(f"  {p['title']} ({len(p['images'])} images)")
        image_info = process_images(p)
        copy_page_media(p)
        p["html"] = rewrite_post_images(p["html"], image_info)
        attach_thumbnail(p, image_info)
        render_page(p, env)

    print("Rendering index...")
    render_index(posts, interests, env)

    print("Rendering tag pages...")
    tag_map = render_tags(posts, env)

    print("Rendering search page...")
    render_search(posts, env)

    print("Generating sitemap.xml...")
    render_sitemap(posts, interests, tag_map)

    print("Generating feed.xml...")
    render_rss(posts)

    print("Generating robots.txt...")
    render_robots_txt()

    # Copy standalone pages (no template processing)
    bfr_src = os.path.join(CONTENT_DIR, "bfr", "index.html")
    if os.path.isfile(bfr_src):
        bfr_dest = os.path.join(DIST_DIR, "bfr")
        os.makedirs(bfr_dest, exist_ok=True)
        shutil.copy2(bfr_src, os.path.join(bfr_dest, "index.html"))

    total = len(posts) + len(interests)
    print(f"Built {total} pages + index -> dist/")


if __name__ == "__main__":
    build()
