.PHONY: all resume coverletter init clean help

CC = lualatex
BUILD_DIR = build

# Add src/ to TeX search path so \documentclass{awesome-cv} finds awesome-cv.cls
export TEXINPUTS := src/:.:$(TEXINPUTS)

# Auto-extract author name from config.tex: \name{First}{Last} -> First_Last
FIRST_NAME := $(shell grep '\\name{' config.tex 2>/dev/null | sed 's/.*\\name{\([^}]*\)}.*/\1/')
LAST_NAME  := $(shell grep '\\name{' config.tex 2>/dev/null | sed 's/.*\\name{[^}]*}{\([^}]*\)}.*/\1/')
AUTHOR     := $(if $(FIRST_NAME),$(FIRST_NAME)_$(LAST_NAME),Awesome)

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: resume coverletter

resume: | $(BUILD_DIR)
	$(CC) -output-directory=$(BUILD_DIR) -jobname=$(AUTHOR)_CV src/main.tex
	$(CC) -output-directory=$(BUILD_DIR) -jobname=$(AUTHOR)_CV src/main.tex
	@echo "  -> $(BUILD_DIR)/$(AUTHOR)_CV.pdf"

coverletter: | $(BUILD_DIR)
	$(CC) -output-directory=$(BUILD_DIR) -jobname=$(AUTHOR)_Cover_Letter src/coverletter.tex
	$(CC) -output-directory=$(BUILD_DIR) -jobname=$(AUTHOR)_Cover_Letter src/coverletter.tex
	@echo "  -> $(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf"

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

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
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. Edit config.tex with your personal information"
	@echo "  2. Edit letter_config.tex for your target job"
	@echo "  3. Edit files in sections/ with your content"
	@echo "  4. Run 'make resume' or 'make coverletter' or 'make all'"

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------

clean:
	rm -rf $(BUILD_DIR)
	rm -f *.aux *.log *.out *.toc *.fls *.synctex.gz *.dvi *.pdf

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------

help:
	@echo "Awesome-CV Makefile (Author: $(AUTHOR))"
	@echo ""
	@echo "Targets:"
	@echo "  make init        - First-time setup (creates private config files)"
	@echo "  make resume      - Build $(BUILD_DIR)/$(AUTHOR)_CV.pdf"
	@echo "  make coverletter - Build $(BUILD_DIR)/$(AUTHOR)_Cover_Letter.pdf"
	@echo "  make all         - Build both"
	@echo "  make clean       - Remove all build artifacts"
	@echo "  make help        - Show this help message"
