#!/usr/bin/env python3
import os
from datetime import datetime, timezone

from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request

APP = "rbcapp1"
SERVICES = ("httpd", "rabbitMQ", "postgreSQL")
ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
ES_INDEX = os.environ.get("ES_INDEX", "service-status")

app = Flask(__name__)


def es_client():
    return Elasticsearch(ES_HOST)


def ensure_index(client):
    if client.indices.exists(index=ES_INDEX):
        return

    client.indices.create(
        index=ES_INDEX,
        mappings={
            "properties": {
                "service_name": {"type": "keyword"},
                "service_status": {"type": "keyword"},
                "host_name": {"type": "keyword"},
                "@timestamp": {"type": "date"},
            }
        },
    )


def latest_statuses(client):
    ensure_index(client)
    out = {}

    for svc in SERVICES:
        resp = client.search(
            index=ES_INDEX,
            size=1,
            sort=[{"@timestamp": {"order": "desc"}}],
            query={"term": {"service_name": svc}},
        )
        hits = resp["hits"]["hits"]
        out[svc] = hits[0]["_source"]["service_status"] if hits else "DOWN"

    return out


def app_status(statuses):
    return "UP" if all(v == "UP" for v in statuses.values()) else "DOWN"


@app.route("/add", methods=["POST"])
def add():
    if request.is_json:
        data = request.get_json()
    elif "file" in request.files:
        import json

        data = json.load(request.files["file"].stream)
    else:
        return jsonify({"error": "send JSON body or upload file field 'file'"}), 400

    for field in ("service_name", "service_status", "host_name"):
        if field not in data:
            return jsonify({"error": f"missing {field}"}), 400

    if data["service_name"] not in SERVICES:
        return jsonify({"error": "unknown service_name"}), 400

    doc = {
        "service_name": data["service_name"],
        "service_status": str(data["service_status"]).upper(),
        "host_name": data["host_name"],
        "@timestamp": datetime.now(timezone.utc).isoformat(),
    }

    client = es_client()
    ensure_index(client)
    client.index(index=ES_INDEX, document=doc, refresh=True)  # healthcheck picks it up immediately

    return jsonify({"status": "ok"}), 201


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    statuses = latest_statuses(es_client())
    down = [s for s, st in statuses.items() if st == "DOWN"]

    return jsonify(
        {
            "application_name": APP,
            "application_status": app_status(statuses),
            "services": statuses,
            "down_services": down,
        }
    )


@app.route("/healthcheck/<service_name>", methods=["GET"])
def healthcheck_one(service_name):
    if service_name not in SERVICES:
        return jsonify({"error": "unknown service"}), 404

    statuses = latest_statuses(es_client())
    return jsonify(
        {
            "application_name": APP,
            "application_status": app_status(statuses),
            "service_name": service_name,
            "service_status": statuses[service_name],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("API_PORT", "5000")))
