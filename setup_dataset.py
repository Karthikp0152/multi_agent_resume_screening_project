import os
import shutil
from pathlib import Path

try:
    import kagglehub
except ImportError:  # pragma: no cover - exercised via CLI, not tests
    kagglehub = None

def setup_dataset():
    if kagglehub is None:
        print("Error: missing dependency 'kagglehub'.")
        print("Install it with: python -m pip install kagglehub")
        print("Or reinstall project dependencies with: python -m pip install -r requirements.txt")
        return

    # Dataset handle
    dataset_handle = "snehaanbhawal/resume-dataset"
    
    # Target directory
    target_dir = Path("archive")
    
    print(f"Starting download of {dataset_handle} via kagglehub...")
    try:
        download_path = kagglehub.dataset_download(dataset_handle)
        print(f"Downloaded to cache: {download_path}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nNote: You might need to set up Kaggle credentials.")
        print("See: https://github.com/Kaggle/kagglehub#authentication")
        return

    print("Organizing dataset files...")
    
    # Ensure archive directory exists
    target_dir.mkdir(exist_ok=True)
    
    # 1. Handle Resume.csv
    resume_target_dir = target_dir / "Resume"
    resume_target_dir.mkdir(exist_ok=True)

    download_root = Path(download_path)
    csv_candidates = [
        download_root / "Resume.csv",
        download_root / "Resume" / "Resume.csv",
    ]
    csv_source = next((path for path in csv_candidates if path.exists()), None)
    csv_target = resume_target_dir / "Resume.csv"

    if csv_source is None:
        print("Warning: could not find Resume.csv in downloaded dataset.")
    else:
        shutil.copy2(csv_source, csv_target)
        print(f"Copied {csv_source} -> {csv_target}")
    
    # 2. Handle data/ folder
    data_source = download_root / "data"
    data_target = target_dir / "data"
    
    if data_source.exists():
        if data_target.exists():
            print(f"Removing existing {data_target}...")
            shutil.rmtree(data_target)
        
        # Copy the whole directory
        shutil.copytree(data_source, data_target)
        print(f"Copied {data_source} -> {data_target}")
    else:
        print("Warning: could not find PDF data directory in downloaded dataset.")

    print("\nDataset setup complete!")
    print(f"CSV location: {csv_target.resolve()}")
    print(f"PDF root: {data_target.resolve()}")

if __name__ == "__main__":
    setup_dataset()
