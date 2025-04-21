# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a benchmarking framework for evaluating face-swapping tools. The framework:

1. Takes template images containing faces
2. Swaps faces with provided avatar images 
3. Evaluates the quality of the face swaps
4. Provides a web interface and CLI for benchmarking

## Commands
- Setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pip install -e .`
- Run web UI: `python start_web.py`
- CLI: `python -m benchmark.cli run`, `python -m benchmark.cli run --case-ids tc_01`, `python -m benchmark.cli report <run_id>`

## Environment Variables
- `REPLICATE_API_TOKEN`: Required for using Replicate's face swap models

## Code Style
- Python 3.10+ async style with type annotations
- Imports: stdlib first, then third-party, then local
- Use Pydantic for data models
- Naming: snake_case for variables/functions, PascalCase for classes
- Error handling: Always use try/except with specific exceptions
- Async/await pattern for concurrent operations
- Follow SQLAlchemy ORM patterns for database operations
- FastAPI for web endpoints, WebSockets for real-time updates

## Key Components

- `benchmark/core/plugins/` - Contains plugins for different face swap methods
- `benchmark/core/runner.py` - Orchestrates the benchmark execution
- `benchmark/web/` - Web interface for the benchmark
- `datasets/` - Test cases with template and avatar images

## Development Guidelines

1. The benchmark uses Replicate's API to perform face swapping
2. Each plugin must have a `generate(case)` function that returns a PIL Image
3. Ensure REPLICATE_API_TOKEN is set in the environment when testing
4. The web UI uses FastAPI with WebSockets for real-time updates
5. Test cases are defined in `datasets/test_cases.json`

## Troubleshooting

1. If face swapping fails, check the Replicate API token is set correctly
2. Ensure the template and avatar images exist at the specified paths
3. Look for detailed error messages in the browser console
4. For file upload issues, ensure the correct Content-Type is used (application/octet-stream)

## Key API Details

- Replicate model: cdingram/face-swap (version d1d6ea8c8be89d664a07a457526f7128109dee7030fdac424788d762c71ed111)
- API file upload endpoint: https://api.replicate.com/v1/files
- API prediction endpoint: https://api.replicate.com/v1/predictions