# Emergent patterns in ETHGlobal project descriptions

**Corpus:** 8,200 ETHGlobal showcase projects (IDs 8088–16287) across 38 hackathon
events. 8,199 non-empty descriptions, 8,169 unique; short tagline texts (median 14
words). **Method:** sentence-transformer embeddings (`all-MiniLM-L6-v2`) → KMeans
(k=14, silhouette-selected) for themes; deterministic TF-IDF / n-gram / lexicon
analysis for tech terms; `id`-ordered time buckets for trends; Claude for theme
labelling and synthesis.

> **Read the time axis with care.** `id` tracks the explorer's catalogue order, which
> correlates with recency at the extremes (bucket 1 ≈ 2022, bucket 6 ≈ 2025) but is
> **not** an exact event timeline — a few 2021 events are interleaved with 2022 ones.
> Trends below are framed as *older cohort → recent cohort*, not precise dates. The
> AI-agent signal (near-zero early, dominant late) independently confirms the ordering
> is directionally right.

---

## 1. Thematic clusters — what people build

Fourteen coherent themes emerged. (Silhouette scores were low and flat across k —
expected for short, overlapping texts — so boundaries are soft and k was chosen for
interpretability.)

| # | Theme | Projects | Share |
|---|-------|---------:|------:|
| 5 | **NFTs, collectibles & creator marketplaces** | 1,112 | 13.6% |
| 3 | **AI agents & autonomous assistants** | 781 | 9.5% |
| 6 | **Crypto payments, wallets & off-ramps** | 779 | 9.5% |
| 1 | **DeFi lending, perps & collateral** | 713 | 8.7% |
| 0 | **On-chain trading tools & dev infrastructure** | 684 | 8.3% |
| 2 | **Creator & social-token platforms** | 672 | 8.2% |
| 8 | **Crowdfunding, donations & creator monetization** | 581 | 7.1% |
| 7 | **Decentralized storage & content sharing** | 538 | 6.6% |
| 13 | **ZK identity, privacy & verifiable reputation** | 531 | 6.5% |
| 10 | **Web3 social networks & web2 bridges** | 477 | 5.8% |
| 12 | **On-chain gaming & play-to-earn** | 431 | 5.3% |
| 9 | **DeFi portfolio & yield automation** | 321 | 3.9% |
| 11 | **Cross-chain atomic swaps (1inch Fusion+)** | 299 | 3.6% |
| 4 | **DAO tooling & governance** | 281 | 3.4% |

**Macro view.** Roughly a third of all projects are some flavour of **finance**
(DeFi lending + portfolio + payments + cross-chain swaps ≈ 26%, before counting
trading infra). A second pillar is **creator economy / social / NFT** (NFTs +
creator-tokens + crowdfunding + storage + web3-social ≈ 41% combined) — though, as
§2 shows, this pillar is overwhelmingly an *older-era* phenomenon. **AI agents** are
the third pillar and almost entirely a recent arrival.

---

## 2. Trends over time — the big rotation

Theme share by time bucket (oldest → newest), via the tech lexicon:

| Signal | b1 | b2 | b3 | b4 | b5 | b6 | Verdict |
|--------|---:|---:|---:|---:|---:|---:|---------|
| NFT / collectibles | 24.6 | 39.2 | 29.5 | 5.5 | 4.8 | 3.8 | **Collapsed** |
| AI / agents | 1.2 | 0.9 | 0.7 | 40.5 | 18.2 | 23.0 | **Exploded** |
| Stablecoins / payments | 3.7 | 2.8 | 4.9 | 6.0 | 10.1 | 14.4 | **Steady rise** |
| Identity / proof-of-human | 4.2 | 2.9 | 1.1 | 8.1 | 6.7 | 8.9 | Rising |
| Privacy | 6.1 | 2.6 | 2.0 | 7.3 | 5.8 | 8.5 | Resurgent |
| x402 / agentic payments | 0.0 | 0.0 | 0.0 | 0.1 | 0.9 | 3.5 | **Net-new** |
| Prediction / betting | 0.4 | 0.5 | 1.0 | 1.6 | 1.5 | 3.4 | Rising |
| Cross-chain / interop | 4.7 | 2.8 | 2.5 | 4.0 | 19.6 | 10.7 | Spiky (prize-driven) |
| Gaming / metaverse | 5.8 | 11.6 | 5.9 | 4.0 | 2.6 | 3.7 | Faded |
| DAO / governance | 6.7 | 10.2 | 3.8 | 3.4 | 1.3 | 2.1 | **Faded** |

Headlines:

- **NFTs → AI is the defining rotation.** NFTs were the single largest theme of the
  2021–22 era (peaking near 40% of a cohort) and have all but vanished from recent
  builds (~4%). AI agents traced the exact opposite arc, from ~1% to a fifth-plus of
  recent projects. The creator/social/DAO cluster of the last cycle faded with it.
- **Payments is the quiet structural winner** — no single spike, just a steady climb
  from ~3% to ~14%, suggesting durable conviction rather than hype. **x402 / agentic
  commerce** is the newest seedling: literally absent until the most recent cohort,
  where it already hits 3.5% (and dovetails with the AI-agent wave — agents that pay).
- **Privacy / ZK / identity dipped mid-corpus then rebounded** in recent cohorts —
  a maturing, not a fad.

**Caveat — themed hackathons distort the curve.** The two sharpest spikes are
**event artifacts**, not organic swings: the AI bucket-4 jump (40.5%) coincides with
*Agentic Ethereum* (a dedicated AI hackathon), and the cross-chain bucket-5 spike
(19.6%) with *Unite Defi* (1inch-sponsored — "1inch fusion" is the 6th-most-common
bigram). ETHGlobal's sponsor/prize themes visibly steer what gets built; read spikes
as "the ecosystem can be *directed*," and the smoother trends (payments, NFT decline)
as the more organic signal.

---

## 3. Tech & buzzwords

Most-mentioned technologies/primitives across the whole corpus:

| Share | Technology |
|------:|-----------|
| 19.8% | DeFi / trading |
| 17.9% | NFT / collectibles |
| 14.1% | AI / agents |
| 7.4% | Cross-chain / interop |
| 7.0% | Stablecoins / payments |
| 5.6% | Gaming / metaverse |
| 5.5% | Wallets |
| 5.4% | Privacy |
| 5.3% | Identity / proof-of-human |
| 4.6% | DAO / governance |
| 2.9% | ZK / zero-knowledge |

**Recurring phrasing** (top bigrams/trigrams): `real time`, `ai agent(s)`,
`smart contract(s)`, `1inch fusion`, `social media`, `nft marketplace`,
`zero knowledge proofs`, `lens protocol`, `cross / atomic swaps`, `privacy preserving`,
`real estate` (RWA), `uniswap v4 hook(s)`, `pyth price feeds`, `limit order protocol`.

**Marketing buzzwords** are surprisingly contained: `seamless/frictionless` (1.9%),
`trustless` (1.6%), `non-custodial`, `permissionless` and `composable` each ~1% or
less. Builders describe *what it does* far more than they reach for adjectives.

**Named ecosystems that recur** point to where sponsor gravity sits: **1inch** (Fusion+
cross-chain swaps), **Lens Protocol** (social), **Uniswap v4 hooks**, **Pyth** (oracles),
**Self.xyz / World ID** (identity), **Filecoin/IPFS** (storage).

---

## 4. Outliers & novelty

123 projects (~1.5%) sit far from every theme centroid. They split in two:

**Data-quality noise (real, and worth knowing).** A meaningful slice of the long tail —
and of the keyword lists for the infra/social/crowdfunding clusters — is **junk
submissions**: `TestData…TestData`, `test test test`, `tsete tstes`, `dummy dummy`,
`Solves Sudoku Solves Sudoku`, and blank rule-lines. These are placeholder/duplicate
hackathon entries, not products. Filter `is_outlier` (and watch for `test`/`dummy`
keywords) before any downstream modelling.

**Genuine novelty — the creative fringe.** Once noise is set aside, the outliers are
the most *idea-distinctive* projects, e.g.:

- **MyVote** — reducing the 550,000 rejected mail ballots via on-chain voting.
- **VanityFactory** — bounties for CREATE2 vanity contract addresses.
- **Guess-half-the-mean** — a classic game-theory experiment run on-chain.
- **TravelScript** — cross-border access to controlled medication.
- **SubKey** — granular per-contract permission delegation for keys.
- Plenty of pure whimsy: lost-sock subscription NFTs, "Armed Loogies," Eggie Planet,
  an eye-fatigue "ape into rest" app.

These won't form clusters by definition, but they're the leading indicator of where
the next theme might nucleate (much as lone AI experiments did before bucket 4).

---

## Methodology & reproducibility

- **Pipeline:** `analyze_descriptions.py` — load → chronology/time-buckets → NLP tables
  & tech lexicon → embed (cached to `.cache_embeddings.npy`) → KMeans (k swept 12–32,
  silhouette-selected, `random_state=42`) → outlier flag (bottom 1.5% by cosine-to-
  centroid) → c-TF-IDF keywords → outputs.
- **Outputs:** `cluster_summaries.json` (per-cluster keywords + representatives),
  `analysis_stats.json` (trends, n-grams, chronology), and
  **`ethglobal_projects_enriched.csv`** — every project tagged with `theme_label`,
  `cluster_keywords`, `tech_tags`, `time_bucket`, `event_rank`, `is_outlier`,
  `centroid_sim`. Theme names live in `cluster_labels.json` (edit + re-run to relabel;
  embeddings are cached so it's instant and deterministic).
- **Known limitations:** (1) `id` is a catalogue-order proxy, not exact dates — coarse
  trends only; (2) soft cluster boundaries (low silhouette) — themes overlap at the
  edges; (3) themed hackathons bias the mix; (4) ~1–2% junk submissions remain in the
  corpus (flagged, not deleted).

### Suggested next steps
- Scrape real event dates to replace the `id` proxy and get a true timeline.
- Split the two largest themes (NFTs, payments) at higher k for finer sub-themes.
- Cross-tabulate `theme_label` against `prizes` to see which themes actually *win*.
