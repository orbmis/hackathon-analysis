#!/usr/bin/env python3
"""Emergent-pattern analysis of ETHGlobal project descriptions.

Pipeline:
  Layer 0  load + event chronology (id is a recency proxy) + time buckets
  Layer 1  deterministic NLP: n-grams, TF-IDF, tech/buzzword lexicon (+ trends)
  Layer 2  embed (all-MiniLM-L6-v2) -> KMeans (silhouette-chosen k) -> outliers
           -> per-cluster c-TF-IDF keywords + representative descriptions
  Layer 4  write cluster_summaries.json, analysis_stats.json, enriched CSV

Outputs feed Claude's inline labelling: drop a cluster_labels.json mapping
{cluster_id: {"label","gloss"}} next to this script and re-run — embeddings are
cached so the relabel pass is instant and cluster ids stay stable.
"""

import json
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

CSV_IN = "ethglobal_projects.csv"
CSV_OUT = "ethglobal_projects_enriched.csv"
CLUSTER_SUMMARIES = "cluster_summaries.json"
ANALYSIS_STATS = "analysis_stats.json"
EMB_CACHE = ".cache_embeddings.npy"
LABELS_FILE = "cluster_labels.json"

N_BUCKETS = 6
K_RANGE = list(range(12, 34, 2))   # candidate cluster counts
RANDOM_STATE = 42
N_REP = 8                          # representative descriptions per cluster
N_KEYWORDS = 12                    # c-TF-IDF keywords per cluster

# Domain filler words that are true but uninformative for theme-finding. Kept
# OUT of n-gram/keyword tables but reported separately so nothing is hidden.
DOMAIN_STOP = {
    "blockchain", "decentralized", "decentralised", "platform", "users", "user",
    "app", "application", "web3", "web", "crypto", "using", "use", "based",
    "build", "built", "enables", "enable", "allows", "allow", "powered", "data",
    "onchain", "chain", "ethereum", "project", "solution", "system", "new",
    "easy", "simple", "first", "world", "way", "make", "making", "create",
}

# Tech / buzzword lexicon: canonical tag -> regex (matched on lowercased text).
TECH_LEXICON = {
    "ZK / zero-knowledge": r"\bzk\b|zero[- ]knowledge|zk-?(?:proof|snark|stark|rollup|ml|tls|email)|zkp\b",
    "AI / agents": r"\b(?:ai|llm|gpt|agent|agentic|autonomous agent|chatbot|machine learning|ml model|rag)\b",
    "Account abstraction": r"account abstraction|\berc-?4337\b|\baa wallet|smart account|gasless|paymaster|session key",
    "x402 / agentic payments": r"\bx402\b|agentic (?:commerce|payment)|pay-?per-?use",
    "DeFi / trading": r"\bdefi\b|\bdex\b|amm|liquidity|yield|lending|borrow|staking|perpetual|perps?\b|swap|trading",
    "Uniswap hooks": r"uniswap|\bv4 hook|\bhook(?:s)?\b",
    "Rollups / L2 / scaling": r"\brollup|layer ?2|\bl2\b|optimistic|validium|scaling|appchain",
    "Oracles": r"\boracle(?:s)?\b|chainlink|price feed",
    "NFT / collectibles": r"\bnft(?:s)?\b|non-?fungible|collectible|erc-?721|erc-?1155",
    "DAO / governance": r"\bdao\b|governance|voting|quadratic",
    "Identity / proof-of-human": r"\bidentity\b|proof of (?:human|person)|sybil|worldcoin|world id|self.protocol|kyc|verif(?:y|ied|ication)",
    "Privacy": r"\bprivacy\b|private|confidential|encrypt|fhe|homomorphic|anonym",
    "Stablecoins / payments": r"stablecoin|\busdc\b|\busdt\b|payment|remittance|payroll|invoice|payout",
    "RWA / tokenization": r"\brwa\b|real[- ]world asset|tokeniz|tokenis",
    "Cross-chain / interop": r"cross[- ]chain|interoperab|bridge|omnichain|multichain|multi-?chain|ccip|layerzero",
    "Wallets": r"\bwallet(?:s)?\b|seed phrase|self-?custod|non-?custodial",
    "MEV": r"\bmev\b|front-?run|maximal extractable",
    "TEE / verifiable compute": r"\btee\b|trusted execution|verifiable comput|attestation",
    "Restaking / EigenLayer": r"restak|eigenlayer|\bavs\b",
    "Prediction / betting": r"prediction market|betting|wager|forecast",
    "Gaming / metaverse": r"\bgam(?:e|ing|efi)\b|metaverse|\bp2e\b|play-?to-?earn",
    "Social / SocialFi": r"socialfi|social (?:network|media|graph)|farcaster|lens protocol",
    "Buzz: trustless": r"trustless",
    "Buzz: permissionless": r"permissionless",
    "Buzz: non-custodial": r"non-?custodial|self-?custod",
    "Buzz: composable": r"composab",
    "Buzz: seamless/frictionless": r"seamless|frictionless",
}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def load_data():
    df = pd.read_csv(CSV_IN, dtype={"id": int})
    df["description"] = df["description"].fillna("").astype(str)
    df["norm"] = df["description"].str.lower()
    # Chronology: higher id == more recent. event_rank 1 == oldest event.
    ev_order = df.groupby("event")["id"].median().sort_values()
    rank = {ev: i + 1 for i, ev in enumerate(ev_order.index)}
    df["event_rank"] = df["event"].map(rank)
    # Equal-count chronological buckets by id (bucket 1 = oldest).
    df["time_bucket"] = pd.qcut(df["id"], N_BUCKETS, labels=range(1, N_BUCKETS + 1)).astype(int)
    return df


def tech_tags(df):
    """Match the lexicon against each description; return per-row tags + stats."""
    compiled = {tag: re.compile(pat) for tag, pat in TECH_LEXICON.items()}
    row_tags = []
    for txt in df["norm"]:
        row_tags.append([tag for tag, rx in compiled.items() if rx.search(txt)])
    df["tech_tags"] = ["; ".join(t) for t in row_tags]

    n = len(df)
    overall = Counter(t for tags in row_tags for t in tags)
    # share within each time bucket
    by_bucket = {}
    for b in range(1, N_BUCKETS + 1):
        idx = df.index[df["time_bucket"] == b]
        cnt = Counter(t for i in idx for t in row_tags[df.index.get_loc(i)])
        by_bucket[b] = {tag: round(cnt[tag] / max(len(idx), 1), 4) for tag in TECH_LEXICON}
    stats = {
        "overall_counts": dict(overall.most_common()),
        "overall_share": {t: round(c / n, 4) for t, c in overall.most_common()},
        "share_by_bucket": by_bucket,
    }
    return stats


def ngram_tables(df):
    stop = sorted(set(CountVectorizer(stop_words="english").get_stop_words()) | DOMAIN_STOP)
    out = {}
    for label, rng in [("unigrams", (1, 1)), ("bigrams", (2, 2)), ("trigrams", (3, 3))]:
        vec = CountVectorizer(stop_words=stop, ngram_range=rng, min_df=5)
        X = vec.fit_transform(df["norm"])
        freqs = np.asarray(X.sum(axis=0)).ravel()
        vocab = np.array(vec.get_feature_names_out())
        top = freqs.argsort()[::-1][:40]
        out[label] = [[vocab[i], int(freqs[i])] for i in top]
    return out


def embed(df):
    if EMB_CACHE and __import__("os").path.exists(EMB_CACHE):
        emb = np.load(EMB_CACHE)
        if emb.shape[0] == len(df):
            log(f"  loaded cached embeddings {emb.shape}")
            return emb
    from sentence_transformers import SentenceTransformer
    log("  embedding descriptions (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode(df["description"].tolist(), batch_size=128,
                        show_progress_bar=False, normalize_embeddings=True)
    emb = np.asarray(emb, dtype=np.float32)
    np.save(EMB_CACHE, emb)
    return emb


def choose_k(emb):
    best_k, best_s, scores = None, -1, {}
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(emb)
        s = silhouette_score(emb, km.labels_, sample_size=2500, random_state=RANDOM_STATE)
        scores[k] = round(float(s), 4)
        log(f"    k={k}: silhouette={s:.4f}")
        if s > best_s:
            best_k, best_s = k, s
    return best_k, scores


def cluster_keywords(df, labels, k):
    """c-TF-IDF: treat each cluster's concatenated text as one document."""
    docs = []
    for c in range(k):
        docs.append(" ".join(df["norm"].values[labels == c]))
    stop = sorted(set(CountVectorizer(stop_words="english").get_stop_words()) | DOMAIN_STOP)
    vec = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    M = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    kws = []
    for c in range(k):
        row = M[c].toarray().ravel()
        top = row.argsort()[::-1][:N_KEYWORDS]
        kws.append([vocab[i] for i in top if row[i] > 0])
    return kws


def main():
    log("Layer 0: loading data + chronology...")
    df = load_data()
    log(f"  {len(df)} rows, {df['event'].nunique()} events, {N_BUCKETS} time buckets")

    log("Layer 1: deterministic NLP...")
    tech = tech_tags(df)
    ngrams = ngram_tables(df)

    log("Layer 2: embeddings + clustering...")
    emb = embed(df)
    k, sil_scores = choose_k(emb)
    log(f"  chosen k={k}")
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(emb)
    labels = km.labels_
    df["cluster_id"] = labels

    # Outliers: cosine similarity to own (normalised) centroid; bottom ~1.5%.
    centroids = normalize(km.cluster_centers_)
    sims = np.einsum("ij,ij->i", emb, centroids[labels])
    thresh = np.quantile(sims, 0.015)
    df["centroid_sim"] = sims.round(4)
    df["is_outlier"] = sims <= thresh

    kws = cluster_keywords(df, labels, k)
    df["cluster_keywords"] = ["; ".join(kws[c]) for c in labels]

    # Representative descriptions: highest similarity to centroid within cluster.
    summaries = []
    for c in range(k):
        idx = np.where(labels == c)[0]
        order = idx[np.argsort(sims[idx])[::-1]]
        reps = df["description"].values[order][:N_REP]
        size_by_bucket = (df.loc[labels == c, "time_bucket"]
                          .value_counts().reindex(range(1, N_BUCKETS + 1), fill_value=0)
                          .astype(int).tolist())
        summaries.append({
            "cluster_id": int(c),
            "size": int(len(idx)),
            "share": round(len(idx) / len(df), 4),
            "keywords": kws[c],
            "size_by_time_bucket": size_by_bucket,
            "representative_descriptions": [str(r) for r in reps],
        })
    summaries.sort(key=lambda s: -s["size"])

    # Optional: apply human labels if present.
    labelmap = {}
    import os
    if os.path.exists(LABELS_FILE):
        labelmap = {int(k_): v for k_, v in json.load(open(LABELS_FILE)).items()}
        log(f"  applied {len(labelmap)} human labels from {LABELS_FILE}")
    df["theme_label"] = df["cluster_id"].map(
        lambda c: labelmap.get(c, {}).get("label", f"cluster_{c}"))
    for s in summaries:
        s["theme_label"] = labelmap.get(s["cluster_id"], {}).get("label", f"cluster_{s['cluster_id']}")
        s["gloss"] = labelmap.get(s["cluster_id"], {}).get("gloss", "")

    # Event chronology table.
    ev = (df.groupby("event")
            .agg(count=("id", "size"), median_id=("id", "median"),
                 event_rank=("event_rank", "first"))
            .sort_values("event_rank").reset_index())
    event_chrono = ev.to_dict(orient="records")
    bucket_info = {}
    for b in range(1, N_BUCKETS + 1):
        sub = df[df["time_bucket"] == b]
        top_ev = sub["event"].value_counts().head(4).index.tolist()
        bucket_info[b] = {"count": int(len(sub)),
                          "id_range": [int(sub["id"].min()), int(sub["id"].max())],
                          "top_events": top_ev}

    # Write outputs.
    json.dump(summaries, open(CLUSTER_SUMMARIES, "w"), indent=2, ensure_ascii=False)
    json.dump({
        "n_rows": int(len(df)), "k": int(k), "silhouette_by_k": sil_scores,
        "time_buckets": bucket_info, "event_chronology": event_chrono,
        "tech": tech, "ngrams": ngrams,
        "n_outliers": int(df["is_outlier"].sum()),
    }, open(ANALYSIS_STATS, "w"), indent=2, ensure_ascii=False, default=str)

    cols = ["id", "title", "description", "url", "event", "prizes", "prize_count",
            "event_rank", "time_bucket", "cluster_id", "theme_label",
            "cluster_keywords", "tech_tags", "centroid_sim", "is_outlier"]
    df[cols].to_csv(CSV_OUT, index=False)

    log(f"\nDone. k={k}, {df['is_outlier'].sum()} outliers.")
    log(f"  wrote {CLUSTER_SUMMARIES}, {ANALYSIS_STATS}, {CSV_OUT}")


if __name__ == "__main__":
    main()
