# AI Project Repository

This repository contains the codebase for our Applicant Tracking System (ATS), Screening, and Interview AI components.

## Directory Structure

- `data/`: Raw data, datasets, and extracted text from resumes.
- `parsers/`: Logic for parsing documents (PDFs, Word docs) to extract raw text and metadata.
- `ats_engine/`: Core ATS processing and matching logic.
- `screening_ai/`: AI models for initial resume screening.
- `interview_ai/`: Generative AI components for interview questions or evaluation.
- `scoring/`: Modules for calculating candidate scores and metrics.
- `utils/`: Shared utilities, including our logging system (`logger.py`).
- `tests/`: `pytest` test suite.

## Environment Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   ```
2. **Activate Virtual Environment**:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Code Standards & Documentation

- **Formatting**: We use [Black](https://github.com/psf/black) for automated code formatting.
- **Linting**: We use [Flake8](https://flake8.pycqa.org/) to enforce style consistency.
- **Documentation**: All public functions and classes must include Google-style or Sphinx-style docstrings explaining the arguments and return values.

## Testing

Run the test suite using:
```bash
pytest
```
