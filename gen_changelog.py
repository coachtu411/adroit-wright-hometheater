#!/usr/bin/env python3
"""Regenerate changelog.html from git history of this directory.

Source of truth is git log itself -- this script produces a generated VIEW of it,
never hand-edited. Run this after any structural/architectural edit to index.html
or research.html (not needed for pricing/line-item edits, which have their own
in-tool Version History).

Usage: python3 gen_changelog.py   (run from inside site/)
"""
import subprocess
import html
import re
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
REPO_URL = "https://github.com/coachtu411/adroit-wright-hometheater"
SEP = "\x1f"
END = "\x1e"

AUTHOR_COLORS = {
    "AMOS": "amos",
}
def author_class(name):
    return AUTHOR_COLORS.get(name, "human")

def run_git_log():
    fmt = f"%H{SEP}%ad{SEP}%an{SEP}%s{SEP}%b{END}"
    out = subprocess.run(
        ["git", "log", "--date=format:%Y-%m-%d %H:%M", f"--pretty=format:{fmt}", "--", "."],
        cwd=SITE_DIR, capture_output=True, text=True, check=True,
    ).stdout
    entries = []
    for raw in out.split(END):
        raw = raw.strip("\n")
        if not raw.strip():
            continue
        parts = raw.split(SEP)
        if len(parts) < 5:
            continue
        h, date, author, subject, body = parts[0].lstrip("\n"), parts[1], parts[2], parts[3], parts[4].strip("\n")
        entries.append({"hash": h, "date": date, "author": author, "subject": subject, "body": body})
    return entries

def files_touched(h):
    out = subprocess.run(
        ["git", "show", "--stat", "--format=", h, "--", "."],
        cwd=SITE_DIR, capture_output=True, text=True, check=True,
    ).stdout
    files = []
    for line in out.splitlines():
        line = line.strip()
        m = re.match(r"^(\S+\.\w+)\s*\|", line)
        if m:
            files.append(m.group(1))
    return files

def split_blocks(body):
    """Git hard-wraps commit bodies at ~72 cols. Split into blank-line-separated blocks,
    each either a bullet list (lines starting with '- ') or a flowing-prose paragraph."""
    if not body.strip():
        return []
    return [b for b in body.strip().split("\n\n") if b.strip()]

def render_block(block):
    lines = [l.rstrip() for l in block.split("\n") if l.strip()]
    is_list = any(l.lstrip().startswith("- ") for l in lines)
    if not is_list:
        return f"<p>{html.escape(' '.join(block.split()))}</p>"
    items, current = [], None
    for l in lines:
        stripped = l.lstrip()
        if stripped.startswith("- "):
            if current is not None:
                items.append(current)
            current = stripped[2:].strip()
        elif current is not None:
            current += " " + stripped
    if current is not None:
        items.append(current)
    lis = "".join(f"<li>{html.escape(' '.join(item.split()))}</li>" for item in items)
    return f"<ul class='cl-body-list'>{lis}</ul>"

def render_entry(e):
    day = e["date"].split(" ")[0]
    time = e["date"].split(" ")[1]
    ac = author_class(e["author"])
    short = e["hash"][:7]
    body_html = "".join(render_block(b) for b in split_blocks(e["body"]))
    touched = files_touched(e["hash"])
    files_html = "".join(f'<span class="cl-file">{html.escape(f)}</span>' for f in touched)
    return f'''
    <div class="cl-entry">
      <div class="cl-entry-head">
        <span class="cl-time">{time}</span>
        <span class="cl-author {ac}">{html.escape(e["author"])}</span>
        <span class="cl-files">{files_html}</span>
      </div>
      <div class="cl-subject">{html.escape(e["subject"])}</div>
      {body_html}
      <div class="cl-meta">
        <a href="{REPO_URL}/commit/{e["hash"]}" target="_blank" rel="noopener">View diff on GitHub ↗</a>
        <code>{short}</code>
        <span class="cl-rollback">Rollback: <code>git checkout {short} -- {" ".join(touched) if touched else "index.html research.html"}</code></span>
      </div>
    </div>'''

def render_day_group(day, entries):
    rows = "".join(render_entry(e) for e in entries)
    return f'''
  <section class="cl-day">
    <h2>{day}</h2>
    {rows}
  </section>'''

def main():
    entries = run_git_log()
    entries.sort(key=lambda e: e["date"], reverse=True)
    by_day = {}
    for e in entries:
        day = e["date"].split(" ")[0]
        by_day.setdefault(day, []).append(e)
    days_html = "".join(render_day_group(day, by_day[day]) for day in by_day)
    total = len(entries)
    authors = sorted(set(e["author"] for e in entries))

    html_out = TEMPLATE.replace("{{DAYS}}", days_html).replace("{{TOTAL}}", str(total)).replace(
        "{{AUTHORS}}", ", ".join(html.escape(a) for a in authors)
    )
    out_path = SITE_DIR / "changelog.html"
    out_path.write_text(html_out)
    print(f"Wrote {out_path} — {total} commits, authors: {', '.join(authors)}")

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1F2D4D">
<title>Changelog — Site Edit History | Oliver Wright Project Hub</title>
<style>
  :root{
    --teal:#0E7C7B; --teal-dark:#0A5E5D; --teal-wash:#E6F2F1;
    --navy:#1F2D4D; --navy-wash:#EAEEF5;
    --amber:#C77F1A; --amber-wash:#FBF1DF;
    --red:#B23A3A; --red-wash:#FBEAEA;
    --green:#3F8F5F; --green-wash:#E9F5EE;
    --purple:#6B4E9E; --purple-wash:#EFEAF7;
    --ink:#23282E; --grey:#6B7480; --line:#DCE1E6; --bg:#F4F6F8;
  }
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%;overflow-x:hidden;}
  body{margin:0;background:var(--bg);color:var(--ink);overflow-x:hidden;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.5;-webkit-font-smoothing:antialiased;padding-bottom:60px;}
  a{color:var(--teal-dark);}
  .wrap{max-width:900px;margin:0 auto;padding:0 16px 40px;}
  header.masthead{background:linear-gradient(135deg,var(--navy) 0%,#16223b 100%);color:#fff;
    padding:22px 16px 20px;}
  header.masthead .inner{max-width:900px;margin:0 auto;}
  .brand{font-weight:800;letter-spacing:3px;font-size:11.5px;color:#8fd3d2;text-transform:uppercase;}
  header.masthead h1{margin:8px 0 6px;font-size:21px;line-height:1.3;font-weight:700;}
  header.masthead .sub{color:#cdd6e6;font-size:13px;}
  .amberline{height:4px;background:linear-gradient(90deg,var(--teal),var(--navy),var(--purple),var(--amber));}
  .cl-back-bar{background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;text-align:center;}
  .cl-back-bar a{font-weight:700;font-size:13px;text-decoration:none;}
  .cl-back-bar a:hover{text-decoration:underline;}
  .cl-tldr{margin:22px 0;background:var(--navy-wash);border:1px solid #c8d2e6;border-left:6px solid var(--navy);
    border-radius:14px;padding:16px 18px;font-size:13.5px;line-height:1.65;color:var(--navy);}
  .cl-tldr b{color:var(--navy);}
  .cl-tldr .cl-warn{margin-top:10px;padding:10px 12px;background:var(--amber-wash);border-radius:8px;
    border-left:4px solid var(--amber);font-size:12.5px;color:#5a4419;}
  .cl-day{margin:28px 0;}
  .cl-day h2{font-size:12px;font-weight:800;letter-spacing:1.1px;text-transform:uppercase;color:var(--teal-dark);
    border-bottom:2px solid var(--teal);padding-bottom:8px;margin:0 0 14px;}
  .cl-entry{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:10px;
    box-shadow:0 1px 2px rgba(31,45,77,.05);}
  .cl-entry-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;}
  .cl-time{font-size:11px;font-weight:800;color:var(--grey);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}
  .cl-author{font-size:10px;font-weight:800;letter-spacing:.4px;text-transform:uppercase;border-radius:20px;
    padding:2px 9px;}
  .cl-author.amos{background:var(--teal-wash);color:var(--teal-dark);}
  .cl-author.human{background:var(--purple-wash);color:var(--purple);}
  .cl-files{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto;}
  .cl-file{font-size:10px;font-weight:700;background:var(--navy-wash);color:var(--navy);border-radius:6px;
    padding:2px 7px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}
  .cl-subject{font-weight:700;color:var(--navy);font-size:14px;line-height:1.4;}
  .cl-entry p{font-size:13px;line-height:1.6;color:var(--ink);margin:6px 0 0;}
  .cl-body-list{margin:6px 0 0;padding-left:18px;}
  .cl-body-list li{font-size:13px;line-height:1.6;color:var(--ink);margin:4px 0;}
  .cl-meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:10px;padding-top:10px;
    border-top:1px solid var(--line);font-size:11.5px;}
  .cl-meta a{font-weight:700;text-decoration:none;}
  .cl-meta a:hover{text-decoration:underline;}
  .cl-meta code{background:var(--navy-wash);color:var(--navy);border-radius:4px;padding:2px 6px;
    font-size:10.5px;}
  .cl-rollback{color:var(--grey);}
  .cl-rollback code{background:var(--amber-wash);color:#8a5c0f;}
  footer{text-align:center;color:var(--grey);font-size:11.5px;padding:22px 16px 8px;line-height:1.6;}
  footer a{color:var(--teal-dark);}
  @media (max-width:640px){
    header.masthead h1{font-size:19px;}
    .cl-files{margin-left:0;}
  }
</style>
</head>
<body>

<header class="masthead">
  <div class="inner">
    <div class="brand">ADROIT COMMUNICATIONS</div>
    <h1>Changelog — Site Edit History</h1>
    <div class="sub">Oliver Wright Residence · ADR-2026-WRIGHT · Georgetown, Washington DC</div>
  </div>
</header>
<div class="amberline"></div>
<div class="cl-back-bar"><a href="index.html">← Back to project hub</a></div>

<div class="wrap">
  <div class="cl-tldr">
    <b>Structural/architectural site changes only</b> — every edit to <code>index.html</code> and
    <code>research.html</code> (new pages, layout, features, sections), newest first. This is generated
    directly from git history, not hand-maintained — regenerate with <code>python3 gen_changelog.py</code>
    after any future edit. <b>{{TOTAL}} commits</b> so far, from: {{AUTHORS}}.
    <div class="cl-warn">
      <b>Not the same as pricing/line-item versioning</b> — editing the estimate itself (quantities, rates,
      active toggles, notes) is tracked separately by the in-tool <b>🕘 Version History</b> button on the
      project hub (browser-local, auto-snapshots + one-click revert). This page is for structural changes
      to the page itself. To roll back a structural change: click "View diff" below to see exactly what
      changed on GitHub, or run the <code>git checkout</code> command shown under any entry, or use GitHub's
      own revert-commit button on the <a href="''' + REPO_URL + '''/commits/main" target="_blank" rel="noopener">full commit history</a>.
    </div>
  </div>

  {{DAYS}}
</div>

<footer>
  Adroit Communications LLC · Living project hub &amp; edit history · ADR-2026-WRIGHT · not for client
  distribution. Generated from <code>git log</code> in
  <code>data/project_records/ADR-2026-WRIGHT/site/</code>.
</footer>

</body>
</html>
'''

if __name__ == "__main__":
    main()
