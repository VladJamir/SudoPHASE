# Thesis Manuscript

This directory contains the LaTeX source files for the thesis manuscript.

## Compiling the Thesis

### Prerequisites
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Required LaTeX packages (should be available in most distributions)

### Compilation

**Using pdflatex:**
```bash
pdflatex thesis.tex
bibtex thesis  # If you add citations
pdflatex thesis.tex
pdflatex thesis.tex  # Run twice for proper references
```

**Using Make (if Makefile is available):**
```bash
make thesis
```

**Using latexmk (recommended):**
```bash
latexmk -pdf thesis.tex
```

## Document Structure

The thesis is organized into the following sections:

1. **Introduction**: Background, motivation, objectives, and contributions
2. **Literature Review**: Related work on Sudoku solving and parallel metaheuristics
3. **Methodology**: Detailed descriptions of all three algorithms
4. **Implementation**: System architecture and implementation details
5. **Experimental Evaluation**: Results, analysis, and discussion
6. **Conclusion**: Summary and future work

## Customization

### Adding Your Information
Edit the following lines in `thesis.tex`:
```latex
\title{Parallel Ant Colony System with Simulated Annealing for Sudoku Puzzle Solving}
\author{Your Name}
\date{\today}
```

### Adding Figures
To add figures, use:
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{figures/your_figure.pdf}
\caption{Your figure caption}
\label{fig:your_label}
\end{figure}
```

### Adding Tables
Tables can be added using the `table` environment. See the existing table in Section 5 for an example.

### Adding Citations
1. Add entries to the bibliography section at the end
2. Cite them in the text using `\cite{key}`
3. Run `bibtex` and recompile

## Notes

- The document uses standard LaTeX packages that should be available in most distributions
- If compilation fails due to missing packages, install them using your LaTeX distribution's package manager
- The abstract, table of contents, and bibliography are automatically generated
- Page numbers and headers can be customized if needed

## Output

The compiled PDF will be named `thesis.pdf` and will contain:
- Title page
- Abstract
- Table of Contents
- All sections with proper formatting
- Bibliography
























