"""
Download CMS Timely and Effective Care data.

Source: Centers for Medicare & Medicaid Services
Dataset: Timely and Effective Care — Hospital
"""

import ssl
from urllib.request import urlopen, Request
from pathlib import Path

DATA_URL = (
    "https://data.cms.gov/provider-data/sites/default/files/resources/"
    "0437b5494ac61507ad90f2af6b8085a7_1770163650/"
    "Timely_and_Effective_Care-Hospital.csv"
)

OUTPUT_PATH = Path("data/timely_effective_care.csv")


def download():
    if OUTPUT_PATH.exists():
        size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
        print(f"Data already exists ({size_mb:.1f} MB): {OUTPUT_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Downloading CMS Timely and Effective Care data...")
    req = Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(req, context=ctx) as response:
        total = response.headers.get("Content-Length")
        total = int(total) if total else None
        downloaded = 0

        with open(OUTPUT_PATH, "wb") as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {downloaded / 1e6:.1f} / {total / 1e6:.1f} MB ({pct:.0f}%)", end="", flush=True)
                else:
                    print(f"\r  {downloaded / 1e6:.1f} MB", end="", flush=True)

    print()
    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Saved to {OUTPUT_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    download()
