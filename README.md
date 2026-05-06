# Pixelated Metasurface Inverse Design Atlas

An interactive graph atlas of inverse design methods for pixelated electromagnetic
metasurfaces. Browse by method, application, data regime, and lineage.

**Live ->** [saarthakg-dtu.github.io/Paper_atlas](https://saarthakg-dtu.github.io/Paper_atlas)

## What's here

A force-directed graph in concentric year rings (1995-2025). Curated backbone papers
are connected by lineage edges showing research threads from foundational PSO/GA/ACO
optimisation through to deep generative models.

Filter by **method**, **application**, data regime, or year. Click any node to inspect
tags, lineage, and related papers. Use `Structured only` for the curated backbone.

## Taxonomy

| Method | What it means |
|--------|--------------|
| Optimization | BPSO, ACO, GA, adjoint, topology optimisation, surrogate-assisted |
| Deep Learning | CNN, tandem networks, transformers, ANN, reinforcement learning |
| Generative | GAN, VAE, diffusion models, VAE-PSO hybrid |
| Hybrid | Surrogate + NSGA-II, BPSO + CNN, VAE + PSO, physics-informed NN |
| Analytical | Equivalent circuit, coupled-mode, closed-form FSS theory |

| Application | Examples |
|-------------|---------|
| FSS / Filter | MOLACO 3D-FSS, MVBPSO bandpass/bandstop, MC-cGAN |
| Patch Antenna | MOTOL, surrogate Pareto, SVR reflectarray |
| Microwave / RIS | BPSO checkerboard, microwave cloak, RIS beamforming |
| Absorber | RL absorber, ACDL adaptive cascade |
| Beam Steering | GAN metagrating, space-time coding |
| Lens / Hologram | Topology opt metalens, hologram GAN |
| Sensing | ML reprogrammable imager |

## Adding papers

Edit `papers.js`:

```js
{
  id: "unique_id",
  title: "Paper Title",
  authors: "Author et al.",
  year: 2025,
  venue: "Journal/Conference",
  category: "optimization",   // optimization | deep_learning | generative | hybrid | analytical
  domain: "filter",           // filter | antenna | microwave | absorber | beam_steering | lens_hologram | sensing | general
  training: "supervised",     // supervised | unsupervised | reinforcement
  arxiv: "https://arxiv.org/abs/...",
  tags: ["tag1", "tag2"],
  desc: "One-line description.",
  cites: ["other_paper_id"],
  status: "structured",
}
```

## Auto-ingest

`scripts/fetch_papers.py` pulls recent arXiv papers matching pixelated metasurface
queries quarterly via GitHub Actions. Push to `main` to deploy automatically.

## Local dev

```bash
open index.html
# or:
python3 -m http.server 8000
```
