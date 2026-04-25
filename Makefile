TF_DIR = infra

# APP Related Shortcuts

dev: backend/.venv frontend/.venv
	@bash -c '\
	  set -a; source .env; set +a; \
	  (cd backend && .venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000) & \
	  BACKEND_PID=$$!; \
	  trap "kill $$BACKEND_PID 2>/dev/null" EXIT; \
	  cd frontend && BACKEND_URL=http://localhost:8000 .venv/bin/chainlit run app.py --host 0.0.0.0 --port 8080'

backend/.venv:
	uv venv backend/.venv
	uv pip install -q --python backend/.venv/bin/python -e ./backend

frontend/.venv:
	uv venv frontend/.venv
	uv pip install -q --python frontend/.venv/bin/python -e ./frontend

# INFRA Related Shortcuts

init:
	terraform -chdir=$(TF_DIR) init

plan:
	terraform -chdir=$(TF_DIR) plan

apply:
	terraform -chdir=$(TF_DIR) apply

destroy:
	terraform -chdir=$(TF_DIR) destroy

apply-auto:
	terraform -chdir=$(TF_DIR) apply -auto-approve

destroy-auto:
	terraform -chdir=$(TF_DIR) destroy -auto-approve

output:
	terraform -chdir=$(TF_DIR) output
