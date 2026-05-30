#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "assessment" / "sales-data.csv"
OUTPUT = Path(__file__).resolve().parent / "below_avg_price_per_sqft.csv"


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT

    with src.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames

    price_per_ft = []
    for row in rows:
        sqft = float(row["sq__ft"])
        if sqft > 0:
            price_per_ft.append(float(row["price"]) / sqft)

    avg = sum(price_per_ft) / len(price_per_ft)

    kept = []
    for row in rows:
        sqft = float(row["sq__ft"])
        if sqft <= 0:
            continue
        if (float(row["price"]) / sqft) < avg:
            kept.append(row)

    with dst.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)

    print(f"avg price/sqft: ${avg:.2f}")
    print(f"kept {len(kept)} of {len(rows)} rows -> {dst}")


if __name__ == "__main__":
    main()
