# AI Technical Support and TAM Assistant

This project implements the four tasks from the Zycus technical assessment: ticket triage, TAM account health summarisation, an evaluation harness, and a production design note.

The solution uses only the supplied synthetic tickets, account summaries, and product knowledge base.

## Stack

- Python
- FastAPI
- Streamlit
- Gemini API
- scikit-learn TF-IDF retrieval
- Pydantic
- pytest

## Repository structure

```text
app/                    Application logic
app/triage/             Ticket triage pipeline and prompt
app/tam/                Account health pipeline and prompt
data/                   Supplied tickets and accounts
knowledge-base/         Supplied Markdown knowledge base
evaluation/             Evaluation cases and scoring
scripts/                Local utility scripts
ui/                     Streamlit demo
DESIGN.md               Production design note
DATA_SCHEMA.md          Supplied data schema
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

The application also works without an API key by using a small deterministic local fallback. The assessment submission should be demonstrated with the Gemini API enabled.

## Run the API

From the repository root:

```bash
uvicorn app.main:app --reload
```

API endpoints:

```text
GET  /
POST /triage
POST /account-health
```

Example triage request:

```json
{
  "subject": "DataBridge Pro is timing out",
  "body": "Our pipeline is timing out when processing records."
}
```

Example account request:

```json
{
  "account_id": "ACC-3336"
}
```

## Run Streamlit

```bash
streamlit run ui/streamlit_app.py
```

The UI provides both ticket triage and TAM account health flows.

## Run the evaluation harness

```bash
python scripts/run_evaluation.py
```

The harness has five cases for each task, including an adversarial case for each task. It compares expected values where available and checks required output fields. The report contains a 0-1 score and pass/fail result for every case.

## Run pytest

```bash
pytest
```

## Design choices

Ticket triage uses a small retrieval layer before generation. The Markdown knowledge base is split by heading and indexed with TF-IDF. This keeps retrieval local, fast, and reproducible for the small supplied corpus.

The account health flow first retrieves the account and its last 90 days of tickets. Deterministic rules identify obvious risk signals before the LLM creates the final brief. This makes risk detection easier to test and prevents the LLM from being the only source of business-risk detection.

Gemini is called with temperature 0.0. Outputs are also validated with Pydantic models so the API has a stable schema.

## Prompt versions

Task 1 prompt: `triage-v1`

Task 2 prompt: `tam-v1`
