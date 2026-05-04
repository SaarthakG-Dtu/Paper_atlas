#!/usr/bin/env python3
"""
Fetch new world model papers from arxiv and append them to papers.js.

Usage:
  python scripts/fetch_papers.py              # last 18 months (catches missed quarters)
  python scripts/fetch_papers.py --months 6   # shorter window for quarterly runs

Runs quarterly via GitHub Actions (workflow_dispatch also available).
"""
import arxiv
import json
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ── arxiv queries ─────────────────────────────────────────────────────────────
# ti: = title field   cat: = arxiv category (cs.LG/cs.RO/cs.CV/cs.AI)
# Pinning to CS categories prevents physics/astro false positives.
QUERIES = [
    'ti:"world model" AND (cat:cs.LG OR cat:cs.AI OR cat:cs.RO OR cat:cs.CV)',
    'ti:"world models" AND (cat:cs.LG OR cat:cs.AI OR cat:cs.RO OR cat:cs.CV)',
    'ti:"world foundation model" AND (cat:cs.LG OR cat:cs.AI OR cat:cs.RO OR cat:cs.CV)',
    'ti:"neural world model" AND cat:cs.LG',
    'ti:"video world model" AND (cat:cs.LG OR cat:cs.CV)',
    'ti:"diffusion world model" AND (cat:cs.LG OR cat:cs.CV)',
    'ti:"latent world model" AND cat:cs.LG',
    'ti:"generative world model" AND (cat:cs.LG OR cat:cs.AI)',
]

# At least one of these must appear in title+abstract for a paper to be included
RELEVANCE_KEYWORDS = [
    "reinforcement learning", "model-based", "model based",
    "policy", "planning", "simulation", "robot", "driving",
    "dynamics model", "latent dynamics", "video generation",
    "game", "agent", "environment model", "imagination",
    "world model", "world models",
]

DEFAULT_LOOKBACK_MONTHS = 18


def is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def categorize(title: str, summary: str):
    text = (title + " " + summary).lower()

    if any(w in text for w in ["diffusion", "score matching", "ddpm", "ddim", "flow matching", "denoising"]):
        category = "diffusion"
    elif any(w in text for w in ["autoregressive", "gpt", "discrete token", "vq-vae", "vqvae", "codebook", "next-token"]):
        category = "autoregressive"
    elif any(w in text for w in ["transformer", "attention"]) and "latent" not in text:
        category = "autoregressive"
    elif any(w in text for w in ["latent space", "rssm", "variational", "vae", "latent dynamic", "latent representation"]):
        category = "latent"
    else:
        category = "hybrid"

    if any(w in text for w in ["driv", "vehicle", "waymo", "nuplan", "carla", "nuscenes", "autonomous"]):
        domain = "autonomous_driving"
    elif any(w in text for w in ["robot", "manipulation", "locomotion", "gripper", "dexterous", "embodied"]):
        domain = "robotics"
    elif any(w in text for w in ["atari", "minecraft", "game", "doom", "procgen", "gaming"]):
        domain = "gaming"
    elif any(w in text for w in ["video generation", "video synthesis", "text-to-video", "video prediction"]):
        domain = "video"
    else:
        domain = "general"

    if any(w in text for w in ["online", "reinforcement learning", "on-policy", "real-time interaction", "real robot"]):
        training = "online"
    else:
        training = "offline"

    return category, domain, training


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", title.lower())
    return s[:40].strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=DEFAULT_LOOKBACK_MONTHS,
                        help="How many months back to search")
    args = parser.parse_args()

    papers_js = Path(__file__).parent.parent / "papers.js"
    content = papers_js.read_text()

    existing_arxiv_ids = set(re.findall(r"arxiv\.org/abs/([0-9]+\.[0-9]+)", content))
    existing_titles_lower = set(t.lower() for t in re.findall(r'title:\s*"([^"]+)"', content))

    cutoff = datetime.now() - timedelta(days=args.months * 30)
    print(f"Searching arxiv for world model papers since {cutoff.strftime('%Y-%m-%d')} …\n")

    client = arxiv.Client(num_retries=3, delay_seconds=3)
    seen_ids: set[str] = set()
    new_papers = []

    for query in QUERIES:
        search = arxiv.Search(
            query=query,
            max_results=30,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        try:
            for result in client.results(search):
                pub_date = result.published.replace(tzinfo=None)
                if pub_date < cutoff:
                    break

                arxiv_id = result.get_short_id().split("v")[0]
                if arxiv_id in existing_arxiv_ids or arxiv_id in seen_ids:
                    continue
                if result.title.lower() in existing_titles_lower:
                    continue
                if not is_relevant(result.title, result.summary):
                    print(f"  skip (not relevant): {result.title}")
                    continue

                seen_ids.add(arxiv_id)

                category, domain, training = categorize(result.title, result.summary)
                year = result.published.year

                authors_list = [a.name.split()[-1] for a in result.authors[:3]]
                authors = ", ".join(authors_list)
                if len(result.authors) > 3:
                    authors += " et al."

                slug = f"{slugify(result.title)}_{year}"
                desc = result.summary[:220].replace("\n", " ").replace('"', '\\"')
                if len(result.summary) > 220:
                    desc += "…"

                new_papers.append({
                    "id": slug,
                    "title": result.title.replace('"', '\\"'),
                    "authors": authors,
                    "year": year,
                    "venue": "Preprint",
                    "category": category,
                    "domain": domain,
                    "training": training,
                    "arxiv": f"https://arxiv.org/abs/{arxiv_id}",
                    "tags": [],
                    "desc": desc,
                    "cites": [],
                })
        except Exception as exc:
            print(f"Warning: query failed — {exc}", file=sys.stderr)

    if not new_papers:
        print("No new relevant papers found.")
        return 0

    added_date = datetime.now().strftime("%Y-%m-%d")
    js_block = f"\n  // ══════ Auto-added {added_date} ══════\n"
    for p in new_papers:
        js_block += f"""  {{
    id: "{p['id']}",
    title: "{p['title']}",
    authors: "{p['authors']}",
    year: {p['year']},
    venue: "{p['venue']}",
    category: "{p['category']}",
    domain: "{p['domain']}",
    training: "{p['training']}",
    arxiv: "{p['arxiv']}",
    tags: [],
    desc: "{p['desc']}",
    cites: [],
  }},
"""

    updated = content.replace(
        "\n];\n\n// Build edges",
        js_block + "];\n\n// Build edges",
    )

    if updated == content:
        print("ERROR: Could not find insertion point in papers.js", file=sys.stderr)
        return 1

    papers_js.write_text(updated)
    print(f"\nAdded {len(new_papers)} paper(s):\n")
    for p in new_papers:
        print(f"  [{p['year']}] [{p['category']}/{p['domain']}] {p['title']}")
    return len(new_papers)


if __name__ == "__main__":
    result = main()
    sys.exit(0 if isinstance(result, int) and result >= 0 else 1)
