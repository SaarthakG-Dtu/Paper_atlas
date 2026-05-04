# wm_papers

An interactive graph of world model research papers. Browse by year, method, domain, and training paradigm.

**Live →** [shaswat2001.github.io/wm_papers](https://shaswat2001.github.io/wm_papers)

## What's here

A force-directed graph laid out in concentric year rings (2018–2025), with citation edges showing influence between papers. Filter by method (latent / diffusion / autoregressive), domain (robotics / gaming / driving / video), training type, or year. Search across titles, authors, and tags.

## Paper taxonomy

| Method | What it means |
|--------|--------------|
| Latent | RSSM, MuZero-style — learning dynamics in a learned latent space |
| Diffusion | Diffusion-based frame or trajectory prediction |
| Autoregressive | Transformer / token-based next-frame prediction |

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
  cites: ["other_paper_id"],    // papers this one influenced
}
```

Push to `main` and GitHub Actions will deploy automatically.

## Local dev

Just open `index.html` in a browser. No build step.

```bash
# or use a local server
python3 -m http.server 8000
```

## Future

- Google Scholar auto-scraper (GitHub Action + serpapi)
- Embedding-based semantic clustering
- BibTeX export per paper
- Community PRs for new papers
