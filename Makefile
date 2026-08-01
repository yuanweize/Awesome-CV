.PHONY: all resume coverletter merged init clean help validate validate-template status context context-smoke privacy portfolio-audit role-audit test check dify-check dify-package prepare-tex-cache

CC = lualatex
PYTHON ?= python3
BUILD_DIR = build
JD ?=
ROLE ?=
CONTEXT_OUTPUT ?= $(BUILD_DIR)/ai-context.generated.md
PYTHONPYCACHEPREFIX ?= /tmp/awesome-cv-pycache
export PYTHONPYCACHEPREFIX

# Keep LuaTeX's generated font/cache files outside the repository. This also
# makes local builds work when the system TeX tree is read-only.
TEX_CACHE_ROOT ?= $(if $(TMPDIR),$(TMPDIR),/tmp)
TEXMFVAR ?= $(TEX_CACHE_ROOT)/awesome-cv-texmf
TEXMFCONFIG ?= $(TEX_CACHE_ROOT)/awesome-cv-texconfig
export TEXMFVAR TEXMFCONFIG

# Add src/ to TeX search path so \documentclass{awesome-cv} finds awesome-cv.cls
export TEXINPUTS := src/:.:$(TEXINPUTS)

# Extract and whitelist the author slug before it reaches a shell command.
AUTHOR := $(shell $(PYTHON) tools/author_slug.py config.tex 2>/dev/null)

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: validate resume coverletter merged

validate:
	@$(PYTHON) tools/validate_master_cv.py --strict

validate-template:
	@$(PYTHON) tools/validate_master_cv.py templates/master_cv.yaml.example --strict

status:
	@./cv status

context:
	@test -n "$(JD)" || (echo "Usage: make context JD=path/to/job.md [ROLE=systems]" >&2; exit 2)
	@mkdir -p "$(BUILD_DIR)"
	@$(PYTHON) tools/generate_ai_context.py --jd "$(JD)" $(if $(ROLE),--role "$(ROLE)",) --output "$(CONTEXT_OUTPUT)"

context-smoke:
	@output=$$(mktemp "$${TMPDIR:-/tmp}/awesome-cv-context.XXXXXX"); \
	trap 'rm -f "$$output"' EXIT; \
	$(PYTHON) tools/generate_ai_context.py \
		--master templates/master_cv.yaml.example \
		--jd tests/fixtures/systems_job.md \
		--role systems \
		--output "$$output"; \
	grep -q 'project.signalwatch-features' "$$output"; \
	if grep -q 'alex@example.org' "$$output"; then \
		echo "Context smoke test leaked contact data" >&2; exit 1; \
	fi; \
	if grep -q 'private:employment-reference' "$$output"; then \
		echo "Context smoke test leaked a private evidence locator" >&2; exit 1; \
	fi

privacy:
	@$(PYTHON) tools/privacy_check.py

portfolio-audit:
	@$(PYTHON) tools/portfolio_audit.py --strict

role-audit:
	@$(PYTHON) tools/role_audit.py

test:
	@$(PYTHON) -m unittest discover -s tests -v
	@$(PYTHON) -m compileall -q skills/evidence-first-cv/scripts tools tests
	@$(PYTHON) -m compileall -q integrations/dify/plugin/engine integrations/dify/plugin/tools integrations/dify/plugin/provider
	@$(PYTHON) -m py_compile integrations/dify/plugin/main.py integrations/dify/plugin/engine_adapter.py
	@bash -n cv tools/tech-stack-collector/run.sh

check: validate-template privacy test context-smoke

dify-check:
	@cd integrations/dify/plugin && uv sync --frozen
	@cd integrations/dify/plugin && .venv/bin/python -c 'from dify_plugin.config.config import DifyPluginEnv; from dify_plugin.core.plugin_registration import PluginRegistration; r = PluginRegistration(DifyPluginEnv()); print("Dify plugin OK:", sorted(r.tools_mapping["evidence_first_cv"][2]))'

dify-package:
	@$(PYTHON) tools/package_dify_plugin.py


prepare-tex-cache:
	@mkdir -p "$(TEXMFVAR)" "$(TEXMFCONFIG)"

resume: prepare-tex-cache | $(BUILD_DIR)
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_CV" src/main.tex
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_CV" src/main.tex
	@echo "  -> $(BUILD_DIR)/$(AUTHOR)_CV.pdf"

coverletter: prepare-tex-cache | $(BUILD_DIR)
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_Cover_Letter" src/coverletter.tex
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_Cover_Letter" src/coverletter.tex
	@echo "  -> $(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf"

merged: resume coverletter
	@if command -v pdfunite >/dev/null 2>&1; then \
		pdfunite "$(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf" "$(BUILD_DIR)/$(AUTHOR)_CV.pdf" "$(BUILD_DIR)/$(AUTHOR)_Application.pdf"; \
		echo "  -> $(BUILD_DIR)/$(AUTHOR)_Application.pdf (merged)"; \
	else \
		echo "  ⚠ pdfunite not found, skipping merge (install poppler: brew install poppler)"; \
	fi

$(BUILD_DIR):
	@mkdir -p "$(BUILD_DIR)"

#-------------------------------------------------------------------------------
# Setup for first-time users
#-------------------------------------------------------------------------------

init:
	@echo "Setting up Awesome-CV..."
	@if [ ! -f config.tex ]; then \
		cp templates/config.tex.example config.tex; \
		echo "  Created config.tex from template"; \
	else \
		echo "  config.tex already exists, skipping"; \
	fi
	@if [ ! -f letter_config.tex ]; then \
		cp templates/letter_config.tex.example letter_config.tex; \
		echo "  Created letter_config.tex from template"; \
	else \
		echo "  letter_config.tex already exists, skipping"; \
	fi
	@if [ ! -d sections ]; then \
		mkdir -p sections; \
	fi
	@for f in templates/sections/*.tex; do \
		base=$$(basename $$f); \
		if [ ! -f sections/$$base ]; then \
			cp $$f sections/$$base; \
			echo "  Created sections/$$base from template"; \
		fi; \
	done
	@mkdir -p meta meta/applications profiles archive/applications archive/research
	@if [ ! -f meta/master_cv.yaml ]; then \
		cp templates/master_cv.yaml.example meta/master_cv.yaml; \
		echo "  Created meta/master_cv.yaml from template"; \
	else \
		echo "  meta/master_cv.yaml already exists, skipping"; \
	fi
	@if [ ! -f meta/applications.yaml ]; then \
		cp templates/applications.yaml.example meta/applications.yaml; \
		echo "  Created meta/applications.yaml from template"; \
	else \
		echo "  meta/applications.yaml already exists, skipping"; \
	fi
	@if [ ! -f meta/profile_catalog.yaml ]; then \
		cp templates/profile_catalog.yaml.example meta/profile_catalog.yaml; \
		echo "  Created meta/profile_catalog.yaml from template"; \
	else \
		echo "  meta/profile_catalog.yaml already exists, skipping"; \
	fi
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. Edit meta/master_cv.yaml with your master database"
	@echo "  2. Run 'make validate' to verify schema"
	@echo "  3. Edit config.tex and sections/ for target roles"
	@echo "  4. Run 'make resume' or './cv build <company>'"

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------

clean:
	@$(PYTHON) tools/safe_clean.py --build-dir "$(BUILD_DIR)"

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------

help:
	@echo "Awesome-CV Makefile (Author: $(AUTHOR))"
	@echo ""
	@echo "Targets:"
	@echo "  make init        - First-time setup (creates private config files)"
	@echo "  make validate    - Validate the private evidence-first master database"
	@echo "  make status      - Report memory, manifests, applications, and profile drift"
	@echo "  make context JD=job.md ROLE=systems - Export evidence-bound AI context"
	@echo "  make context-smoke - Exercise the public JD-to-context workflow"
	@echo "  make privacy     - Check tracked files for private data and secrets"
	@echo "  make portfolio-audit - Compare private GitHub inventory with governed portfolio memory"
	@echo "  make role-audit   - Report career interests, readiness, and claim coverage"
	@echo "  make test        - Run unit and syntax tests"
	@echo "  make check       - Validate template, privacy, and tests"
	@echo "  make dify-check  - Sync the locked Dify SDK and load all plugin tools"
	@echo "  make dify-package - Build and inspect a clean ignored .difypkg archive"
	@echo "  make resume      - Build $(BUILD_DIR)/$(AUTHOR)_CV.pdf"
	@echo "  make coverletter - Build $(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf"
	@echo "  make merged      - Merge Cover Letter + CV into $(BUILD_DIR)/$(AUTHOR)_Application.pdf"
	@echo "  make all         - Build all (resume + coverletter + merged)"
	@echo "  make clean       - Remove all build artifacts"
	@echo "  make help        - Show this help message"
