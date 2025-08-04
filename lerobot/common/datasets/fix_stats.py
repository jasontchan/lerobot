#!/usr/bin/env python3
import os
import json
import argparse
import numpy as np
from huggingface_hub import hf_hub_download, upload_file


def collapse_emg_stats(stats: dict):
    """
    In-place collapse of any stats under keys starting with "observation.emg":
    for each of 'min','max','mean','std' compute elementwise collapse across axis=0
    then re-wrap so result has shape (1, ...) instead of (N, ...).
    """
    for key, s in stats.items():
        if key.startswith("observation.emg"):
            for stat_name, fn in [
                ("min", np.min),
                ("max", np.max),
                ("mean", np.mean),
                ("std", np.std),
            ]:
                arr = np.array(s[stat_name])
                if arr.ndim >= 2:
                    collapsed = fn(arr, axis=0)
                    collapsed = np.expand_dims(collapsed, axis=0)
                    s[stat_name] = collapsed.tolist()


def process_jsonl(in_path: str, out_path: str):
    """
    Read each line from in_path (JSONL), collapse EMG stats, write to out_path.
    """
    with open(in_path, "r") as infile, open(out_path, "w") as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            collapse_emg_stats(obj.get("stats", {}))
            outfile.write(json.dumps(obj) + "\n")


def main():
    p = argparse.ArgumentParser(
        description="Collapse EMG stats in a HF dataset's episode_stats.jsonl and push it back"
    )
    p.add_argument(
        "--repo-id",
        required=True,
        help="Hugging Face dataset repo ID (e.g. user/dataset-name)",
    )
    p.add_argument(
        "--revision",
        default="main",
        help="Branch/commit/ref to download from (default: main)",
    )
    p.add_argument(
        "--token",
        default=os.environ.get("HUGGINGFACE_TOKEN"),
        help="HF token (env HUGGINGFACE_TOKEN or pass here)",
    )
    args = p.parse_args()

    # 1) Download the existing file
    print(f"Downloading meta/episodes_stats.jsonl from {args.repo_id}...")
    local_in = hf_hub_download(
        repo_id=args.repo_id,
        repo_type="dataset",
        filename="meta/episodes_stats.jsonl",
        revision=args.revision,
        # token=args.token,
    )

    # 2) Process it
    local_out = "episodes_stats.jsonl"
    print(f"Processing and writing to {local_out}...")
    process_jsonl(local_in, local_out)

    # 3) Upload back, overwriting the original
    print(f"Uploading collapsed file back to {args.repo_id}...")
    upload_file(
        path_or_fileobj=local_out,
        path_in_repo="meta/episodes_stats.jsonl",
        repo_id=args.repo_id,
        repo_type="dataset",
        # token=args.token,
        commit_message="Collapse EMG stats in episodes_stats.jsonl",
    )
    print("Done!")


if __name__ == "__main__":
    main()
