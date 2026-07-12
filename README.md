# LaTeX Paper Template

[![Paper CI](https://github.com/fwerkor/latex-paper-template/actions/workflows/ci.yml/badge.svg)](https://github.com/fwerkor/latex-paper-template/actions/workflows/ci.yml)
[![Online PDF](https://img.shields.io/badge/PDF-online%20preview-2563eb)](https://fwerkor.github.io/latex-paper-template/)

A reusable, CI-first academic paper repository. Every push and pull request compiles the paper, checks references and citations, validates the resulting PDF, and uploads downloadable build artifacts. Every commit to `main` also publishes a stable browser preview through GitHub Pages.

## Use this template

1. Select **Use this template** on GitHub and create a repository.
2. Edit `metadata.tex`, then replace the placeholder section files under `sections/`.
3. Review the two switches in `preview-config.json`.
4. Update the repository-specific badge and Pages URL in this README.
5. In **Settings → Pages**, select **GitHub Actions** as the source if GitHub does not enable it automatically.
6. Push a commit. The PDF becomes available from both the workflow run and, by default, the Pages site.

## Online preview and downloads

For this repository:

- Stable browser preview: <https://fwerkor.github.io/latex-paper-template/>
- Direct PDF: <https://fwerkor.github.io/latex-paper-template/paper.pdf>
- Per-commit artifacts: open the latest **Paper CI** run and download the `paper-*` artifact
- Tagged releases: push a tag such as `v1.0.0`; the release workflow attaches the PDF, source archive, and checksums

The Pages preview tracks the latest successful build from `main`. Pull requests do not replace the public preview; their PDFs remain isolated as workflow artifacts.

## Preview controls

Edit `preview-config.json`:

```json
{
  "enable_public_preview": true,
  "block_search_indexing": true
}
```

| Setting | Default | Effect |
| --- | --- | --- |
| `enable_public_preview` | `true` | Publishes the latest `main` PDF through GitHub Pages. Setting it to `false` deploys a disabled notice without `paper.pdf`, replacing the currently published PDF on the next successful run. |
| `block_search_indexing` | `true` | Adds page-level `noindex`, `nofollow`, `noarchive`, and related directives, and publishes a `robots.txt` that disallows all crawlers. Setting it to `false` publishes an `Allow: /` rule and removes the page-level robots directives. |

Crawler blocking is advisory and is not access control. Anyone who knows the Pages URL can still open the PDF while public preview is enabled. Disabling public preview removes the PDF from future Pages deployments, but it cannot revoke copies that were previously downloaded or cached elsewhere. Per-commit workflow artifacts continue to be produced regardless of these switches.

## Repository layout

```text
paper.tex                 Entry point
metadata.tex              Title, authors, anonymity, and PDF metadata
config/                    Packages and custom commands
sections/                  One file per paper section
tables/                    Standalone table fragments
figures/                   Figures and editable figure sources
references.bib             BibTeX database
preview-config.json        Public preview and crawler-indexing switches
scripts/                   Build and validation utilities
.github/workflows/         CI, Pages deployment, and release automation
```

## Local development

A recent TeX Live installation with `latexmk` is recommended.

```bash
make build      # build/paper.pdf
make watch      # rebuild continuously
make check      # compile plus structural/log/PDF/preview checks
make test       # validate preview switches without rebuilding the paper
make lint       # codespell and ChkTeX
make clean
```

The PDF validator requires `pypdf`; linting additionally uses `codespell` and `chktex`:

```bash
python3 -m pip install --user pypdf codespell
```

On Debian or Ubuntu:

```bash
sudo apt-get install latexmk lmodern texlive-latex-extra texlive-science \
  texlive-fonts-recommended texlive-bibtex-extra chktex lacheck
```

## CI behavior

`Paper CI` runs on every push, pull request, and manual dispatch. It performs:

- repository and `\input`/bibliography structure validation;
- GitHub Actions schema, expression, and embedded-shell validation with actionlint;
- spelling checks for source and documentation;
- ChkTeX and LaCheck static analysis;
- reproducible compilation with a pinned GitHub Action revision and TeX Live 2025;
- failure on unresolved references, citations, duplicate labels, missing files, and fatal TeX diagnostics;
- PDF integrity, metadata, encryption, size, and page-count checks;
- upload of the PDF, log, bibliography output, and SyncTeX data as a per-commit artifact;
- upload of diagnostics even when compilation fails.

`Publish PDF` reads `preview-config.json`, then either deploys the latest `main` PDF with the selected crawler policy or replaces the site with a preview-disabled notice. `Release paper` creates a GitHub Release for `v*` tags. Dependabot proposes updates for GitHub Actions each week.

## Adapting to a conference template

Replace `\documentclass` and packages in `paper.tex`/`config/packages.tex` with the venue files. Keep `paper.tex` as the root file, or update `ROOT`, workflow `root_file`, and scripts consistently. Commit required `.cls`, `.sty`, and bibliography-style files when redistribution is permitted.

For double-blind review, leave `\anonymoustrue` enabled in `metadata.tex`. Before a camera-ready release, switch to `\anonymousfalse`, fill in authors and affiliations, remove visible TODO markers, and inspect the PDF artifact.

## License

The repository infrastructure and placeholder content are available under the MIT License. Replace the license when the venue, publisher, or project requires different terms.
