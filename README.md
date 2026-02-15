# Brian's Spare Time

A static blog built with Python. Generates optimized HTML from Markdown content with image processing, tag pages, search, RSS feed, and sitemap.

## Setup

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```sh
uv venv .venv
uv pip install -r requirements.txt
```

## Development

Start the dev server (auto-rebuilds on changes to content/, templates/, static/):

```sh
./test-serve.sh
```

Serves at http://localhost:8000.

## Build

Generate the static site into `dist/`:

```sh
.venv/bin/python build.py
```

## Project structure

```
content/
  posts/          # Blog posts (each in its own directory with index.md + images)
  interests/      # Interest pages (same structure)
templates/        # Jinja2 HTML templates
static/           # CSS, JS, favicon, logo
dist/             # Build output (git-ignored)
.image-cache/     # Optimized image cache (git-ignored)
build.py          # Static site generator
serve.py          # Dev server with file watching
```

## Adding a post

Create a directory under `content/posts/` with an `index.md` file:

```
content/posts/my-new-post/
  index.md
  photo1.jpg
  photo2.jpg
```

Frontmatter format:

```yaml
---
title: "My New Post"
date: 2026-01-15
description: "A short description for meta tags and search."
image: "photo1.jpg"
tags:
  - photography
  - film
---
```

Images referenced in the markdown are automatically optimized into multiple sizes with srcset.

## Deployment

Configured for Netlify via `netlify.toml`. Push to the repo and Netlify will build and deploy automatically.

The site URL is configured in `build.py` as `SITE_URL` (used for sitemap, RSS feed, and OG tags).
