#!/usr/bin/env python3
"""
Fetch new metasurface inverse design papers from arxiv and append them to papers.js.

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
# ti: = title field   cat: = arxiv category (cs.LG/cs.AI/eess.SP/physics.optics)
# Pinning to these categories reduces unrelated arXiv false positives.
QUERIES = [
    'ti:"metasurface" AND ti:"inverse design" AND (cat:cs.LG OR cat:cs.AI OR cat:eess.SP OR cat:physics.optics)',
    'ti:"inverse design" AND ti:"metasurface" AND (cat:cs.LG OR cat:eess.SP)',
    'ti:"deep learning" AND ti:"metasurface" AND (cat:cs.LG OR cat:eess.SP OR cat:physics.optics)',
    'ti:"neural network" AND ti:"metasurface" AND cat:eess.SP',
    'ti:"generative" AND ti:"metasurface" AND (cat:cs.LG OR cat:eess.SP)',
    'ti:"metasurface" AND ti:"optimization" AND (cat:eess.SP OR cat:physics.optics)',
    'ti:"programmable metasurface" AND (cat:eess.SP OR cat:cs.LG)',
    'ti:"reconfigurable metasurface" AND (cat:eess.SP OR cat:cs.LG)',
    'ti:"intelligent metasurface" AND (cat:eess.SP OR cat:cs.AI)',
    'ti:"microwave metasurface" AND ti:"design" AND cat:eess.SP',
    'ti:"patch antenna" AND ti:"machine learning" AND cat:eess.SP',
    'ti:"RIS" AND ti:"deep learning" AND (cat:eess.SP OR cat:cs.IT)',
]

# At least one of these must appear in title+abstract for a paper to be included
RELEVANCE_KEYWORDS = [
    "metasurface", "meta-surface", "metaatom", "meta-atom",
    "inverse design", "inverse problem",
    "electromagnetic", "em simulation",
    "unit cell", "subwavelength",
    "reconfigurable intelligent surface", "RIS",
    "beam steering", "beam forming",
    "absorber", "absorbing",
    "hologram", "holographic",
    "patch antenna", "microstrip",
    "bandpass filter", "bandstop",
    "coding metasurface", "programmable",
    "topology optimization",
]

DEFAULT_LOOKBACK_MONTHS = 18


def is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def categorize(title: str, summary: str):
    text = (title + " " + summary).lower()

    # METHOD (category)
    if any(w in text for w in ["diffusion model", "ddpm", "score-based", "flow matching", "gan", "vae", "generative adversarial", "variational autoencoder", "denoising"]):
        category = "generative"
    elif any(w in text for w in ["deep learning", "neural network", "cnn", "transformer", "attention", "lstm", "mlp", "ann", "tandem"]):
        category = "deep_learning"
    elif any(w in text for w in ["adjoint", "gradient descent", "topology optim", "genetic algorithm", "particle swarm", "evolutionary", "simulated annealing", "bayesian optim"]):
        category = "optimization"
    elif any(w in text for w in ["analytical", "closed-form", "equivalent circuit", "transmission line", "coupled mode"]):
        category = "analytical"
    else:
        category = "hybrid"

    # DOMAIN (application area)
    if any(w in text for w in ["patch antenna", "microstrip", "antenna array", "aperture antenna"]):
        domain = "antenna"
    elif any(w in text for w in ["microwave", "millimeter wave", "mmwave", "mm-wave", "ghz", "radar", "ris", "reconfigurable intelligent"]):
        domain = "microwave"
    elif any(w in text for w in ["absorb", "perfect absorber", "wideband absorb", "narrowband absorb"]):
        domain = "absorber"
    elif any(w in text for w in ["hologram", "holograph", "lens", "flat lens", "metalens"]):
        domain = "lens_hologram"
    elif any(w in text for w in ["filter", "bandpass", "bandstop", "frequency selective"]):
        domain = "filter"
    elif any(w in text for w in ["beam steer", "beam form", "beam shap", "beam split", "radiation pattern"]):
        domain = "beam_steering"
    elif any(w in text for w in ["sensor", "sensing", "detect", "imaging"]):
        domain = "sensing"
    else:
        domain = "general"

    # DATA REGIME (training)
    if any(w in text for w in ["reinforcement learning", "reward", "agent", "policy"]):
        training = "reinforcement"
    elif any(w in text for w in ["unsupervised", "self-supervised", "generative", "unlabeled", "autoencoder"]):
        training = "unsupervised"
    else:
        training = "supervised"

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
    print(f"Searching arxiv for metasurface inverse design papers since {cutoff.strftime('%Y-%m-%d')} ...\n")

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
