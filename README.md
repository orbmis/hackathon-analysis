# ETHGlobal Hackathon Analysis

Data pipeline and analysis of **8,200 ETHGlobal showcase projects** scraped from the
[ETHGlobal Explorer](https://www.ethglobalexplorer.com). It clusters project descriptions into
themes, tracks how the project mix has shifted over time, analyses which categories actually win
sponsor prizes, and builds a **forward-looking "sponsor-alpha" forecast** for upcoming hackathons.

The full write-up of findings is in **[`patterns_report.md`](patterns_report.md)** (§1–§9).

## Headline findings

- **The NFT → AI rotation.** NFTs fell from ~40% of an early cohort to ~4%; AI agents went the
  opposite way (~1% → 20–40%). Payments rose steadily; DAOs and gaming faded.
- **Prizes are era-confounded.** Older events award prizes far more often (~61% vs ~22%). After
  era-adjusting, **AI agents over-perform (1.19×)** while **cross-chain swaps under-perform (0.63×)**.
- **The agent edge was bought.** Coinbase Developer Platform alone = 47.6% of agent prizes, and the
  lift lives almost entirely in the *Agentic Ethereum* themed hackathon.
- **Sponsor-alpha model.** Specialist sponsors (1inch, Coinbase, Uniswap, Unlock, Lens) earmark
  categories; the alpha window opens at a category's themed moment and closes on saturation.
- **Forward forecast (mid-2026).** The easy windows have closed — agents are cooling, cross-chain is
  a saturation trap, DeFi lending is the least-bad-but-crowded bet, and 10/14 categories have no
  specialist sponsor money at all.

## Pipeline

Each stage writes artifacts consumed by the next. Run them in order from the repo root.

| Stage | Script | Produces | Report |
|------|--------|----------|--------|
| 1. Pull projects | `pull_projects.py` | `ethglobal_projects.csv` | — |
| 2. Theme analysis | `analyze_descriptions.py` | `ethglobal_projects_enriched.csv`, `cluster_summaries.json`, `analysis_stats.json` | §1–§4 |
| 3. Sub-themes | `subcluster_themes.py` | `subcluster_summaries.json` (+ `subtheme_label` column) | §5 |
| 4. Agent deep-dive | `agent_deepdive.py` | `agent_subclusters.json` | §7 |
| 5. Sponsor-alpha model | `sponsor_alpha.py` | `sponsor_alpha.json` | §6, §8 |
| 6. Scrape event data | `scrape_events.py` | `event_meta.csv`, `event_sponsors.csv` | §9 |
| 7. Forward forecast | `forecast_alpha.py` | `alpha_forecast.{csv,json}`, `sponsor_recurrence.csv` | §9 |

> Theme/sub-theme names are human-assigned in `cluster_labels.json` / `subtheme_labels.json` — edit
> those and re-run stage 2/3 to relabel (embeddings are cached, so it's instant and deterministic).

## Quick start

```bash
# scrapers use stdlib urllib; analysis needs these
pip install numpy pandas scikit-learn sentence-transformers certifi

python3 pull_projects.py          # ~10 min, rate-limited; resumable (skips saved rows)
python3 analyze_descriptions.py   # downloads all-MiniLM-L6-v2 (~80MB) on first run
python3 subcluster_themes.py
python3 agent_deepdive.py
python3 sponsor_alpha.py
python3 scrape_events.py          # ~3 min, rate-limited scrape of ethglobal.com
python3 forecast_alpha.py
```

Both scrapers (`pull_projects.py`, `scrape_events.py`) self-rate-limit with random delays and retry
on transient failures. `pull_projects.py` is resumable — re-run it (or use `--start-page N`) and it
skips rows already in the CSV.

## Key outputs

- **[`patterns_report.md`](patterns_report.md)** — the narrative report, §1–§9.
- **`ethglobal_projects_enriched.csv`** — every project tagged with `theme_label`, `subtheme_label`,
  `cluster_keywords`, `tech_tags`, `time_bucket`, `is_outlier`, etc. Slice it yourself.
- **`alpha_forecast.csv`** — per-category forward alpha index for upcoming events.
- **`event_sponsors.csv`** — real per-sponsor `$` prize pools across 49 past events.

## Method notes & caveats

- **Themes** come from sentence-transformer embeddings (`all-MiniLM-L6-v2`) + KMeans (k=14,
  silhouette-selected). Cluster boundaries are soft (low silhouette is expected for short texts).
- **Chronology** uses project `id` as a recency proxy (the explorer exposes no dates); reliable for
  the coarse old→new split, approximate for exact timing.
- **Prize win-rate** uses `prize_count > 0` as a win proxy, era-adjusted against per-cohort baselines.
- **The forecast is a projection, not a guarantee:** upcoming sponsors are *predicted* (upcoming event
  pages don't publish them yet), and there is a **~7-month staleness gap** — sponsor data runs to
  May 2026 while project supply/momentum end at Buenos Aires (Nov 2025). Anchored at 2026-06-10.

Per-section caveats are documented inline in `patterns_report.md`.

## Repo layout

```
pull_projects.py            Stage 1 — paginated, resumable project scraper
analyze_descriptions.py     Stage 2 — embeddings, clustering, NLP, tech lexicon
subcluster_themes.py        Stage 3 — sub-cluster the two largest themes
agent_deepdive.py           Stage 4 — decompose the AI-agent prize lift
sponsor_alpha.py            Stage 5 — earmark scores, themed-event premium, decay
scrape_events.py            Stage 6 — scrape event dates + per-sponsor $ pools
forecast_alpha.py           Stage 7 — recurrence model + category alpha index
cluster_labels.json         Human theme names (cluster_id -> label/gloss)
subtheme_labels.json        Human sub-theme names
patterns_report.md          Findings write-up (§1–§9)
*.csv / *.json              Generated data artifacts (see table above)
```

`.cache_embeddings.npy` (the ~12MB embedding cache) is git-ignored and regenerated on demand.
