import os
import io
import zipfile
import math
import requests
import pandas as pd

UCI_ZIP_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
OUTPUT_PREFIX = "sms_part"
NUM_PARTS = 5  # Split into 5 CSV files

def download_zip(url: str) -> bytes:
    print("Downloading dataset...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    print("Download complete.")
    return r.content

def extract_sms_data(zip_bytes: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for filename in z.namelist():
            if "SMSSpamCollection" in filename:
                with z.open(filename) as f:
                    raw = f.read().decode("utf-8", errors="replace")
                break
        else:
            raise RuntimeError("SMS Spam Collection file not found")

    rows = [line.split("\t", 1) for line in raw.splitlines() if line.strip()]
    df = pd.DataFrame(rows, columns=["label", "text"])
    df["label"] = df["label"].str.lower().str.strip()
    df["text"] = df["text"].str.strip()
    return df

def split_and_save(df, num_parts, prefix):
    total = len(df)
    per = math.ceil(total / num_parts)
    print(f"Total messages = {total}. Each file ≈ {per} rows.")

    for i in range(num_parts):
        start = i * per
        end = min(total, (i + 1) * per)
        part = df.iloc[start:end]
        filename = f"{prefix}{i+1}.csv"
        part.to_csv(filename, index=False, encoding="utf-8")
        print(f"Saved {filename} ({len(part)} rows)")

def main():
    if os.path.exists("sms_part1.csv"):
        print("Dataset already created. Delete files if you want to regenerate.")
        return

    zip_bytes = download_zip(UCI_ZIP_URL)
    df = extract_sms_data(zip_bytes)

    # Shuffle to mix spam/ham properly
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    split_and_save(df, NUM_PARTS, OUTPUT_PREFIX)
    print("Dataset prepared successfully.")

if __name__ == "__main__":
    main()
