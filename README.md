# Scale AI RLHF Pipeline

This repository contains an advanced pipeline designed for Reinforcement Learning from Human Feedback (RLHF) processing. It simulates a robust, multi-agent workflow to ingest, process, annotate, verify, and finalize text pairs to produce high-quality training data for LLMs.

## Overview

The Scale AI RLHF Pipeline employs a system of specialized AI agents, each handling a crucial step in the data refinement process. The architecture is modular and queue-based to handle large volumes of data efficiently.

The agents involved are:

1. **Ingestion Agent (`agents/ingestion_agent.py`)**: Reads the raw data, validates its schema, and batches it for processing.
2. **Router Agent (`agents/router_agent.py`)**: Acts as a dispatcher, intelligently routing batched data to appropriate models or processing queues based on task complexity.
3. **Annotator Agent (`agents/annotator_agent.py`)**: Uses AI models to generate high-quality responses or annotations for the input prompts. 
4. **Quality Agent (`agents/quality_agent.py`)**: Acts as a reviewer to grade the annotated responses for helpfulness, harmlessness, and accuracy.
5. **Consensus Agent (`agents/consensus_agent.py`)**: Acts as an arbiter to resolve disagreements and filter out low-quality annotations, ensuring only the best data makes it to the final dataset.

## Setup and Installation

1. **Install Dependencies**:
   Ensure you have Python 3 installed. Then, create a virtual environment and install the required packages:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Configuration**:
   - Update `config.yaml` to tweak pipeline parameters (e.g., batch sizes, model parameters).
   - Set up your `.env` file with necessary API keys (like `GEMINI_API_KEY`) required for the agents to operate.

## How to Run

To run the pipeline and process a dataset, you can execute the `main.py` script and pass your JSONL file as an argument:

```bash
python main.py data/raw_pairs.jsonl
```

### Process Simulation

Running `main.py` acts as a simulation of the full end-to-end RLHF pipeline:
- The system reads `raw_pairs.jsonl`.
- Data flows sequentially through the agents (Ingestion -> Router -> Annotator -> Quality -> Consensus).
- Clean, verified pairs are outputted.

### Outputs

After execution, the finalized, high-quality data is exported to the `outputs/` directory as `final_pairs.jsonl`. This data is ready to be used in RLHF training!

## Directory Structure

- `agents/`: Contains the logic for the different agents in the pipeline.
- `data/`: Contains sample datasets (e.g., `raw_pairs.jsonl`).
- `outputs/`: Destination for processed data files.
- `utils/`: Helper scripts and utilities used across the pipeline (e.g., inter-rater reliability calculations like Cohen's Kappa).
