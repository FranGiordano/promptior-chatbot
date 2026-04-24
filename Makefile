TF_DIR = infra

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
