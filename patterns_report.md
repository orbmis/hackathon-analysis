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

## 5. Sub-themes within the two largest clusters

Splitting the two biggest themes at higher resolution (`subcluster_themes.py`, sub-KMeans
on the same embeddings) reveals their internal structure. Sub-theme labels are in the
enriched CSV's `subtheme_label` column.

**NFTs, collectibles & creator marketplaces (1,112)** is not one thing — it's six:

| Sub-theme | Projects | Share |
|-----------|---------:|------:|
| NFT marketplaces & real-world utility | 262 | 24% |
| NFT-Fi: lending, collateral & fractionalization | 261 | 23% |
| Creator media & streaming (NFT memberships) | 207 | 19% |
| NFT gaming & collectible cards | 145 | 13% |
| Generative & collaborative art NFTs | 124 | 11% |
| Minting tools & launchpads | 113 | 10% |

The notable find: ~23% of "NFT" projects are actually **NFT-Fi** (using NFTs as
financial collateral — lending, renting, fractionalizing), i.e. closer to DeFi than to
art. Pure art NFTs are only ~11%.

**Crypto payments, wallets & off-ramps (779)** splits cleanly into four:

| Sub-theme | Projects | Share |
|-----------|---------:|------:|
| Stablecoin payments, payroll & subscriptions (PYUSD) | 222 | 28% |
| Wallets (smart / hardware / privacy) | 212 | 27% |
| P2P transfers, payment links & tipping | 192 | 25% |
| Neobank, savings & everyday-finance apps | 153 | 20% |

PYUSD (PayPal's stablecoin) is a recurring anchor in the largest sub-theme — another
case of sponsor gravity shaping what gets built.

---

## 6. Which themes actually win prizes

`prize_count > 0` (project won ≥ 1 sponsor prize) is a win proxy. **Overall win-rate is
39.7%** — ETHGlobal hands out many sponsor prizes, so winning *something* is common.

**The raw cross-tab is a trap — it's dominated by an era confound.** Win-rate by cohort
falls from ~61% in the oldest buckets to ~22% in the newest (older events list prizes far
more completely / had higher prize-to-project ratios). So a naive ranking just surfaces
*old* themes (NFTs, DAOs, social) as "winners." The honest metric is **era-adjusted lift**:
a theme's win-rate vs. the baseline of *its own* time cohorts.

| Theme | n | Win % | Era-adj. lift | Read |
|-------|--:|------:|:-------------:|------|
| **AI agents & autonomous assistants** | 781 | 41.0 | **1.19×** | Genuinely over-performs |
| Crowdfunding & creator monetization | 581 | 43.4 | 1.07× | Slight edge |
| ZK identity, privacy & reputation | 531 | 39.0 | 1.05× | Slight edge |
| Web3 social & web2 bridges | 477 | 51.2 | 1.04× | ~Average (era-inflated raw) |
| NFTs & creator marketplaces | 1,112 | 48.7 | 1.03× | ~Average (era-inflated raw) |
| On-chain gaming | 431 | 38.3 | 1.00× | Average |
| Crypto payments & wallets | 779 | 35.3 | 0.98× | Average |
| DeFi lending & perps | 713 | 32.8 | 0.98× | Average |
| DAO tooling & governance | 281 | 50.9 | 0.97× | ~Average (era-inflated raw) |
| On-chain trading infra | 684 | 32.6 | 0.93× | Slight drag |
| **DeFi portfolio & yield automation** | 321 | 27.1 | **0.82×** | Saturated / under-performs |
| **Cross-chain atomic swaps (1inch)** | 299 | 18.1 | **0.63×** | Heavily under-performs |

Headlines:

- **AI agents are the only clear over-performer (1.19×)** even after era adjustment —
  driven by concentrated sponsor demand. Coinbase Developer Platform alone accounts for
  **181 of the prizes** won by agent projects; sponsors actively bought the agent wave.
- **The NFT/DAO/social "wins" evaporate once era-adjusted** — they were high only because
  they're old-era themes, when prizes were plentiful. On a level field they're ~average.
- **Cross-chain swaps are the worst bet (0.63×)** — a textbook saturation story: the
  1inch-sponsored *Unite Defi* flood meant hundreds of near-identical Fusion+ swap clones
  chasing a handful of 1inch prizes (36 of them). DeFi yield automation (0.82×) is the
  next-most-crowded-yet-thin field.
- **Takeaway for a builder:** novelty with a hungry sponsor (agents) beats piling into a
  single-sponsor bounty everyone else also targeted (Fusion+ swaps).

> Caveat: era adjustment controls for cohort prize density but not for sponsor mix or
> the explorer's data completeness; treat lifts as directional, not precise.

---

## 7. Why AI agents over-perform — decomposing the 1.19× lift

The agent advantage is real but **not** broad organic quality. Decomposed three ways
(`agent_deepdive.py`), it resolves into two coupled artifacts: a dedicated prize-rich
hackathon and a single mega-sponsor.

**By sub-type — broad, with one exception.** Sub-clustering the 781 agent projects gives
six sub-types; almost all over-perform, so no single niche carries the lift:

| Agent sub-type | n | Win % | Era-adj. lift |
|----------------|--:|------:|:-------------:|
| Agent swarms, marketplaces & business-ops | 142 | 45.1 | **1.30×** |
| On-chain copilots, auditing & security | 121 | 43.0 | 1.22× |
| Trading / portfolio / hedge-fund agents | 115 | 42.6 | 1.20× |
| Consumer & creator agents (NPCs, art, fitness) | 189 | 42.3 | 1.19× |
| Agent marketplaces w/ payments, TEE, inference | 138 | 34.8 | 1.13× |
| Telegram / Discord trading bots | 76 | 35.5 | **1.00×** |

The only sub-type with *no* edge is plain **chat bots** (Telegram/Discord) — a commoditized
wrapper that judges don't reward. "Infrastructure-flavoured" agents (swarms, copilots) win most.

**By sponsor — this is the real engine.** Agent projects won 380 sponsor-prizes, but they
are extraordinarily concentrated:

- **Coinbase Developer Platform alone = 47.6%** of all agent prizes (181 of 380); top-5
  sponsors = 63.7%.
- For comparison, the **corpus's most-concentrated sponsor is just 8.4%** (Polygon). Agent
  prizes are ~6× more single-sponsor-dependent than the average theme.
- CDP (AgentKit) effectively *bankrolled the category*. The lift is, to a first
  approximation, a Coinbase-funded phenomenon.

**By event — it lives in one hackathon.** The over-performance is overwhelmingly inside
**Agentic Ethereum** (a dedicated, prize-rich agent hackathon): 307 agent projects, 61.6%
win-rate vs a 43.2% cohort baseline (**1.43×**). Strip that event out and in ordinary recent
general events agents actually *under*-perform — **ETHOnline 2025 (0.54×)** and **New Delhi
(0.43×)** — because by then the category was crowded and the earmarked money was gone.
(A few later events still show residual agent demand — Buenos Aires 1.68×, NY 1.51× — but on
small, noisy samples.)

**Conclusion.** "Agents win" really means *"agents won where and when the money was earmarked
for them"* — a themed track (Agentic Ethereum) plus a mega-sponsor (Coinbase). The sharpened
builder takeaway: **follow earmarked sponsor capital, not the buzzword.** By the time a hot
category reaches general events, its edge has already been competed away (exactly what
happened to agents at ETHOnline 2025 / New Delhi, and to Fusion+ swaps in §6).

---

## Methodology & reproducibility

- **Pipeline:** `analyze_descriptions.py` — load → chronology/time-buckets → NLP tables
  & tech lexicon → embed (cached to `.cache_embeddings.npy`) → KMeans (k swept 12–32,
  silhouette-selected, `random_state=42`) → outlier flag (bottom 1.5% by cosine-to-
  centroid) → c-TF-IDF keywords → outputs.
- **Sub-themes (§5):** `subcluster_themes.py` — sub-KMeans within the two largest themes
  using the cached embeddings; writes `subcluster_summaries.json` and the `subtheme_label`
  column. Sub-theme names live in `subtheme_labels.json` (edit + re-run to relabel).
- **Prizes (§6):** computed from the `prizes` / `prize_count` columns, era-adjusted against
  per-`time_bucket` baselines.
- **Agent deep-dive (§7):** `agent_deepdive.py` — sub-clusters the agent theme and decomposes
  its prize lift by sub-type, sponsor, and event; writes `agent_subclusters.json`.
- **Outputs:** `cluster_summaries.json` (per-cluster keywords + representatives),
  `analysis_stats.json` (trends, n-grams, chronology), `subcluster_summaries.json`, and
  **`ethglobal_projects_enriched.csv`** — every project tagged with `theme_label`,
  `subtheme_label`, `cluster_keywords`, `tech_tags`, `time_bucket`, `event_rank`,
  `is_outlier`, `centroid_sim`. Theme names live in `cluster_labels.json` (edit + re-run to
  relabel; embeddings are cached so it's instant and deterministic).
- **Known limitations:** (1) `id` is a catalogue-order proxy, not exact dates — coarse
  trends only; (2) soft cluster boundaries (low silhouette) — themes overlap at the
  edges; (3) themed hackathons bias the mix; (4) ~1–2% junk submissions remain in the
  corpus (flagged, not deleted).

### Suggested next steps
- Scrape real event dates to replace the `id` proxy and get a true timeline.
- ~~Split the two largest themes at higher k for finer sub-themes~~ — done (§5).
- ~~Cross-tabulate `theme_label` against `prizes`~~ — done (§6).
- ~~Drill into the AI-agent over-performance~~ — done (§7): it's Coinbase + Agentic Ethereum.
- Generalize §7: profile each major sponsor's "earmarked" theme and measure how fast each
  category's edge decays once it hits general events.
