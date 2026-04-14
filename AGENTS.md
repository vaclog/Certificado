# Repository Guidelines

## Project Structure & Module Organization
This repository is a small Python automation workflow for certificado/remito processing. Top-level scripts handle each step of the pipeline: `leer_mail.py` downloads attachments, `extraer_simple.py` and related `extraer_*.py` variants parse PDFs, `db.py` persists results to MariaDB, and `smtp.py` sends error notifications. Shared utilities live in `util.py` and `config.py`. Runtime folders such as `attached/`, `processed/`, `temp/`, `recortes/`, and `images/` contain working files and reference assets; treat them as operational data, not source code.

## Build, Test, and Development Commands
Use the Conda environment defined in `environment.yml`.

```powershell
conda env create -f environment.yml
conda activate certificado
python leer_mail.py
python extraer_simple.py
python update_desde_excel.py
```

`leer_mail.py` pulls PDF attachments from IMAP into the attachments folder set in `.env`. `extraer_simple.py` extracts RX/remito/certificado data and moves processed files to `processed/`. `certi.bat` is the Windows scheduler entrypoint that activates Conda and runs the mail + extraction sequence.

## Coding Style & Naming Conventions
Follow the existing codebase style: Python, 4-space indentation, snake_case for functions/variables, and PascalCase only for classes such as `Config` and `DB`. Keep modules focused on one task and prefer small helper functions over deeply nested logic. Preserve the current logging pattern with `logging` plus `.env`-driven configuration. There is no enforced formatter in the repo, so keep edits consistent with surrounding code.

## Testing Guidelines
There is no automated test suite yet. Validate changes by running the affected script against sample PDFs or inbox data in a non-production environment and confirm database writes, file moves, and email notifications behave as expected. For parser changes, test at least one matching PDF and one non-matching PDF. If you add tests, place them under `tests/` and use `test_<module>.py`.

## Commit & Pull Request Guidelines
Recent commits use short, imperative summaries in Spanish, for example `descomento mover archivo` or `nuevo formato de remitos`. Keep commits focused and descriptive. PRs should include: the workflow affected, any required `.env` or database assumptions, manual validation steps, and screenshots or log excerpts only when they clarify parser behavior or failures.

## Security & Configuration Tips
Do not commit `.env`, PDFs, spreadsheets, or generated images; `.gitignore` already excludes them. Keep credentials in `.env` only, and avoid hardcoding machine-specific paths outside local batch files such as `certi.bat`.
