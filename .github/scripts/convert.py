#!/usr/bin/env python3
"""
convert.py — converts a markdown post to HTML and updates index.html.

Each markdown file should start with YAML front matter:

---
title: My Post Title
date: 2026-04-22
slug: my-post-slug
---

Post content here...
"""

import sys
import re
from datetime import date
from pathlib import Path
import frontmatter
import markdown

# ---------------------------------------------------------------------------
# Config — update these once
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

STYLES = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --text: #fff;
      --muted: #888;
      --bg: #000;
      --rule: #333;
      --font: ui-monospace, 'SF Mono', 'Cascadia Mono', 'Roboto Mono', Menlo, Consolas, monospace;
    }

    html { font-size: 15px; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.6;
      padding: 2.5rem 1.5rem 5rem;
      max-width: 680px;
      margin: 0 auto;
    }

    a { color: var(--text); text-decoration: underline; text-underline-offset: 3px; }
    a:hover { color: var(--muted); }

    nav { margin-bottom: 2.5rem; }
    nav a { font-size: 0.9rem; text-decoration: none; }
    nav a:hover { text-decoration: underline; }

    .post-header { margin-bottom: 2rem; }

    .post-date {
      font-size: 0.85rem;
      color: var(--muted);
      display: block;
      margin-bottom: 0.75rem;
    }

    .post-header h1 {
      font-size: 1.6rem;
      font-weight: 700;
      line-height: 1.25;
      letter-spacing: -0.02em;
    }

    hr {
      border: none;
      border-top: 1px solid var(--rule);
      margin: 2rem 0;
      width: 5rem;
    }

    .post-body { font-size: 0.95rem; line-height: 1.75; }
    .post-body p  { margin-bottom: 1.25rem; }
    .post-body h2 { font-size: 1.3rem; font-weight: 700; margin: 2rem 0 0.75rem; }
    .post-body h3 { font-size: 1rem; font-weight: 700; margin: 1.5rem 0 0.5rem; }
    .post-body ul, .post-body ol { padding-left: 1.5rem; margin-bottom: 1.25rem; }
    .post-body li { margin-bottom: 0.35rem; }
    .post-body blockquote {
      border-left: 2px solid var(--rule);
      padding-left: 1rem;
      margin: 1.5rem 0;
      color: var(--muted);
    }
    .post-body strong { font-weight: 700; }
    .post-body em { font-style: italic; }
    .post-body code {
      background: #111;
      padding: 0.15em 0.4em;
      border-radius: 3px;
      font-size: 0.85em;
    }
    .post-body pre {
      background: #111;
      border: 1px solid var(--rule);
      border-radius: 4px;
      padding: 1rem;
      margin: 1.5rem 0;
      overflow-x: auto;
    }
    .post-body pre code { background: none; padding: 0; font-size: 0.85em; }
    .post-body img { max-width: 100%; display: block; margin: 2rem auto; }

    .post-footer {
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--rule);
      display: flex;
      justify-content: space-between;
    }

    .post-footer a { font-size: 0.85rem; color: var(--muted); text-decoration: none; }
    .post-footer a:hover { color: var(--text); text-decoration: underline; }

    footer { margin-top: 2rem; font-size: 0.8rem; color: var(--muted); }
    footer nav { display: flex; gap: 1.25rem; flex-wrap: wrap; margin-top: 0.5rem; }
    footer nav a { color: var(--text); font-size: 0.8rem; text-decoration: none; }
    footer nav a:hover { text-decoration: underline; }
"""


def build_nav():
    links = ""
    for label, href in NAV_LINKS:
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        links += f'    <a href="{href}"{target}>{label}</a>\n'
    return f"  <nav>\n{links}  </nav>"


def md_to_html(md_path):
    post = frontmatter.load(md_path)
    body_html = markdown.markdown(post.content, extensions=["extra", "smarty"])
    meta = {
        "title": post.get("title", md_path.stem.replace("-", " ").title()),
        "date":  str(post.get("date", date.today())),
        "slug":  post.get("slug", md_path.stem),
    }
    return body_html, meta


def build_post_html(body_html, meta):
    nav   = build_nav()
    title = meta["title"]
    dt    = meta["date"]
    year  = dt[:4]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — {AUTHOR}</title>
  <style>{STYLES}  </style>
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
    <a href="/">← home</a>
    <a href="/#writings">all writing</a>
  </div>

  <footer>
    <p>Copyright © {year} {AUTHOR}</p>
    <nav>
      <a href="/">Home</a>
      <a href="/#writings">Writing</a>
      <a href="https://github.com/{GITHUB_USER}" target="_blank" rel="noopener">Code</a>
    </nav>
  </footer>

</body>
</html>
"""


def update_index(meta):
    index_path = Path("index.html")
    if not index_path.exists():
        print("  ⚠️  index.html not found — skipping index update.")
        return

    html  = index_path.read_text(encoding="utf-8")
    slug  = meta["slug"]
    title = meta["title"]
    dt    = meta["date"]

    if f'href="/{slug}.html"' in html:
        print(f"  ℹ️  /{slug}.html already in index — skipping.")
        return

    new_li = (
        f'      <li>\n'
        f'        <span class="post-date">{dt}</span>\n'
        f'        <a href="/{slug}.html">{title}</a>\n'
        f'      </li>\n'
    )

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
