#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone

SERVICES = {
    "httpd": "httpd",
    "rabbitMQ": "rabbitmq-server",
    "postgreSQL": "postgresql",
}


def service_status(unit):
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", unit],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "DOWN"

    return "UP" if proc.stdout.strip() == "active" else "DOWN"


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    host = socket.gethostname()
    os.makedirs(out_dir, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for name, unit in SERVICES.items():
        status = service_status(unit)
        payload = {
            "service_name": name,
            "service_status": status,
            "host_name": host,
        }

        path = os.path.join(out_dir, f"{name}-status-{ts}.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=3)

        print(f"{name}: {status} -> {path}")


if __name__ == "__main__":
    main()
