#!/usr/bin/env python3
"""Export seen_jobs.json and scrape pools into an SQLite database (jobs.db)
and generate an interactive, searchable HTML Job Dashboard.

Usage:
    python3 tools/export_sqlite.py
    python3 tools/export_sqlite.py --db job_scraper/jobs.db --html reports/dashboard.html
"""

import argparse
import html
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SEEN = ROOT / "job_scraper" / "seen_jobs.json"
DEFAULT_DB = ROOT / "job_scraper" / "jobs.db"
DEFAULT_HTML = ROOT / "job_scraper" / "logs" / "dashboard.html"


def export_to_sqlite(seen_path, db_path):
    """Populate SQLite database from seen_jobs.json."""
    if not Path(seen_path).is_file():
        return 0

    with open(seen_path, encoding="utf-8") as f:
        data = json.load(f)

    seen = data.get("seen", {})
    if not seen:
        return 0

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        dedup_key TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        portal TEXT,
        url TEXT,
        profile TEXT,
        first_seen TEXT,
        status TEXT,
        fit TEXT,
        also_on TEXT
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_portal ON jobs(portal)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_first_seen ON jobs(first_seen)")

    count = 0
    for key, job in seen.items():
        if not isinstance(job, dict):
            continue
        also_on_str = json.dumps(job.get("also_on", []), ensure_ascii=False)
        cur.execute("""
        INSERT OR REPLACE INTO jobs (
            dedup_key, title, company, location, portal, url, profile, first_seen, status, fit, also_on
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key,
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("portal"),
            job.get("url"),
            job.get("profile"),
            job.get("first_seen"),
            job.get("status", "new"),
            job.get("fit"),
            also_on_str,
        ))
        count += 1

    conn.commit()
    conn.close()
    return count


def generate_interactive_dashboard(seen_path, html_path):
    """Generate a modern, client-side searchable HTML dashboard."""
    if not Path(seen_path).is_file():
        return

    with open(seen_path, encoding="utf-8") as f:
        data = json.load(f)

    jobs = []
    for key, j in data.get("seen", {}).items():
        if isinstance(j, dict):
            item = dict(j)
            item["dedup_key"] = key
            jobs.append(item)

    # Sort most recent first
    jobs.sort(key=lambda x: x.get("first_seen") or "", reverse=True)

    html_path = Path(html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    jobs_json = json.dumps(jobs, ensure_ascii=False)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Economics Job Board Explorer</title>
<style>
  :root {{
    --bg: #f8fafc;
    --card: #ffffff;
    --border: #e2e8f0;
    --text: #0f172a;
    --muted: #64748b;
    --primary: #2563eb;
    --primary-light: #eff6ff;
    --badge-bg: #f1f5f9;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 24px; }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  header {{ margin-bottom: 24px; }}
  h1 {{ font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 6px; }}
  p.subtitle {{ color: var(--muted); font-size: 14px; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; background: var(--card); padding: 16px; border-radius: 8px; border: 1px solid var(--border); }}
  .search-box {{ flex: 1; min-width: 260px; }}
  input[type="text"] {{ width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; outline: none; }}
  input[type="text"]:focus {{ border-color: var(--primary); box-shadow: 0 0 0 2px rgba(37,99,235,0.15); }}
  select {{ padding: 10px 14px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; background: #fff; outline: none; }}
  .stats-bar {{ margin-bottom: 16px; font-size: 14px; color: var(--muted); }}
  .job-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }}
  .job-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 18px; transition: transform 0.15s, box-shadow 0.15s; display: flex; flex-direction: column; }}
  .job-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }}
  .job-title {{ font-size: 16px; font-weight: 600; color: #1e293b; text-decoration: none; margin-bottom: 6px; line-height: 1.3; }}
  .job-title:hover {{ color: var(--primary); text-decoration: underline; }}
  .job-company {{ font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 4px; }}
  .job-location {{ font-size: 13px; color: var(--muted); margin-bottom: 12px; }}
  .badge-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; padding-top: 10px; border-top: 1px solid #f1f5f9; }}
  .badge {{ font-size: 11px; font-weight: 500; padding: 3px 8px; border-radius: 4px; background: var(--badge-bg); color: var(--muted); }}
  .badge-portal {{ background: #e0f2fe; color: #0369a1; }}
  .badge-date {{ background: #fef3c7; color: #92400e; }}
  .empty-state {{ grid-column: 1 / -1; text-align: center; padding: 48px; color: var(--muted); background: var(--card); border-radius: 8px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Economics Job Board Explorer</h1>
    <p class="subtitle">Interactive database of all scraped, deduplicated, and ranked job opportunities.</p>
  </header>

  <div class="controls">
    <div class="search-box">
      <input type="text" id="search" placeholder="Search by title, employer, location, keywords..." oninput="filterJobs()">
    </div>
    <select id="portalFilter" onchange="filterJobs()">
      <option value="">All Portals</option>
    </select>
    <select id="profileFilter" onchange="filterJobs()">
      <option value="">All Profiles</option>
    </select>
  </div>

  <div class="stats-bar" id="statsBar">Loading jobs...</div>
  <div class="job-grid" id="jobGrid"></div>
</div>

<script>
  const allJobs = {jobs_json};

  // Populate filter dropdowns
  const portals = new Set();
  const profiles = new Set();
  allJobs.forEach(j => {{
    if (j.portal) portals.add(j.portal);
    if (j.profile) profiles.add(j.profile);
  }});

  const portalSelect = document.getElementById('portalFilter');
  Array.from(portals).sort().forEach(p => {{
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    portalSelect.appendChild(opt);
  }});

  const profileSelect = document.getElementById('profileFilter');
  Array.from(profiles).sort().forEach(p => {{
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    profileSelect.appendChild(opt);
  }});

  function escapeHtml(str) {{
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }}

  function filterJobs() {{
    const query = document.getElementById('search').value.toLowerCase().trim();
    const portal = document.getElementById('portalFilter').value;
    const profile = document.getElementById('profileFilter').value;

    const filtered = allJobs.filter(j => {{
      if (portal && j.portal !== portal) return false;
      if (profile && j.profile !== profile) return false;
      if (query) {{
        const text = ((j.title || '') + ' ' + (j.company || '') + ' ' + (j.location || '') + ' ' + (j.profile || '')).toLowerCase();
        if (!text.includes(query)) return false;
      }}
      return true;
    }});

    render(filtered);
  }}

  function render(jobs) {{
    const grid = document.getElementById('jobGrid');
    const stats = document.getElementById('statsBar');
    stats.textContent = `Showing ${{jobs.length}} of ${{allJobs.length}} job opportunities`;

    if (jobs.length === 0) {{
      grid.innerHTML = '<div class="empty-state">No matching job postings found.</div>';
      return;
    }}

    grid.innerHTML = jobs.map(j => {{
      const url = j.url || '#';
      const title = escapeHtml(j.title || 'Untitled');
      const company = escapeHtml(j.company || '—');
      const location = escapeHtml(j.location || 'Germany');
      const portal = escapeHtml(j.portal || 'direct');
      const date = escapeHtml(j.first_seen || '');
      const profile = escapeHtml(j.profile || '');
      const alsoOn = j.also_on && j.also_on.length ? `+${{j.also_on.length}} portals` : '';

      return `
        <div class="job-card">
          <a href="${{escapeHtml(url)}}" target="_blank" rel="noopener noreferrer" class="job-title">${{title}}</a>
          <div class="job-company">${{company}}</div>
          <div class="job-location">📍 ${{location}}</div>
          <div class="badge-row">
            <span class="badge badge-portal">${{portal}}</span>
            ${{profile ? `<span class="badge">${{profile}}</span>` : ''}}
            ${{date ? `<span class="badge badge-date">📅 ${{date}}</span>` : ''}}
            ${{alsoOn ? `<span class="badge">${{alsoOn}}</span>` : ''}}
          </div>
        </div>
      `;
    }}).join('');
  }}

  // Initial render
  filterJobs();
</script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)


def main():
    parser = argparse.ArgumentParser(description="Export seen_jobs to SQLite & Interactive HTML")
    parser.add_argument("--seen", default=str(DEFAULT_SEEN), help="Path to seen_jobs.json")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Output SQLite database path")
    parser.add_argument("--html", default=str(DEFAULT_HTML), help="Output interactive HTML dashboard path")
    args = parser.parse_args()

    count = export_to_sqlite(args.seen, args.db)
    print(f"Exported {count} jobs to SQLite database: {args.db}")

    generate_interactive_dashboard(args.seen, args.html)
    print(f"Generated interactive HTML dashboard: {args.html}")


if __name__ == "__main__":
    main()
