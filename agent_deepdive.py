#!/usr/bin/env python3
"""Why do AI-agent projects over-perform on prizes (1.19x era-adjusted)?

Decomposes the lift three ways: by agent sub-type, by sponsor, and by event/era.
Reuses cached embeddings; emits agent_subclusters.json and prints the breakdowns.
"""

import json
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

CSV = "ethglobal_projects_enriched.csv"
EMB = ".cache_embeddings.npy"
AGENT_CLUSTER = 3
RANDOM_STATE = 42
SUB_LABELS = {  # filled after first inspection; key "ag:N"
}

STOP_EXTRA = {"ai", "agent", "agents", "agentic", "autonomous", "powered", "using",
              "platform", "based", "web3", "blockchain", "decentralized", "users",
              "user", "data", "onchain", "smart", "build", "real", "time"}
# Prize names that are ETHGlobal-level awards, not sponsors.
NON_SPONSOR = {"Finalist", "???"}


def ctfidf(texts, labels, k):
    docs = [" ".join(texts[labels == c]) for c in range(k)]
    stop = sorted(set(CountVectorizer(stop_words="english").get_stop_words()) | STOP_EXTRA)
    vec = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    M = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    return [[vocab[i] for i in M[c].toarray().ravel().argsort()[::-1][:10]
             if M[c].toarray().ravel()[i] > 0] for c in range(k)]


def main():
    df = pd.read_csv(CSV)
    df["won"] = df["prize_count"] > 0
    emb = np.load(EMB)
    bucket_base = df.groupby("time_bucket")["won"].mean()  # era baseline

    mask = (df["cluster_id"] == AGENT_CLUSTER).values
    idx = np.where(mask)[0]
    sub = df[mask].copy()
    print(f"AI agents: n={len(sub)}, win-rate {sub['won'].mean()*100:.1f}% "
          f"(corpus {df['won'].mean()*100:.1f}%)\n")

    # --- 1. sub-types ---
    aemb = emb[idx]
    best_k, best_s = None, -1
    for k in range(4, 8):
        km = KMeans(k, random_state=RANDOM_STATE, n_init=10).fit(aemb)
        s = silhouette_score(aemb, km.labels_, random_state=RANDOM_STATE)
        if s > best_s:
            best_k, best_s = k, s
    km = KMeans(best_k, random_state=RANDOM_STATE, n_init=10).fit(aemb)
    labels = km.labels_
    texts = sub["description"].fillna("").str.lower().values
    kws = ctfidf(texts, labels, best_k)
    sims = np.einsum("ij,ij->i", aemb, normalize(km.cluster_centers_)[labels])
    sub["ag"] = labels

    print(f"=== 1. AGENT SUB-TYPES (sub_k={best_k}) — era-adjusted ===")
    summ = []
    rows = []
    for c in range(best_k):
        sel = sub[sub["ag"] == c]
        exp = sel["time_bucket"].map(bucket_base).mean()
        lift = sel["won"].mean() / exp
        order = np.argsort(sims[labels == c])[::-1]
        reps = sel["description"].values[order][:4]
        rows.append((len(sel), sel["won"].mean(), lift, c, kws[c]))
        summ.append({"sub": f"ag:{c}", "n": int(len(sel)),
                     "win_rate": round(float(sel["won"].mean()), 3),
                     "era_adj_lift": round(float(lift), 2),
                     "keywords": kws[c],
                     "reps": [str(r) for r in reps]})
    for n, wr, lift, c, kw in sorted(rows, key=lambda r: -r[2]):
        print(f"  ag:{c} n={n:>3} win={wr*100:4.1f}% lift={lift:.2f}x | {', '.join(kw[:7])}")
        for s in summ:
            if s["sub"] == f"ag:{c}":
                print(f"        · {s['reps'][0][:88]}")
    json.dump(summ, open("agent_subclusters.json", "w"), indent=2, ensure_ascii=False)

    # --- 2. sponsors ---
    print("\n=== 2. SPONSORS backing agent winners ===")
    c = Counter()
    for p in sub["prizes"].dropna():
        for nm in str(p).split("; "):
            nm = nm.strip()
            if nm and nm not in NON_SPONSOR:
                c[nm] += 1
    total = sum(c.values())
    print(f"  {total} sponsor-prizes across agent projects, {len(c)} distinct sponsors")
    for nm, n in c.most_common(12):
        print(f"    {n:>3} ({n/total*100:4.1f}%)  {nm}")
    top5 = sum(n for _, n in c.most_common(5))
    print(f"  top-1 share {c.most_common(1)[0][1]/total*100:.1f}% | top-5 share {top5/total*100:.1f}%")
    # corpus-wide comparison
    cc = Counter()
    for p in df["prizes"].dropna():
        for nm in str(p).split("; "):
            nm = nm.strip()
            if nm and nm not in NON_SPONSOR:
                cc[nm] += 1
    ctot = sum(cc.values())
    print(f"  (corpus top-1 share {cc.most_common(1)[0][1]/ctot*100:.1f}% — "
          f"{cc.most_common(1)[0][0]})")

    # --- 3. event / era ---
    print("\n=== 3. WHERE the lift lives (by event, agent projects only) ===")
    ev = (sub.groupby("event")
            .agg(n=("id", "size"), win=("won", "mean"),
                 base=("time_bucket", lambda s: bucket_base[s].mean()))
            .query("n >= 15"))
    ev["lift"] = ev["win"] / ev["base"]
    for e, r in ev.sort_values("n", ascending=False).head(10).iterrows():
        print(f"  {e[:32]:<32} n={int(r.n):>3} win={r.win*100:4.1f}% "
              f"base={r.base*100:4.1f}% lift={r.lift:.2f}x")


if __name__ == "__main__":
    main()
