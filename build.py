#!/usr/bin/env python3
"""Static site generator for BST blog."""

import json
import os
import re
import shutil

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

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}
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
        body = convert_v_img_tags(body)
        html = render_markdown(body)

        images = [
            fn for fn in os.listdir(page_dir)
            if os.path.splitext(fn)[1].lower() in IMAGE_EXTS
        ]

        output_dir = os.path.join(subdir, name)

        pages.append({
            "title": meta.get("title", name),
            "date": meta.get("date", ""),
            "description": meta.get("description", ""),
            "image": meta.get("image", ""),
            "tags": meta.get("tags", []),
            "html": html,
            "images": images,
            "source_dir": page_dir,
            "output_dir": output_dir,
            "page_type": page_type,
        })

    return pages


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

        if ext == ".gif":
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
                if orig_w <= target_w:
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
        src = match.group(1)

        if src not in image_info:
            return tag

        versions = image_info[src]
        default = versions.get(1000) or versions[max(versions)]

        srcset_parts = []
        for w in [1000, 2000]:
            if w in versions:
                v = versions[w]
                srcset_parts.append(f"{v['filename']} {v['width']}w")

        alt_match = re.search(r'alt="([^"]*)"', tag)
        alt = alt_match.group(1) if alt_match else ""

        new_tag = f'<img src="{default["filename"]}" alt="{alt}"'
        if srcset_parts:
            new_tag += f' srcset="{", ".join(srcset_parts)}"'
            new_tag += ' sizes="(max-width: 1000px) 100vw, 1000px"'
        new_tag += f' width="{default["width"]}" height="{default["height"]}"'
        new_tag += ' loading="lazy">'
        return new_tag

    return re.sub(r'<img\s[^>]*?src="([^"]*?)"[^>]*/?>', replace_img, html)


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
        print(f"  {p['title']}")
        image_info = process_images(p)
        p["html"] = rewrite_post_images(p["html"], image_info)
        hero = p.get("image", "")
        if hero and hero in image_info:
            tn = image_info[hero][400]
            p["thumbnail"] = tn["filename"]
            p["thumb_width"] = tn["width"]
            p["thumb_height"] = tn["height"]
        else:
            p["thumbnail"] = hero
            p["thumb_width"] = ""
            p["thumb_height"] = ""
        render_page(p, env)

    print("Collecting interests...")
    interests = collect_pages("interests", "interest")
    for p in interests:
        print(f"  {p['title']}")
        image_info = process_images(p)
        p["html"] = rewrite_post_images(p["html"], image_info)
        hero = p.get("image", "")
        if hero and hero in image_info:
            tn = image_info[hero][400]
            p["thumbnail"] = tn["filename"]
            p["thumb_width"] = tn["width"]
            p["thumb_height"] = tn["height"]
        else:
            p["thumbnail"] = hero
            p["thumb_width"] = ""
            p["thumb_height"] = ""
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

    total = len(posts) + len(interests)
    print(f"Built {total} pages + index -> dist/")


if __name__ == "__main__":
    build()
