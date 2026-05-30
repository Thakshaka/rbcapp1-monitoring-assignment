#!/usr/bin/env python3
import glob
import json
import os
import sys
import urllib.request

API = os.environ.get("API_URL", "http://localhost:5000/add")


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(glob.glob(os.path.join(folder, "*-status-*.json")))

    if not files:
        print("no status files found", file=sys.stderr)
        sys.exit(1)

    for path in files:
        with open(path) as f:
            body = json.dumps(json.load(f)).encode()

        req = urllib.request.Request(
            API,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            print(f"{path} -> {resp.status}")


if __name__ == "__main__":
    main()
