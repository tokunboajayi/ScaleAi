// skills/ingestion.md
# Ingestion Agent Rules 
## Input Formats Accepted 
- JSON: { prompt, response_a, response_b } 
- CSV: columns [prompt, response_a, response_b] 
- Batch JSON: array of the above 
## Domain Classification Rules 
- code: contains code blocks, programming terms, technical syntax 
- legal: references laws, contracts, regulations, court decisions 
- medical: references symptoms, diagnoses, treatments, medications 
- math: contains equations, numerical reasoning, statistical analysis 
- general: everything else 
## Validation Rules 
- REJECT if prompt is empty or < 10 characters 
- REJECT if response_a or response_b is empty 
- REJECT if response_a == response_b (identical responses) 
- WARN if either response is < 20 characters (may be too short to evaluate) 
## Difficulty Scoring 
- low: prompt is simple, responses are short and clear 
- medium: prompt requires domain knowledge, multi-step reasoning 
- high: prompt requires expert judgment, complex reasoning, responses > 500 words 
## Output Schema (strict) 
{ "id": "uuid-v4", "prompt": "string", "response_a": "string", "response_b": "string", "domain": "code|legal|medical|math|general", "difficulty": "low|medium|high", "batch_id": "string", "ingested_at": "ISO-8601 timestamp", "validation_status": "valid|rejected|warned", "rejection_reason": "string|null" }
