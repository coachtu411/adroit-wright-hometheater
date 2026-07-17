# Wright Residence — Home Theater Project Hub

Shared, editable project page for Tunde and Claudio — built with Claude Code, hosted free on GitHub Pages
(no Wix/Squarespace/build step). One `index.html` file, no dependencies.

**Live site:** set after first deploy — see below.

## Editing

- **Quickest:** open `index.html` on github.com, click the pencil (edit) icon, make changes, commit directly
  to `main`. The live site updates automatically within about a minute.
- **Bigger changes / ask Claude:** `git clone` this repo (or point Claude Code at it) and edit `index.html`
  locally, then `git push`.

## What's on the page

Contacts, scope summary, the current draft estimate (both pricing options), a timeline of the engagement,
and open items still blocking a final send. Source of truth for the underlying data lives in the Adroit
brain at `data/project_records/ADR-2026-WRIGHT/` — update there first, then reflect changes here.

## Notes

- `robots.txt` blocks search-engine indexing (`noindex`/`Disallow: /`) — the page is still publicly
  reachable by anyone with the link, it just won't show up in Google.
- This repo is **public** (GitHub Pages free tier requires it for a repo this size/account). Don't add
  anything more sensitive than what's already here (no SSNs, account numbers, etc.).
