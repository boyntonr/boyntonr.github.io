#!/usr/bin/env python3
"""
convert.py — converts a markdown post to HTML and updates index.html.

Usage:
    python convert.py posts/my-post.md [posts/another.md ...]

Each markdown file should start with a YAML front matter block, e.g.:

---
title: The Promise of AI in Materials Science
date: 2026-04-22
slug: intro
---

Your post content here...

If 'slug' is omitted, the filename (without .md) is used.
If 'date' is omitted, today's date is used.
"""

import sys
import re
import os
from datetime import date
from pathlib import Path
import frontmatter
import markdown

# ---------------------------------------------------------------------------
# Config — update YOUR NAME here once, and it propagates everywhere
# ---------------------------------------------------------------------------
AUTHOR      = "Your Name"
GITHUB_USER = "yourusername"
NAV_LINKS = [
    ("home",    "/"),
    ("writing", "/#writings"),
    ("projects","/#projects"),
    ("github",  f"https://github.com/{GITHUB_USER}"),
]
# ---------------------------------------------------------------------------


def build_nav():
    links = ""
    for label, href in NAV_LINKS:
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        links += f'    <a href="{href}"{target}>{label}</a>\n'
    return f"  <nav>\n{links}  </nav>"


def md_to_html(md_path: Path) -> tuple[str, dict]:
    """Parse front matter and convert markdown body to HTML."""
    post = frontmatter.load(md_path)
    body_html = markdown.markdown(
        post.content,
        extensions=["extra", "smarty"],
    )
    # Wrap bare paragraphs so they pick up .post-body styles
    meta = {
        "title": post.get("title", md_path.stem.replace("-", " ").title()),
        "date":  str(post.get("date", date.today())),
        "slug":  post.get("slug", md_path.stem),
    }
    return body_html, meta


def build_post_html(body_html: str, meta: dict) -> str:
    nav = build_nav()
    title   = meta["title"]
    dt      = meta["date"]
    year    = dt[:4]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — {AUTHOR}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --text: #111; --muted: #888; --bg: #faf9f7; --rule: #ddd;
      --font-body: 'EB Garamond', Georgia, serif;
      --font-mono: 'JetBrains Mono', 'Courier New', monospace;
    }}
    html {{ font-size: 18px; scroll-behavior: smooth; }}
    body {{
      background: var(--bg); color: var(--text); font-family: var(--font-body);
      line-height: 1.75; padding: 4rem 1.5rem 6rem;
      max-width: 640px; margin: 0 auto; -webkit-font-smoothing: antialiased;
    }}
    nav {{ display: flex; gap: 1.5rem; margin-bottom: 4rem; font-family: var(--font-mono);
           font-size: 0.72rem; letter-spacing: 0.04em; text-transform: uppercase; }}
    nav a {{ color: var(--muted); text-decoration: none; transition: color 0.15s; }}
    nav a:hover {{ color: var(--text); }}
    .post-header {{ margin-bottom: 2.5rem; }}
    .post-date {{ font-family: var(--font-mono); font-size: 0.72rem; color: var(--muted);
                  letter-spacing: 0.04em; margin-bottom: 0.75rem; display: block; }}
    .post-header h1 {{ font-size: 1.9rem; font-weight: 500; line-height: 1.25; letter-spacing: -0.01em; }}
    hr {{ border: none; border-top: 1px solid var(--rule); margin: 2.5rem 0; }}
    .post-body {{ font-size: 1.05rem; line-height: 1.85; }}
    .post-body p  {{ margin-bottom: 1.4rem; }}
    .post-body h2 {{ font-size: 1.25rem; font-weight: 500; margin: 2.5rem 0 0.75rem; letter-spacing: -0.01em; }}
    .post-body h3 {{ font-size: 1.05rem; font-weight: 500; font-style: italic; margin: 2rem 0 0.5rem; }}
    .post-body a  {{ color: var(--text); text-decoration: underline; text-underline-offset: 3px;
                     text-decoration-color: var(--muted); transition: text-decoration-color 0.15s; }}
    .post-body a:hover {{ text-decoration-color: var(--text); }}
    .post-body ul, .post-body ol {{ padding-left: 1.4rem; margin-bottom: 1.4rem; }}
    .post-body li {{ margin-bottom: 0.4rem; }}
    .post-body blockquote {{ border-left: 2px solid var(--rule); padding-left: 1.25rem;
                             margin: 1.75rem 0; color: #555; font-style: italic; }}
    .post-body strong {{ font-weight: 500; }}
    .post-body code {{ font-family: var(--font-mono); font-size: 0.8rem; background: #eee;
                       padding: 0.15em 0.4em; border-radius: 3px; }}
    .post-body pre  {{ background: #f0efed; border: 1px solid var(--rule); border-radius: 4px;
                       padding: 1.25rem; margin: 1.75rem 0; overflow-x: auto; }}
    .post-body pre code {{ background: none; padding: 0; font-size: 0.78rem; line-height: 1.65; }}
    .post-body img {{ max-width: 100%; height: auto; display: block; margin: 2rem auto; }}
    .post-footer {{ margin-top: 3.5rem; padding-top: 2rem; border-top: 1px solid var(--rule);
                    display: flex; justify-content: space-between; align-items: center; }}
    .post-footer a {{ font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase;
                      letter-spacing: 0.04em; color: var(--muted); text-decoration: none; transition: color 0.15s; }}
    .post-footer a:hover {{ color: var(--text); }}
    footer {{ margin-top: 3rem; font-family: var(--font-mono); font-size: 0.68rem;
              color: var(--muted); letter-spacing: 0.03em; }}
    @keyframes fadein {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
    nav          {{ animation: fadein 0.5s ease both 0s; }}
    .post-header {{ animation: fadein 0.5s ease both 0.06s; }}
    hr           {{ animation: fadein 0.5s ease both 0.10s; }}
    .post-body   {{ animation: fadein 0.5s ease both 0.14s; }}
    .post-footer {{ animation: fadein 0.5s ease both 0.18s; }}
    footer       {{ animation: fadein 0.5s ease both 0.22s; }}
  </style>
</head>
<body>

{nav}

  <article>
    <header class="post-header">
      <span class="post-date">{dt}</span>
      <h1>{title}</h1>
    </header>

    <hr />

    <div class="post-body">
{body_html}
    </div>
  </article>

  <div class="post-footer">
    <a href="/">← back to home</a>
    <a href="/#writings">all writing</a>
  </div>

  <footer>
    <p>© {year} {AUTHOR}</p>
  </footer>

</body>
</html>
"""


def update_index(meta: dict):
    """Insert a new <li> entry into index.html if not already present."""
    index_path = Path("index.html")
    if not index_path.exists():
        print("  ⚠️  index.html not found — skipping index update.")
        return

    html = index_path.read_text(encoding="utf-8")
    slug  = meta["slug"]
    title = meta["title"]
    dt    = meta["date"]

    # Don't add duplicates
    if f'href="/{slug}.html"' in html:
        print(f"  ℹ️  /{slug}.html already in index — skipping.")
        return

    new_li = (
        f'      <li>\n'
        f'        <span class="post-date">{dt}</span>\n'
        f'        <a href="/{slug}.html">{title}</a>\n'
        f'      </li>\n'
    )

    # Insert after the opening <ul class="post-list"> tag
    marker = '<ul class="post-list">'
    if marker not in html:
        print("  ⚠️  Could not find post-list in index.html — skipping index update.")
        return

    updated = html.replace(marker, marker + "\n" + new_li, 1)
    index_path.write_text(updated, encoding="utf-8")
    print(f"  ✅  Added '{title}' to index.html")


def main():
    files = sys.argv[1:]
    if not files:
        print("No markdown files supplied.")
        sys.exit(0)

    for f in files:
        md_path = Path(f.strip())
        if not md_path.exists() or md_path.suffix != ".md":
            print(f"Skipping {f} — not a .md file or doesn't exist.")
            continue

        print(f"Converting {md_path}...")
        body_html, meta = md_to_html(md_path)
        post_html = build_post_html(body_html, meta)

        out_path = Path(f"{meta['slug']}.html")
        out_path.write_text(post_html, encoding="utf-8")
        print(f"  ✅  Written to {out_path}")

        update_index(meta)


if __name__ == "__main__":
    main()
