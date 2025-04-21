# Face Swap Benchmarking Framework

This project provides a framework to benchmark face-swapping tools by swapping people in a template photo with supplied avatar images.

![Face Swap Benchmark Screenshot](https://github.com/yourusername/face-swap-benchmark/raw/main/docs/screenshot.png)

## Features

- Fast face-swapping evaluation using Replicate's API (cdingram/face-swap)
- Web interface for visual comparison of results
- Python CLI for automated benchmarking
- Customizable test cases with multiple avatars
- Automatic evaluation of face swap quality
- Human-provided rating system

## Installation

```bash
git clone <repo-url>
cd <repo>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .  # Install in development mode
```  

## Configuration

This project uses the Replicate API for face swapping. Set your API key in the environment:
```bash
export REPLICATE_API_TOKEN="your_replicate_api_token"
```
Alternatively, create a `.env` file in the project root with:
```text
REPLICATE_API_TOKEN=your_replicate_api_token
```

## Quick Start

1. Start the web UI:
   ```bash
   python start_web.py
   ```

2. Open http://localhost:8000 in your browser

3. Select test cases and run the benchmark

4. View and rate the results

## CLI Usage

Run the benchmark on all test cases:
```bash
python -m benchmark.cli run
```  

Run the benchmark on specific test cases:
```bash
python -m benchmark.cli run --case-ids tc_01 tc_02
```

Generate report after a run:
```bash
python -m benchmark.cli report <run_id>
```  

## Test Cases

The framework comes with pre-defined test cases in `datasets/test_cases.json`. Each test case contains:

- A template image with two or more people
- Avatar images to swap onto the faces in the template
- Descriptive information about the scene and swap instructions

## Plugins

The framework currently uses the following face-swap plugins:

- `baseline_replicate`: Uses Replicate's face-swap model (cdingram/face-swap) to perform face swapping

## Extending the Framework

### Adding New Test Cases

Test cases are defined in `datasets/test_cases.json`. Each test case should include:

- `id`: A unique identifier for the test case
- `description`: A description of the scene
- `template_image`: Path to the template image
- `avatars`: Array of paths to avatar images
- `instructions`: Instructions for the face swap

### Adding New Face Swap Methods

To add new face-swap models, create a new plugin in `benchmark/core/plugins/`. Each plugin should have a `generate(case)` function that takes a test case and returns a PIL Image.

## License

MIT License - see LICENSE file for details.