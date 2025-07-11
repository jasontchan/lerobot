import sys
from pathlib import Path
from datasets import load_dataset, Dataset


def remove_frames_with_deleted_episodes(data_dir: str, removed_indices: list[int]):
    data_dir = Path(data_dir)
    parquet_files = list(data_dir.glob("*.parquet"))
    if not parquet_files:
        print(f"No parquet files found in {data_dir}")
        return

    print(
        f"Removing frames with episode_index in {removed_indices} from {len(parquet_files)} parquet files..."
    )
    for pf in parquet_files:
        print(f"Processing {pf}...")
        ds = load_dataset("parquet", data_files=str(pf), split="train")
        orig_len = len(ds)
        ds = ds.filter(lambda x: x["episode_index"] not in removed_indices)
        new_len = len(ds)
        pf_backup = pf.with_suffix(".bak.parquet")
        pf.rename(pf_backup)
        ds.to_parquet(str(pf))
        print(f"  {orig_len-new_len} frames removed. Backup saved as {pf_backup}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python remove_frames_with_deleted_episodes.py <data_dir> <episode_idx1> [<episode_idx2> ...]"
        )
        sys.exit(1)
    data_dir = sys.argv[1]
    removed_indices = [int(x) for x in sys.argv[2:]]
    remove_frames_with_deleted_episodes(data_dir, removed_indices)
