# rbcapp1 monitoring assignment

My solution for the take-home in `assessment/assignment.docx`.

Quick context: rbcapp1 depends on httpd, rabbitMQ and postgreSQL. If any of those are down, the application status is DOWN.

Files are split by test — `test1/` for the python monitoring work, `assignment.yml` + `inventory` at the repo root for ansible, `test3/` for the csv script.

---

## Test 1

Three scripts in `test1/`:

- `monitor_services.py` — checks each service with `systemctl is-active` and writes a json file per service (`httpd-status-<timestamp>.json`, etc.)
- `rest_api.py` — flask app with the three endpoints from the brief
- `post_status_files.py` — small helper to push the json files to `/add`

Elasticsearch can be started with docker compose in `test1/`:

```
cd test1
pip install -r requirements.txt
docker compose up -d
python3 rest_api.py
```

Then on the linux host where the services run:

```
python3 monitor_services.py ./status-output
python3 post_status_files.py ./status-output
```

Check it worked:

```
curl http://localhost:5000/healthcheck
curl http://localhost:5000/healthcheck/httpd
```

Json written by the monitor looks like:

```json
{
   "service_name": "httpd",
   "service_status": "UP",
   "host_name": "host1"
}
```

Systemd unit names I used: `httpd`, `rabbitmq-server`, `postgresql`. On some rhel boxes postgresql might be named differently (e.g. `postgresql-15`) — worth checking before running.

The `/add` endpoint accepts json in the request body or as an uploaded file.

---

## Test 2

Inventory has host1 (httpd), host2 (rabbitMQ), host3 (postgreSQL). Update the `ansible_host` entries before running against real machines.

Run from the repo root:

```
ansible-playbook assignment.yml -i inventory -e action=verify_install
ansible-playbook assignment.yml -i inventory -e action=check-disk
ansible-playbook assignment.yml -i inventory -e action=check-status
```

What each action does:

- **verify_install** — checks packages with `rpm -q` on all hosts. Only httpd gets installed automatically if it's missing (on host1), as the assignment asked for one install example.
- **check-disk** — loops through mounts, flags anything over 80%, sends email to `ops-team@example.com` (set in inventory). Needs a mail relay on the hosts.
- **check-status** — calls the test 1 healthcheck url (`http://localhost:5000/healthcheck` by default). Start the api first.

---

## Test 3

```
python3 test3/filter_sales.py
```

Reads `assessment/sales-data.csv`, works out the average price per square foot, and writes properties below that to `test3/below_avg_price_per_sqft.csv`.
