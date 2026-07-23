import asyncio
import yaml
import sys
import json
import os

from agents.ingestion_agent import IngestionAgent
from agents.router_agent import RouterAgent
from agents.annotator_agent import AnnotatorAgent
from agents.quality_agent import QualityAgent
from agents.consensus_agent import ConsensusAgent
from utils.queue import PipelineQueue
from dotenv import load_dotenv # type: ignore

async def run_pipeline(input_path: str):
    load_dotenv()
    print("--- Starting Antigravity RLHF Pipeline ---")
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
        
    pipeline_config = config.get("pipeline", {})
    queue = PipelineQueue()
    ingestion = IngestionAgent(pipeline_config)
    router = RouterAgent(pipeline_config)
    annotator = AnnotatorAgent(pipeline_config)
    quality = QualityAgent(pipeline_config)
    arbiter = ConsensusAgent(pipeline_config)
    
    # Run pipeline stages
    batches = await ingestion.process(input_path)
    routed = await router.route(batches)
    annotated = await annotator.annotate(routed)
    verified = await quality.verify(annotated)
    final = await arbiter.arbitrate(verified)
    
    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/final_pairs.jsonl"
    with open(out_path, "w") as f:
        for pair in final:
            f.write(json.dumps(pair) + "\n")
            
    print(f"--- Pipeline complete ---")
    print(f"Clean pairs exported: {len(final)}")
    print(f"Export Path: {out_path}")
    return final

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_jsonl>")
        sys.exit(1)
    asyncio.run(run_pipeline(sys.argv[1]))
