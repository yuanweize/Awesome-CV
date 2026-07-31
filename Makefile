.PHONY: all resume coverletter merged init clean help validate validate-template context context-smoke privacy test check

CC = lualatex
PYTHON ?= python3
BUILD_DIR = build
JD ?=
ROLE ?=
CONTEXT_OUTPUT ?= $(BUILD_DIR)/ai-context.generated.md

# Add src/ to TeX search path so \documentclass{awesome-cv} finds awesome-cv.cls
export TEXINPUTS := src/:.:$(TEXINPUTS)

# Extract and whitelist the author slug before it reaches a shell command.
AUTHOR := $(shell $(PYTHON) tools/author_slug.py config.tex 2>/dev/null)

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: validate resume coverletter merged

validate:
	@$(PYTHON) tools/validate_master_cv.py

validate-template:
	@$(PYTHON) tools/validate_master_cv.py templates/master_cv.yaml.example --strict

context:
	@test -n "$(JD)" || (echo "Usage: make context JD=path/to/job.md [ROLE=systems]" >&2; exit 2)
	@mkdir -p "$(BUILD_DIR)"
	@$(PYTHON) tools/generate_ai_context.py --jd "$(JD)" $(if $(ROLE),--role "$(ROLE)",) --output "$(CONTEXT_OUTPUT)"

context-smoke:
	@mkdir -p "$(BUILD_DIR)"
	@$(PYTHON) tools/generate_ai_context.py \
		--master templates/master_cv.yaml.example \
		--jd tests/fixtures/systems_job.md \
		--role systems \
		--output "$(BUILD_DIR)/context-smoke.generated.md"
	@grep -q 'project.signalwatch-features' "$(BUILD_DIR)/context-smoke.generated.md"
	@if grep -q 'alex@example.org' "$(BUILD_DIR)/context-smoke.generated.md"; then \
		echo "Context smoke test leaked contact data" >&2; exit 1; \
	fi
	@if grep -q 'private:employment-reference' "$(BUILD_DIR)/context-smoke.generated.md"; then \
		echo "Context smoke test leaked a private evidence locator" >&2; exit 1; \
	fi

privacy:
	@$(PYTHON) tools/privacy_check.py

test:
	@$(PYTHON) -m unittest discover -s tests -v
	@$(PYTHON) -m compileall -q skills/evidence-first-cv/scripts tools tests
	@bash -n cv tools/tech-stack-collector/run.sh

check: validate-template privacy test context-smoke


resume: | $(BUILD_DIR)
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_CV" src/main.tex
	$(CC) -output-directory="$(BUILD_DIR)" -jobname="$(AUTHOR)_CV" src/main.tex
	@echo "  -> $(BUILD_DIR)/$(AUTHOR)_CV.pdf"

coverletter: | $(BUILD_DIR)
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
	@mkdir -p meta
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
	@echo "  make context JD=job.md ROLE=systems - Export evidence-bound AI context"
	@echo "  make context-smoke - Exercise the public JD-to-context workflow"
	@echo "  make privacy     - Check tracked files for private data and secrets"
	@echo "  make test        - Run unit and syntax tests"
	@echo "  make check       - Validate template, privacy, and tests"
	@echo "  make resume      - Build $(BUILD_DIR)/$(AUTHOR)_CV.pdf"
	@echo "  make coverletter - Build $(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf"
	@echo "  make merged      - Merge Cover Letter + CV into $(BUILD_DIR)/$(AUTHOR)_Application.pdf"
	@echo "  make all         - Build all (resume + coverletter + merged)"
	@echo "  make clean       - Remove all build artifacts"
	@echo "  make help        - Show this help message"
