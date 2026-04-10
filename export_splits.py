import os
import json
import random
import argparse
from typing import List, Tuple, Dict, Optional

import mysql.connector
import pandas as pd


def connect():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "db_26_1"),
    )


def fetchall_dict(cur) -> List[Dict]:
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def table_columns(cur, table: str) -> List[str]:
    cur.execute(f"SHOW COLUMNS FROM `{table}`;")
    return [r[0] for r in cur.fetchall()]


def find_candidate_tables(cur) -> Dict[str, List[str]]:
    """
    Heuristics: look for tables likely to contain SOC code + title text.
    O*NET MySQL dumps often include tables like: occupation_data, alternate_titles, etc.
    We also use INFORMATION_SCHEMA to find columns that look like SOC and title.
    """
    cur.execute("SHOW TABLES;")
    tables = [r[0] for r in cur.fetchall()]

    candidates = {}
    for t in tables:
        cols = table_columns(cur, t)
        lc = [c.lower() for c in cols]
        has_soc = any("onetsoc" in c or ("soc" in c and "code" in c) for c in lc)
        has_titleish = any("title" in c or "name" in c for c in lc)
        if has_soc and has_titleish:
            candidates[t] = cols
    return candidates


def pick_col(cols: List[str], patterns: List[str]) -> Optional[str]:
    lc = [c.lower() for c in cols]
    for p in patterns:
        for i, c in enumerate(lc):
            if p in c:
                return cols[i]
    return None


def build_title_dataset(conn, max_rows_per_table: Optional[int] = None) -> pd.DataFrame:
    """
    Builds a dataset with columns:
      - text (job title / alternate title)
      - onetsoc_code
      - source_table
      - source_col
    """
    cur = conn.cursor()
    candidates = find_candidate_tables(cur)

    if not candidates:
        raise RuntimeError(
            "Could not auto-detect any tables with SOC code + title-like fields.\n"
            "Next step: run SHOW TABLES; and paste the output here."
        )

    rows: List[Dict] = []

    for table, cols in candidates.items():
        soc_col = pick_col(cols, ["onetsoc", "soc_code", "soc", "code"])
        # prefer title columns
        title_col = pick_col(cols, ["alternate_title", "title", "name"])

        if not soc_col or not title_col:
            continue

        limit_clause = f"LIMIT {int(max_rows_per_table)}" if max_rows_per_table else ""
        q = f"""
            SELECT `{soc_col}` AS onetsoc_code, `{title_col}` AS text
            FROM `{table}`
            WHERE `{soc_col}` IS NOT NULL AND `{title_col}` IS NOT NULL
        {limit_clause};
        """
        cur.execute(q)
        for r in fetchall_dict(cur):
            text = str(r["text"]).strip()
            code = str(r["onetsoc_code"]).strip()
            if text and code:
                rows.append(
                    {
                        "text": text,
                        "onetsoc_code": code,
                        "source_table": table,
                        "source_col": title_col,
                    }
                )

    df = pd.DataFrame(rows).drop_duplicates(subset=["text", "onetsoc_code"])
    # light cleanup
    df["text"] = df["text"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    df = df[df["text"].str.len() >= 2]
    return df


def split_by_unseen_soc(
    df: pd.DataFrame,
    seed: int = 42,
    train_pct: float = 0.7,
    test_pct: float = 0.2,
    val_pct: float = 0.1,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict]:
    assert abs((train_pct + test_pct + val_pct) - 1.0) < 1e-9

    rng = random.Random(seed)
    soc_codes = sorted(df["onetsoc_code"].unique().tolist())
    rng.shuffle(soc_codes)

    n = len(soc_codes)
    n_train = int(round(n * train_pct))
    n_test = int(round(n * test_pct))
    # remainder to val
    n_val = n - n_train - n_test

    train_soc = set(soc_codes[:n_train])
    test_soc = set(soc_codes[n_train : n_train + n_test])
    val_soc = set(soc_codes[n_train + n_test :])

    train_df = df[df["onetsoc_code"].isin(train_soc)].copy()
    test_df = df[df["onetsoc_code"].isin(test_soc)].copy()
    val_df = df[df["onetsoc_code"].isin(val_soc)].copy()

    meta = {
        "seed": seed,
        "split_strategy": "unseen_by_onetsoc_code",
        "soc_counts": {"train": len(train_soc), "test": len(test_soc), "val": len(val_soc)},
        "row_counts": {"train": len(train_df), "test": len(test_df), "val": len(val_df)},
        "soc_lists": {
            "train": sorted(list(train_soc)),
            "test": sorted(list(test_soc)),
            "val": sorted(list(val_soc)),
        },
        "columns": list(df.columns),
    }
    return train_df, test_df, val_df, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="splits", help="Output directory")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train", type=float, default=0.7)
    ap.add_argument("--test", type=float, default=0.2)
    ap.add_argument("--val", type=float, default=0.1)
    ap.add_argument("--max_rows_per_table", type=int, default=0, help="0 means no limit")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    conn = connect()
    try:
        df = build_title_dataset(conn, max_rows_per_table=(args.max_rows_per_table or None))
    finally:
        conn.close()

    if df.empty:
        raise RuntimeError(
            "Dataset is empty after extraction. This usually means table/column names "
            "didn't match the heuristics. Paste SHOW TABLES; + DESCRIBE of the title tables."
        )

    train_df, test_df, val_df, meta = split_by_unseen_soc(
        df, seed=args.seed, train_pct=args.train, test_pct=args.test, val_pct=args.val
    )

    # keep only what you likely need for modeling (but preserve traceability if you want)
    keep_cols = ["text", "onetsoc_code"]
    train_df[keep_cols].to_csv(os.path.join(args.outdir, "train.csv"), index=False)
    test_df[keep_cols].to_csv(os.path.join(args.outdir, "test.csv"), index=False)
    val_df[keep_cols].to_csv(os.path.join(args.outdir, "val_unseen.csv"), index=False)

    with open(os.path.join(args.outdir, "split_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("Wrote:")
    print(f"  {os.path.join(args.outdir, 'train.csv')}")
    print(f"  {os.path.join(args.outdir, 'test.csv')}")
    print(f"  {os.path.join(args.outdir, 'val_unseen.csv')}")
    print(f"  {os.path.join(args.outdir, 'split_metadata.json')}")
    print("\nSample rows:")
    print(train_df[keep_cols].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
