#!/usr/bin/env python3
"""
analyze_and_recommend.py
- tracks_dump.csv 를 로드하여 추천 알고리즘을 적용합니다.
- 추천 방식:
  1) seed_tracks 기반: 사용자가 좋아하는 샘플 트랙 3~5곡을 주면 그 트랙들의 오디오 피처 평균을 선호도 벡터로 사용.
  2) 직접 가중치: danceability, energy, valence, tempo 등 피처별 가중치를 사용해 목표 벡터 생성.
- 점수 = cosine_similarity(features, target) * w_sim + popularity_norm * w_pop + recency_norm * w_time

사용 예시:
python analyze_and_recommend.py --in outputs/tracks_dump.csv --mode seed --seed_ids "3n3Ppam7vgaVa1iaRUc9Lp,6rqhFgbbKwnb9MLmUQDhG6" --topn 20 --out outputs/recommendations_top20.csv
"""

import argparse
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# 1. Load Data
# ---------------------------
def load_data(csv_file: str) -> pd.DataFrame:
    return pd.read_csv(csv_file)


# ---------------------------
# 2. Feature Engineering
# ---------------------------
FEATURE_COLS = [
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo"
]

def build_feature_matrix(df: pd.DataFrame):
    feats = df[FEATURE_COLS].fillna(0)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(feats)
    return df, Xs, scaler


# ---------------------------
# 3. Popularity & Recency
# ---------------------------
def compute_popularity_norm(df: pd.DataFrame):
    if "popularity" in df.columns:
        vals = pd.to_numeric(df["popularity"], errors="coerce").fillna(0).values
        return (vals - vals.min()) / (vals.max() - vals.min() + 1e-6)
    return np.zeros(len(df))

def compute_recency_score(df: pd.DataFrame):
    if "release_date" in df.columns:
        try:
            dates = pd.to_datetime(df["release_date"], errors="coerce")
            ords = dates.map(pd.Timestamp.toordinal).fillna(0).values
            return (ords - ords.min()) / (ords.max() - ords.min() + 1e-6)
        except Exception:
            return np.zeros(len(df))
    return np.zeros(len(df))


# ---------------------------
# 4. Preference Vector
# ---------------------------
def preference_vector_from_seeds(df, Xs, seed_ids):
    mask = df["id"].isin(seed_ids)
    if not mask.any():
        raise ValueError("No seed tracks found in dataset.")
    return Xs[mask].mean(axis=0)

def preference_vector_from_weights(df, scaler, weights: dict):
    vec = np.zeros(len(FEATURE_COLS))
    for i, col in enumerate(FEATURE_COLS):
        if col in weights:
            vec[i] = weights[col]
    # 표준화된 피처 공간에 맞게 transform
    return scaler.transform([vec])[0]


# ---------------------------
# 5. Recommendation
# ---------------------------
def recommend(df, Xs, target_vec, topn=20, w_sim=0.7, w_pop=0.2, w_time=0.1,
              min_popularity=0, exclude_explicit=False):

    sims = cosine_similarity(Xs, target_vec.reshape(1, -1)).flatten()
    pop_norm = compute_popularity_norm(df)
    time_norm = compute_recency_score(df)

    score = w_sim * sims + w_pop * pop_norm + w_time * time_norm

    # 필터링
    mask = np.ones(len(df), dtype=bool)
    if exclude_explicit and "explicit" in df.columns:
        mask &= ~df["explicit"].astype(bool).values
    if min_popularity and "popularity" in df.columns:
        mask &= pd.to_numeric(df["popularity"], errors="coerce").fillna(0).values >= min_popularity

    candidates = df[mask].copy().reset_index(drop=True)
    candidate_scores = score[mask]
    candidates["score"] = candidate_scores

    return candidates.sort_values("score", ascending=False).head(topn)


# ---------------------------
# 6. Save Results
# ---------------------------
def save_results(top_df: pd.DataFrame, out_csv: str, out_html: str = None):
    top_df.to_csv(out_csv, index=False)
    print(f"Saved top recommendations to {out_csv}")

    if out_html:
        rows_html = ""
        for _, r in top_df.iterrows():
            rows_html += (
                f"<tr><td><a href='{r.get('track_url','')}'>{r.get('track_name','')}</a></td>"
                f"<td>{r.get('artists','')}</td><td>{int(r.get('popularity',0))}</td>"
                f"<td>{round(r.get('score',0),3)}</td></tr>\n"
            )
        html = f"""
        <html>
        <head>
        <meta charset='utf-8'/>
        <title>Recommendations Top {len(top_df)}</title>
        <style>
        body{{font-family: Arial, sans-serif; padding: 20px}}
        table{{border-collapse: collapse; width: 100%}}
        th, td{{border: 1px solid #ddd; padding: 8px}}
        th{{background: #f4f4f4}}
        </style>
        </head>
        <body>
        <h2>Top {len(top_df)} Recommendations</h2>
        <table>
        <thead><tr><th>Track</th><th>Artists</th><th>Popularity</th><th>Score</th></tr></thead>
        <tbody>
        {rows_html}
        </tbody>
        </table>
        </body>
        </html>
        """
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved HTML summary to {out_html}")


# ---------------------------
# 7. Utils
# ---------------------------
def parse_weights_arg(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        out = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                out[k.strip()] = float(v.strip())
        return out


# ---------------------------
# 8. Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_csv", required=True)
    parser.add_argument("--mode", choices=["seed", "weights"], required=True)
    parser.add_argument("--seed_ids", help="comma separated seed track ids")
    parser.add_argument("--weights", help="json or k=v pairs for feature weights")
    parser.add_argument("--topn", type=int, default=20)
    parser.add_argument("--out", default="outputs/recommendations_top20.csv")
    parser.add_argument("--out_html", default="outputs/recommendations_summary.html")
    parser.add_argument("--w_sim", type=float, default=0.7)
    parser.add_argument("--w_pop", type=float, default=0.2)
    parser.add_argument("--w_time", type=float, default=0.1)
    parser.add_argument("--min_popularity", type=int, default=0)
    parser.add_argument("--exclude_explicit", action="store_true")
    args = parser.parse_args()

    df = load_data(args.input_csv)
    fdf, Xs, scaler = build_feature_matrix(df)

    if args.mode == "seed":
        if not args.seed_ids:
            raise SystemExit("seed mode requires --seed_ids")
        seed_ids = [s.strip() for s in args.seed_ids.split(",") if s.strip()]
        target = preference_vector_from_seeds(fdf, Xs, seed_ids)
    else:
        if not args.weights:
            raise SystemExit("weights mode requires --weights")
        weights = parse_weights_arg(args.weights)
        target = preference_vector_from_weights(fdf, scaler, weights)

    top = recommend(
        fdf, Xs, target,
        topn=args.topn,
        w_sim=args.w_sim, w_pop=args.w_pop, w_time=args.w_time,
        min_popularity=args.min_popularity,
        exclude_explicit=args.exclude_explicit
    )

    save_results(top, args.out, args.out_html)


if __name__ == "__main__":
    main()
