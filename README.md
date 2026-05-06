# Metasurface Inverse Design Atlas

An interactive atlas of inverse design papers for metasurfaces and electromagnetic structures. Browse by method, application, data regime, and lineage.

**Live ->** [saarthakg-dtu.github.io/Paper_atlas](https://saarthakg-dtu.github.io/Paper_atlas)

## What's here

A force-directed graph laid out in concentric year rings (2018-2026). Curated backbone papers are connected by lineage edges showing research threads.

You can:
- filter by **method**, **application domain**, data regime, or year
- search across titles, authors, tags, and summaries
- switch between color-by-method and color-by-application
- use `Structured only` for the curated subset
- click any node to inspect tags, lineage, and related papers

## Taxonomy

| Method | What it means |
|--------|--------------|
| Optimization | Adjoint, topology optimization, genetic/evolutionary algorithms |
| Deep Learning | CNNs, transformers, tandem networks, ANNs |
| Generative | GANs, VAEs, diffusion models |
| Hybrid | Combinations of the above |
| Analytical | Equivalent circuit, closed-form, coupled-mode theory |

| Application | Examples |
|-------------|---------|
| Microwave | RIS, mmWave beam control |
| Antenna/Patch | Patch antenna, aperture arrays |
| Absorber | Perfect absorbers, wideband absorbers |
| Lens/Hologram | Metalens, flat optics, holographic metasurfaces |
| Filter | FSS, bandpass/bandstop surfaces |
| Beam Steering | Phased arrays, beam shaping |
| Sensing | EM sensors, imaging |

## Adding papers

Edit `papers.js`:

```js
{
  id: "unique_id",
  title: "Paper Title",
  authors: "Author et al.",
  year: 2025,
  venue: "Journal/Conference",
  category: "deep_learning",    // optimization | deep_learning | generative | hybrid | analytical
  domain: "microwave",          // microwave | antenna | absorber | lens_hologram | filter | beam_steering | sensing | general
  training: "supervised",       // supervised | unsupervised | reinforcement
  arxiv: "https://arxiv.org/abs/...",
  tags: ["tag1", "tag2"],
  desc: "One-line description.",
  cites: ["other_paper_id"],
  status: "structured",
}
```

## Local dev

```bash
open index.html   # or:
python3 -m http.server 8000
```
