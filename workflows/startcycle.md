// workflows/startcycle.md
# /startcycle — RLHF Pipeline Full Run 
## Trigger 
/startcycle "<path-to-input-file>" 
## Description 
Starts a complete end-to-end RLHF data processing run. Ingests raw preference pairs, routes them, AI pre-annotates, verifies quality, and exports clean JSONL to GCS. 
## Steps 
### Step 1: Validate Input @ingestion 
Validate the input file at the provided path. Check format (JSON or CSV), count total pairs, report any issues. If format is invalid, STOP and report the error. Do not proceed. 
### Step 2: Ingest and Tag @ingestion 
Process the validated input. Classify every pair by domain and difficulty. Create batches of 500. Write batch manifests to GCS. Report: total pairs ingested, rejected, batch count. 
### Step 3: Route Batches @router 
Receive the batch manifests from ingestion. Route each batch to the appropriate annotator pool. Report: routing summary by pool, any overflow alerts. 
### Step 4: AI Pre-Annotation @annotator 
Process all routed batches. Generate preference scores and rationales for all pairs. Mark pairs requiring human review. Abstain on low-confidence pairs. Report: annotation coverage, abstain rate, safety flags. 
### Step 5: Quality Verification @quality 
After human annotators complete their work, receive all annotated pairs. Compute Cohen's Kappa for all annotator pairs. Flag low-quality pairs and adversarial annotators. Report: batch quality summary, flagged pairs count, annotator flags. 
### Step 6: Consensus Arbitration @arbiter 
Receive quality-verified pairs. Resolve all disagreements. Produce final preference judgments. Export clean JSONL to GCS output path. Generate: final_pairs.jsonl + exclude_log.jsonl + pipeline_report.json. 
### Step 7: Final Report 
Print pipeline summary: 
- Total pairs in vs clean pairs out 
- Exclusion rate and reasons 
- Average confidence score 
- Annotator performance summary 
- GCS output paths
