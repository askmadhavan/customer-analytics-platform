# Contributing

Thanks for your interest in Customer Analytics Platform. Bug reports, new dataset formats, better checks, documentation and tests are all welcome.

## Report a bug or ask for a feature

Open an [issue](https://github.com/askmadhavan/Customer-Analytics-Platform/issues) with:

- what you did, what you expected, and what happened
- for data problems, the column names and a few sample rows with any private values removed
- your browser, or your Python version for pipeline issues

Never attach real customer data to an issue.

## Make a change

1. Fork the repository and create a branch from `main`.
2. Make your change. Open an issue first for anything large, so we can agree on the approach.
3. Run the checks:

   ```bash
   pip install -r requirements.txt
   PYTHONPATH=. pytest
   flake8 api src tests
   ```

4. For web app changes, run it locally (`cd api && uvicorn app.main:app --reload`) and check the affected pages with the example data and with an uploaded CSV, on desktop and at phone width.
5. Open a pull request that explains what changed and why.

## Where things live

- **Web app:** `api/app/static/index.html`. One file holds the pages, styles and scripts, with no build step.
- **API:** `api/app/`
- **Pipeline:** `src/`, `airflow/` and `customer_analytics_dbt/`
- **Machine learning:** `ml/src/`

## Guidelines

- Keep uploaded data in the browser. Do not add code that sends it to a server.
- Show real results. Numbers in the app must come from data, not placeholders.
- Keep the web app dependency-free apart from the CSV parser.
- Follow the existing code style. CI runs flake8.

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
