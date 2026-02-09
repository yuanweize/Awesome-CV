.PHONY: all init clean help

CC = lualatex
MAIN = main.tex

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: main.pdf

main.pdf: $(MAIN) config.tex sections/*.tex
	$(CC) $(MAIN)
	$(CC) $(MAIN)  # Run twice for references

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
	@if [ ! -d sections ]; then \
		cp -r sections_template sections; \
		echo "  Created sections/ from template"; \
	else \
		echo "  sections/ already exists, skipping"; \
	fi
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. Edit config.tex with your personal information"
	@echo "  2. Edit files in sections/ with your content"
	@echo "  3. Run 'make' to compile your CV"

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------

clean:
	rm -f *.pdf *.aux *.log *.out *.toc *.fls *.synctex.gz

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------

help:
	@echo "Awesome-CV Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make init   - First-time setup (creates config.tex and sections/)"
	@echo "  make        - Compile main.pdf"
	@echo "  make clean  - Remove build artifacts"
	@echo "  make help   - Show this help message"
