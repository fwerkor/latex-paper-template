$pdf_mode = 1;
$out_dir = 'build';
$aux_dir = 'build';
$max_repeat = 5;
$bibtex_use = 2;
$cleanup_includes_cusdep_generated = 1;
@default_files = ('paper.tex');

# Keep compilation deterministic and fail on real TeX errors.
$pdflatex = 'pdflatex %O -file-line-error -halt-on-error -interaction=nonstopmode -synctex=1 %S';
