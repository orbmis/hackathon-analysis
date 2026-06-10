#!/usr/bin/env python3
"""Step 3: split the two largest themes into finer sub-themes.

Reuses the cached sentence-transformer embeddings (row-aligned to the enriched
CSV) and runs a second, higher-resolution KMeans within each target theme.
Emits subcluster_summaries.json and, if subtheme_labels.json exists, writes a
`subtheme_label` column back into the enriched CSV.
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

CSV = "ethglobal_projects_enriched.csv"
EMB_CACHE = ".cache_embeddings.npy"
SUB_SUMMARIES = "subcluster_summaries.json"
SUB_LABELS = "subtheme_labels.json"

# theme cluster_id -> (short key, candidate sub-k range)
TARGETS = {5: ("nft", range(4, 9)), 6: ("pay", range(4, 9))}
RANDOM_STATE = 42
N_REP, N_KW = 6, 10

DOMAIN_STOP = {
    "blockchain", "decentralized", "decentralised", "platform", "users", "user",
    "app", "application", "web3", "web", "crypto", "using", "use", "based",
    "build", "built", "enables", "enable", "allows", "allow", "powered", "data",
    "onchain", "chain", "ethereum", "project", "solution", "system", "new",
    "easy", "simple", "first", "world", "way", "make", "making", "create",
    "nft", "nfts", "payment", "payments", "pay",  # the theme words themselves
}


def log(m):
    print(m, file=sys.stderr, flush=True)


def ctfidf(norm_texts, labels, k):
    docs = [" ".join(norm_texts[labels == c]) for c in range(k)]
    stop = sorted(set(CountVectorizer(stop_words="english").get_stop_words()) | DOMAIN_STOP)
    vec = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    M = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    out = []
    for c in range(k):
        row = M[c].toarray().ravel()
        top = row.argsort()[::-1][:N_KW]
        out.append([vocab[i] for i in top if row[i] > 0])
    return out


def sub_k(emb, rng):
    best_k, best_s = None, -1
    for k in rng:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(emb)
        s = silhouette_score(emb, km.labels_, random_state=RANDOM_STATE)
        log(f"      sub-k={k}: silhouette={s:.4f}")
        if s > best_s:
            best_k, best_s = k, s
    return best_k


def main():
    df = pd.read_csv(CSV)
    emb = np.load(EMB_CACHE)
    assert len(df) == len(emb), f"row mismatch {len(df)} vs {len(emb)}"

    all_summaries = {}
    sub_assign = pd.Series(index=df.index, dtype="object")  # "key:subid"

    for theme_id, (key, rng) in TARGETS.items():
        mask = (df["cluster_id"] == theme_id).values
        idx = np.where(mask)[0]
        theme_name = df.loc[mask, "theme_label"].iloc[0]
        sub_emb = emb[idx]
        norm = df.loc[mask, "description"].fillna("").str.lower().values
        log(f"\n  theme {theme_id} '{theme_name}' (n={len(idx)})")
        k = sub_k(sub_emb, rng)
        log(f"    chosen sub-k={k}")
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(sub_emb)
        labels = km.labels_
        cents = normalize(km.cluster_centers_)
        sims = np.einsum("ij,ij->i", sub_emb, cents[labels])
        kws = ctfidf(norm, labels, k)

        for i, sub in enumerate(labels):
            sub_assign.iloc[idx[i]] = f"{key}:{sub}"

        subs = []
        for c in range(k):
            sel = np.where(labels == c)[0]
            order = sel[np.argsort(sims[sel])[::-1]]
            reps = df.loc[mask, "description"].values[order][:N_REP]
            subs.append({
                "subcluster": f"{key}:{c}",
                "size": int(len(sel)),
                "share_of_theme": round(len(sel) / len(idx), 3),
                "keywords": kws[c],
                "representative_descriptions": [str(r) for r in reps],
            })
        subs.sort(key=lambda s: -s["size"])
        all_summaries[theme_name] = {"theme_id": theme_id, "size": int(len(idx)),
                                     "sub_k": int(k), "subclusters": subs}

    json.dump(all_summaries, open(SUB_SUMMARIES, "w"), indent=2, ensure_ascii=False)
    log(f"\n  wrote {SUB_SUMMARIES}")

    # Apply human sub-theme labels if available.
    df["subtheme_label"] = ""
    if os.path.exists(SUB_LABELS):
        lbl = json.load(open(SUB_LABELS))
        df["subtheme_label"] = sub_assign.map(lambda s: lbl.get(s, "") if isinstance(s, str) else "")
        df.to_csv(CSV, index=False)
        log(f"  applied {len(lbl)} sub-theme labels -> {CSV}")
    else:
        log("  (no subtheme_labels.json yet; summaries only)")


if __name__ == "__main__":
    main()
