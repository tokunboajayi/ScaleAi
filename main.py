import asyncio
import yaml
import sys
import json
import os
import argparse
import logging

from agents.ingestion_agent import IngestionAgent
from agents.router_agent import RouterAgent
from agents.annotator_agent import AnnotatorAgent
from agents.quality_agent import QualityAgent
from agents.consensus_agent import ConsensusAgent
from utils.queue import PipelineQueue
from dotenv import load_dotenv # type: ignore
from tqdm.asyncio import tqdm # type: ignore

def setup_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("pipeline.log")
        ]
    )

async def run_pipeline(input_path: str, output_dir: str):
    load_dotenv()
    logger = logging.getLogger("pipeline")
    logger.info("--- Starting Scale AI Enterprise RLHF Pipeline ---")
    
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
    logger.info("Stage 1: Ingestion")
    batches = await ingestion.process(input_path)
    
    logger.info("Stage 2: Routing")
    routed = await router.route(batches)
    
    logger.info("Stage 3: Annotation")
    # Using tqdm for visual progress if there are multiple batches
    annotated = []
    for batch in tqdm(routed, desc="Annotating Batches"):
        res = await annotator.annotate([batch])
        annotated.extend(res)
        
    logger.info("Stage 4: Quality Verification")
    verified = await quality.verify(annotated)
    
    logger.info("Stage 5: Consensus & Arbitration")
    final = await arbiter.arbitrate(verified)
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "final_pairs.jsonl")
    with open(out_path, "w") as f:
        for pair in final:
            f.write(json.dumps(pair) + "\n")
            
    logger.info(f"--- Pipeline complete ---")
    logger.info(f"Clean pairs exported: {len(final)}")
    logger.info(f"Export Path: {out_path}")
    return final

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale AI Enterprise RLHF Pipeline")
    parser.add_argument("input_path", type=str, help="Path to the input JSONL file")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory to save the final outputs")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    setup_logging(args.debug)
    asyncio.run(run_pipeline(args.input_path, args.output_dir))
