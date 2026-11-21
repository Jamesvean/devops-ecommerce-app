# DevOps Shop — Phase 1

Free Flask e-commerce demo for local Ubuntu VMware deployment, then Docker, Jenkins, Kubernetes and Terraform.

## Features
- Product catalogue
- Session-based shopping cart
- Demo checkout with SQLite order persistence (no payment processing)
- JSON health endpoint at `/health`
- pytest unit/integration tests

## Quick start
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl unzip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python app.py
```
Open http://127.0.0.1:5000 and http://127.0.0.1:5000/health from the Ubuntu VM.

## Endpoints
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Product catalogue |
| `/cart/add/<id>` | POST | Add product to session cart |
| `/cart` | GET | View cart |
| `/checkout` | POST | Save demo order to SQLite |
| `/health` | GET | Health check |

## Planned delivery phases
1. Local app and tests
2. Docker image and Compose
3. Jenkins pipeline and GitHub CI
4. K3s Kubernetes manifests and rollout
5. Terraform for AWS infrastructure
6. Observability, security, documentation, teardown

## Security and scope
This is a training/demo application, not a production store. No authentication, payment processing, inventory control, CSRF protection or production WSGI setup is included. Use loopback-only development hosting and do not expose it directly to the Internet. Production hardening is a later phase.
