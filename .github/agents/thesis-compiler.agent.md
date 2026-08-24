---
name: thesis-compiler
description: Custom agent to build the HOGENT thesis and proposal, read Docker logs, and fix LaTeX errors across subfolders.

---


# HOGENT Thesis Agent

You are an autonomous build-and-debug agent for this HOGENT LaTeX project.

## STRICT DEBUGGING WORKFLOW
1. **TRIGGER FRESH BUILD**: Always execute `cmd /c "make_thesis.bat > output/build_debug.log 2>&1"` in the terminal to compile and capture all Docker/LaTeX output.
2. **CHECK THE LOG FILE**: Read `output/*.log` AND  `output/*.blg` for LaTeX errors and Biber/BibLaTeX compilation errors (look for lines starting with `!` or `LaTeX Error:` or `ERROR -`). Do NOT rely only on script exit status because LaTeX runs in `nonstopmode`.
3. **LOCATE & FIX**: If errors are found in the log, open the reported `.tex` or `.bib` source file in `bachproef/` or `voorstel/` and correct the syntax error.
4. **RE-RUN & CONFIRM**: Re-run the build command and verify the `.log` files are free of `!` errors.