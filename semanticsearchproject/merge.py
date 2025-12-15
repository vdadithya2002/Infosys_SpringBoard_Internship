#!/usr/bin/env python3
"""
merge_and_clean_youtube.py

Usage:
    python merge_and_clean_youtube.py \
        --base base_dataset.csv \
        --your your_dataset.csv \
        --out merged_cleaned.csv \
        --drop-duplicates

This script:
 1. loads two CSVs (base and your dataset)
 2. merges them (concatenation, keeping all columns)
 3. cleans `title` and `transcript` columns (remove special chars, lowercasing)
 4. finds duplicates (by video id and by title+transcript fingerprint)
 5. converts ISO8601 duration (contentDetails.duration) to seconds into `duration_seconds`
 6. writes outputs and duplicates report
"""

import argparse
import pandas as pd
import re
try:
    import isodate
except Exception:  # pragma: no cover - friendly message for missing dependency
    raise SystemExit("Missing dependency 'isodate'. Install it in your environment: pip install isodate")
from typing import Optional

# ---------- Utility functions ----------

def load_csv(path: str) -> pd.DataFrame:
    print(f"Loading: {path}")
    df = pd.read_csv(path, dtype=str)  # read everything as str to avoid dtype surprises
    print(f"  -> {len(df)} rows, {len(df.columns)} columns")
    return df

def merge_dfs(base: pd.DataFrame, other: pd.DataFrame) -> pd.DataFrame:
    # Simple vertical concatenation (append). Align columns automatically.
    print("Merging datasets (concatenate rows).")
    merged = pd.concat([base, other], ignore_index=True, sort=False)
    print(f"  -> Merged size: {len(merged)} rows, {len(merged.columns)} columns")
    return merged

def clean_text_column(s: Optional[str]) -> Optional[str]:
    if pd.isna(s):
        return s
    # Normalize whitespace, remove special characters except basic punctuation we might want to keep (.,?!) and numbers
    # You can modify regex to allow/disallow characters as needed.
    text = str(s)
    # Replace newline/tab with space
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove unwanted characters; keep letters, numbers, common punctuation, and spaces
    text = re.sub(r"[^0-9a-zA-Z\s\.\,\?\!\:\;\-\_\(\)]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text).strip()
    # Lowercase
    text = text.lower()
    return text

def convert_iso8601_to_seconds(duration_str: Optional[str]) -> Optional[int]:
    if pd.isna(duration_str) or duration_str == '':
        return None
    try:
        # isodate.parse_duration returns timedelta or Duration
        dur = isodate.parse_duration(duration_str)
        # Some implementations return isodate.duration.Duration which may not have total_seconds,
        # so convert to seconds via timedelta if possible.
        # If it's a Duration (years, months), fallback to None
        if hasattr(dur, 'total_seconds'):
            return int(dur.total_seconds())
        else:
            # attempt to convert Duration to seconds if possible (years/months unknown length -> skip)
            return int(dur.days * 86400 + dur.seconds)
    except Exception as e:
        # Fallback: try manual parsing for patterns like PT1H2M3S
        try:
            pattern = re.compile(r'P(T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)')
            m = pattern.match(duration_str)
            if m:
                hours = int(m.group(2)) if m.group(2) else 0
                mins = int(m.group(3)) if m.group(3) else 0
                secs = int(m.group(4)) if m.group(4) else 0
                return hours*3600 + mins*60 + secs
        except Exception:
            pass
        print(f"Warning: failed to parse duration '{duration_str}': {e}")
        return None

# ---------- Main pipeline ----------

def process(args):
    base = load_csv(args.base)
    other = load_csv(args.your)

    # Merge
    merged = merge_dfs(base, other)

    # Ensure columns exist
    # We'll operate on 'title' and 'transcript' if present; otherwise create empty columns for consistency
    for col in ['title', 'transcript', 'duration', 'id']:
        if col not in merged.columns:
            merged[col] = pd.NA

    # Clean title and transcript
    print("Cleaning 'title' and 'transcript' columns (remove special chars + lowercase).")
    merged['title_clean'] = merged['title'].apply(clean_text_column)
    merged['transcript_clean'] = merged['transcript'].apply(clean_text_column)

    # Duplicate checking
    print("Checking duplicates...")
    # 1) Duplicates by 'id' (video id) if available
    dup_by_id = merged[merged['id'].duplicated(keep=False) & merged['id'].notna()].sort_values('id')
    print(f"  -> Duplicates by id: {dup_by_id['id'].nunique()} duplicated ids, {len(dup_by_id)} duplicate rows")

    # 2) Duplicates by title_clean + transcript_clean fingerprint
    merged['fingerprint'] = (merged['title_clean'].fillna('') + '||' + merged['transcript_clean'].fillna('')).astype(str)
    dup_by_fprint = merged[merged['fingerprint'].duplicated(keep=False)].sort_values('fingerprint')
    print(f"  -> Duplicates by title+transcript fingerprint: {dup_by_fprint['fingerprint'].nunique()} groups, {len(dup_by_fprint)} rows")

    # Save duplicates report
    dup_report = pd.concat([
        dup_by_id.assign(dup_type='by_id'),
        dup_by_fprint.assign(dup_type='by_fingerprint')
    ], ignore_index=True).drop_duplicates()
    if not dup_report.empty:
        dup_report.to_csv(args.duplicates_report, index=False)
        print(f"Duplicates report saved to: {args.duplicates_report}")
    else:
        print("No duplicates found; duplicates report not created.")

    # Optionally drop duplicates
    if args.drop_duplicates:
        # Strategy: keep first occurrence for duplicate ids and fingerprint duplicates
        before = len(merged)
        merged = merged.drop_duplicates(subset=['id'], keep='first')  # remove exact id duplicates first
        merged = merged.drop_duplicates(subset=['fingerprint'], keep='first')  # then text-based duplicates
        after = len(merged)
        print(f"Dropped duplicates. Rows before: {before}, after: {after}")

    # Convert duration to seconds
    print("Converting 'duration' (ISO8601) to seconds in 'duration_seconds' column.")
    merged['duration_seconds'] = merged['duration'].apply(convert_iso8601_to_seconds)

    # Drop old columns: title, transcript, duration (keep only the cleaned versions)
    print("Dropping original columns: 'title', 'transcript', 'duration' (keeping cleaned versions).")
    cols_to_drop = [c for c in ['title', 'transcript', 'duration'] if c in merged.columns]
    merged = merged.drop(columns=cols_to_drop)

    # Final column ordering suggestion
    cols = list(merged.columns)
    # Move key columns early
    front = ['id', 'title_clean', 'transcript_clean', 'duration_seconds']
    rest = [c for c in cols if c not in front]
    final_cols = [c for c in front if c in cols] + rest
    merged = merged[final_cols]

    # Save merged cleaned CSV
    merged.to_csv(args.out, index=False)
    print(f"Merged and cleaned dataset saved to: {args.out}")
    print("Done.")

# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge and clean YouTube datasets")
    parser.add_argument("--base", required=True, help="Path to base CSV (e.g. cleaned_youtube_data.csv)")
    parser.add_argument("--your", required=True, help="Path to your CSV to merge (e.g. nikhil_kamath_50_videos.csv)")
    parser.add_argument("--out", default="merged_cleaned.csv", help="Output merged CSV path")
    parser.add_argument("--duplicates-report", default="duplicates_report.csv", help="Duplicates report CSV")
    parser.add_argument("--drop-duplicates", action="store_true", help="Drop duplicates in the merged output")
    args = parser.parse_args()
    process(args)
