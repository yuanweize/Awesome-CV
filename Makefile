.PHONY: all resume coverletter init clean help

CC = lualatex
BUILD_DIR = build

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: resume coverletter

resume: | $(BUILD_DIR)
	$(CC) -output-directory=$(BUILD_DIR) main.tex
	$(CC) -output-directory=$(BUILD_DIR) main.tex
	@echo "  -> $(BUILD_DIR)/main.pdf"

coverletter: | $(BUILD_DIR)
	$(CC) -output-directory=$(BUILD_DIR) coverletter.tex
	$(CC) -output-directory=$(BUILD_DIR) coverletter.tex
	@echo "  -> $(BUILD_DIR)/coverletter.pdf"

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

#-------------------------------------------------------------------------------
# Setup for first-time users
#-------------------------------------------------------------------------------

init:
	@echo "Setting up Awesome-CV..."
	@if [ ! -f config.tex ]; then \
		cp config.tex.example config.tex; \
		echo "  Created config.tex from template"; \
	else \
		echo "  config.tex already exists, skipping"; \
	fi
	@if [ ! -f letter_config.tex ]; then \
		cp letter_config.tex.example letter_config.tex; \
		echo "  Created letter_config.tex from template"; \
	else \
		echo "  letter_config.tex already exists, skipping"; \
	fi
	@if [ ! -d sections ]; then \
		mkdir -p sections; \
	fi
	@for f in sections_template/*.tex; do \
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
	@echo "Awesome-CV Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make init        - First-time setup (creates private config files)"
	@echo "  make resume      - Build $(BUILD_DIR)/main.pdf"
	@echo "  make coverletter - Build $(BUILD_DIR)/coverletter.pdf"
	@echo "  make all         - Build both"
	@echo "  make clean       - Remove all build artifacts"
	@echo "  make help        - Show this help message"
