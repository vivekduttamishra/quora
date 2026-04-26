import os
import re
from bs4 import BeautifulSoup

# ── Config ───────────────────────────────────────────────────────────────────
INPUT_FILE = "answers.html"   # <-- change to your filename
# Files will be written to the current working directory
# ─────────────────────────────────────────────────────────────────────────────

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80]

def make_answer_html(question, content_html, created, language):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{question}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.7; color: #222; }}
    h1   {{ font-size: 1.5rem; color: #1a1a2e; }}
    .meta {{ font-size: 0.85rem; color: #666; margin-bottom: 24px; }}
    a    {{ color: #c0392b; }}
    blockquote {{ border-left: 4px solid #c0392b; margin: 16px 0; padding: 8px 16px; background: #fdf6f0; }}
  </style>
</head>
<body>
  <p><a href="index.html">← Back to Index</a></p>
  <h1>{question}</h1>
  <div class="meta">📅 {created} &nbsp;|&nbsp; 🌐 {language}</div>
  <div class="content">
    {content_html}
  </div>
</body>
</html>"""

def make_index_html(entries):
    rows = "\n".join(
        f'    <li><a href="{slug}.html">{question}</a> '
        f'<span class="date">{date}</span></li>'
        for question, slug, date in entries
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Quora Answers — Index</title>
  <style>
    body  {{ font-family: Georgia, serif; max-width: 860px; margin: 40px auto; padding: 0 20px; color: #222; }}
    h1    {{ font-size: 2rem; color: #1a1a2e; }}
    ul    {{ list-style: none; padding: 0; }}
    li    {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
    a     {{ text-decoration: none; color: #c0392b; font-size: 1.05rem; }}
    a:hover {{ text-decoration: underline; }}
    .date {{ font-size: 0.8rem; color: #999; margin-left: 10px; }}
  </style>
</head>
<body>
  <h1>📝 Quora Answers</h1>
  <p>{len(entries)} answers</p>
  <ul>
{rows}
  </ul>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

answer_blocks = []
for h2 in soup.find_all("h2"):
    if h2.get_text(strip=True).lower() == "answer":
        answer_blocks.append(h2.find_parent("p") or h2.parent)

entries = []
slug_counts = {}

for block in answer_blocks:
    q_span = block.find("span", class_="rendered_qtext")
    question = q_span.get_text(strip=True) if q_span else "Untitled"

    spans = block.find_all("span", class_="rendered_qtext")
    content_html = str(spans[1]) if len(spans) > 1 else "<p>No content.</p>"

    date_div = block.find("strong", string=lambda t: t and "Creation" in t)
    created  = date_div.find_next_sibling("span").get_text(strip=True) if date_div else "Unknown"

    lang_div = block.find("strong", string=lambda t: t and "language" in t)
    language = lang_div.find_next_sibling("span").get_text(strip=True) if lang_div else "Unknown"

    base_slug = slugify(question)
    if base_slug in slug_counts:
        slug_counts[base_slug] += 1
        slug = f"{base_slug}-{slug_counts[base_slug]}"
    else:
        slug_counts[base_slug] = 0
        slug = base_slug

    # Write directly to current directory — no subfolder
    with open(f"{slug}.html", "w", encoding="utf-8") as f:
        f.write(make_answer_html(question, content_html, created, language))

    entries.append((question, slug, created))
    print(f"  ✓  {slug}.html")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(make_index_html(entries))

print(f"\n✅ Done — {len(entries)} answers written to current directory.")