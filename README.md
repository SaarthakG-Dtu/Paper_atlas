# World Models Atlas

An interactive atlas of world model research papers. Browse the field by year, method, domain, training paradigm, and lineage.

**Live →** [shaswat2001.github.io/wm_papers](https://shaswat2001.github.io/wm_papers)

## What's here

A force-directed graph laid out in concentric year rings, now spanning `2018-2026`. The graph mixes a curated backbone of foundational papers with newer exploratory additions, and uses lineage edges to show which papers build on or belong to the same research thread.

You can:

- filter by method, domain, training type, or year
- search across titles, authors, tags, and summaries
- switch between color-by-method and color-by-domain
- use `Structured only` to focus on the cleaner curated subset
- open any paper to inspect its tags, lineage, and related-track suggestions

## Paper taxonomy

| Method | What it means |
|--------|--------------|
| Latent | RSSM, MuZero-style — learning dynamics in a learned latent space |
| Diffusion | Diffusion-based frame or trajectory prediction |
| Autoregressive | Transformer / token-based next-frame prediction |
| Hybrid | Mixed or cross-paradigm world modeling approaches |

| Domain | Examples |
|--------|---------|
| Robotics | DayDreamer, PWM, RoboDreamer |
| Gaming | Dreamer series, IRIS, DIAMOND, Oasis |
| Driving | GAIA, VISTA, Cosmos, Copilot4D |
| Video | Sora, UniSim |
| General | TD-MPC2, DreamerV3 |

## Adding papers

Edit `papers.js` — add an entry to the `PAPERS` array:

```js
{
  id: "unique_id",
  title: "Paper Title",
  authors: "Author et al.",
  year: 2025,
  venue: "Conference",
  category: "latent",           // latent | diffusion | autoregressive
  domain: "robotics",           // robotics | gaming | autonomous_driving | video | general
  training: "online",           // online | offline | both
  arxiv: "https://arxiv.org/abs/...",
  tags: ["tag1", "tag2"],
  desc: "One-line description.",
  cites: ["other_paper_id"],    // papers this work builds on / should connect to
  status: "structured",         // optional: mark curated entries explicitly
}
```

Notes:

- `cites` is used as a graph-link field, not a strict bibliography dump.
- For recent auto-added papers, it is normal to add lineage links manually after ingestion.
- The UI treats papers with stronger metadata more prominently; sparse auto-added entries still appear, but can be hidden with `Structured only`.

## Auto-ingest workflow

The repo includes [`scripts/fetch_papers.py`](/Users/shaswatgarg/Documents/Projects/wm_papers/scripts/fetch_papers.py), which pulls recent arXiv papers matching world-model-related queries and appends them to `papers.js`.

What it does well:

- catches recent preprints that match the title/query heuristics
- guesses method, domain, and training mode
- avoids re-adding papers already present by title or arXiv ID

What still needs manual cleanup:

- adding tags
- writing better summaries
- fixing occasional misclassified domains or categories
- adding `cites` lineage links so the graph is actually useful

Push to `main` and GitHub Actions will deploy automatically.

## Local dev

Just open `index.html` in a browser. No build step.

```bash
# or use a local server
python3 -m http.server 8000
```

## Future

- split the dataset into clearly curated vs auto-ingested sections
- add a timeline/list view alongside the graph
- improve automatic tagging and linkage suggestions
- add BibTeX export per paper
- support community PRs for new papers and metadata cleanup
