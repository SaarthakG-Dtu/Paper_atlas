#!/usr/bin/env python3
"""
Fetch new world model papers from arxiv and append them to papers.js.
Run quarterly via GitHub Actions, or manually: python scripts/fetch_papers.py
"""
import arxiv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

QUERIES = [
    "world model reinforcement learning",
    "world model robot manipulation",
    "world model autonomous driving",
    "diffusion world model",
    "latent world model video prediction",
    "generative world model planning",
    "neural world model policy",
]

LOOKBACK_MONTHS = 4


def categorize(title: str, summary: str):
    text = (title + " " + summary).lower()

    if any(w in text for w in ["diffusion", "score matching", "ddpm", "ddim", "flow matching"]):
        category = "diffusion"
    elif any(w in text for w in ["autoregressive", "transformer", "gpt", "token-based", "vq-vae", "discrete token"]):
        category = "autoregressive"
    elif any(w in text for w in ["latent space", "rssm", "variational", "vae", "latent dynamic"]):
        category = "latent"
    else:
        category = "hybrid"

    if any(w in text for w in ["driv", "vehicle", "waymo", "nuplan", "carla", "nuScenes"]):
        domain = "autonomous_driving"
    elif any(w in text for w in ["robot", "manipulation", "locomotion", "gripper", "dexterous"]):
        domain = "robotics"
    elif any(w in text for w in ["atari", "minecraft", "game", "doom", "openai gym", "procgen"]):
        domain = "gaming"
    elif any(w in text for w in ["video generation", "video synthesis", "text-to-video"]):
        domain = "video"
    else:
        domain = "general"

    if any(w in text for w in ["online", "reinforcement learning", "on-policy", "real-time interaction"]):
        training = "online"
    else:
        training = "offline"

    return category, domain, training


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", title.lower())
    return s[:40].strip("_")


def main():
    papers_js = Path(__file__).parent.parent / "papers.js"
    content = papers_js.read_text()

    existing_arxiv_ids = set(re.findall(r"arxiv\.org/abs/([0-9]+\.[0-9]+)", content))
    existing_titles = set(t.lower() for t in re.findall(r'title:\s*"([^"]+)"', content))

    cutoff = datetime.now() - timedelta(days=LOOKBACK_MONTHS * 30)

    client = arxiv.Client(num_retries=3, delay_seconds=3)
    seen_ids: set[str] = set()
    new_papers = []

    for query in QUERIES:
        search = arxiv.Search(
            query=query,
            max_results=25,
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
                if result.title.lower() in existing_titles:
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
            print(f"Warning: query '{query}' failed — {exc}", file=sys.stderr)

    if not new_papers:
        print("No new papers found.")
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

    # Insert before the closing ]; of the PAPERS array
    updated = content.replace(
        "\n];\n\n// Build edges",
        js_block + "];\n\n// Build edges",
    )

    if updated == content:
        print("ERROR: Could not find insertion point in papers.js", file=sys.stderr)
        return 1

    papers_js.write_text(updated)
    print(f"Added {len(new_papers)} new paper(s):")
    for p in new_papers:
        print(f"  [{p['category']}/{p['domain']}] {p['title']} ({p['year']})")
    return len(new_papers)


if __name__ == "__main__":
    result = main()
    sys.exit(0 if isinstance(result, int) and result >= 0 else 1)
