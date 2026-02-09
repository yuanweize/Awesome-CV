.PHONY: all resume coverletter init clean help

CC = lualatex

#-------------------------------------------------------------------------------
# Main targets
#-------------------------------------------------------------------------------

all: resume coverletter

resume: main.pdf

coverletter: coverletter.pdf

main.pdf: main.tex config.tex sections/*.tex
	$(CC) main.tex
	$(CC) main.tex

coverletter.pdf: coverletter.tex config.tex sections/letter_body.tex
	$(CC) coverletter.tex
	$(CC) coverletter.tex

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
	@echo "  2. Edit files in sections/ with your content"
	@echo "  3. Run 'make resume' or 'make coverletter' or 'make all'"

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
	@echo "  make init        - First-time setup"
	@echo "  make resume      - Build main.pdf (Resume)"
	@echo "  make coverletter - Build coverletter.pdf"
	@echo "  make all         - Build both"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make help        - Show this help message"
