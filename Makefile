TF_DIR = infra

.env:
	@cp .env.example .env && echo ".env created — fill in your values before running dev"

dev: .env
	@pip install -q -r backend/requirements.txt -r frontend/requirements.txt
	@bash -c '\
	  set -a; source .env; set +a; \
	  (cd backend && uvicorn app:app --host 0.0.0.0 --port 8000) & \
	  BACKEND_PID=$$!; \
	  trap "kill $$BACKEND_PID 2>/dev/null" EXIT; \
	  cd frontend && BACKEND_URL=http://localhost:8000 chainlit run app.py --host 0.0.0.0 --port 8080'

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
