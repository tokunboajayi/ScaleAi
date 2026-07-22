# Google Antigravity Multi-Agent RLHF Pipeline

A production-grade, 5-agent autonomous pipeline built on Google Antigravity that automates the annotation, quality control, consensus arbitration, and dataset export stages of RLHF data production.

## Features
- **Intelligent Routing**: Automatically routes expert domain tasks (Legal, Medical, Code) to specific annotator pools.
- **AI Pre-Scoring**: Uses Gemini to pre-score and generate rationales, reducing human annotation time.
- **Automated Quality Control**: Continuously calculates Cohen's Kappa, flagging adversarial annotators and low-agreement pairs.
- **Consensus Arbitration**: Resolves annotator disagreements using majority voting or AI tie-breaking.
- **Production Export**: Outputs clean, RLHF-ready JSONL preference pairs with full provenance.

## Getting Started

### Prerequisites
- Python 3.10+
- A Google Gemini API Key

### Installation
```bash
git clone <repository_url>
cd rlhf-pipeline
pip install -r requirements.txt
```

### Configuration
Update `config.yaml` to specify your preferred Gemini models and routing rules.
Export your API key:
```bash
export GEMINI_API_KEY="your-api-key"
```

### Running the Pipeline
Place your raw preference pairs in a JSONL file (e.g. `data/raw_pairs.jsonl`), then run the pipeline:
```bash
python main.py data/raw_pairs.jsonl
```

The cleaned dataset and exclusion logs will be written to the `outputs/` directory.
