SHELL := /usr/bin/env bash
ROOT := paper.tex
OUT := build
PDF := $(OUT)/paper.pdf

.PHONY: all build watch check lint clean dist help

all: build

build:
	./scripts/build.sh

watch:
	mkdir -p $(OUT)
	latexmk -pdf -pvc -file-line-error -halt-on-error -interaction=nonstopmode -synctex=1 -outdir=$(OUT) $(ROOT)

check: build
	python3 scripts/check_structure.py
	python3 scripts/check_log.py $(OUT)/paper.log
	python3 scripts/validate_pdf.py $(PDF)

lint:
	codespell
	chktex -q $(ROOT)

clean:
	latexmk -C -outdir=$(OUT) $(ROOT) || true
	rm -rf $(OUT) dist public

dist: check
	./scripts/package-source.sh

help:
	@printf '%s\n' \
	  'make build  - compile the paper into build/paper.pdf' \
	  'make watch  - continuously rebuild while editing' \
	  'make check  - compile and run structural/log/PDF checks' \
	  'make lint   - run spelling and LaTeX linters' \
	  'make dist   - create source and PDF release bundles' \
	  'make clean  - remove generated files'
