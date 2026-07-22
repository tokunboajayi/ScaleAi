import json
import uuid
import datetime

class IngestionAgent:
    def __init__(self, config: dict):
        self.config = config
        self.domains = config.get("routing", {}).get("domains", ["code", "legal", "medical", "math", "general"])
        self.max_batch_size = config.get("routing", {}).get("max_batch_size", 500)

    def classify_domain(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["code", "function", "api", "bug"]): return "code"
        if any(w in prompt_lower for w in ["law", "court", "legal"]): return "legal"
        if any(w in prompt_lower for w in ["symptom", "doctor", "medical"]): return "medical"
        if any(w in prompt_lower for w in ["math", "equation", "calculate"]): return "math"
        return "general"

    def score_difficulty(self, prompt: str) -> str:
        if len(prompt) < 50: return "low"
        if len(prompt) < 200: return "medium"
        return "high"

    async def process(self, input_path: str) -> list:
        print(f"[Ingestion] Processing file {input_path}")
        batches = []
        current_batch = []
        batch_count = 0
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                
                try:
                    raw_pair = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                prompt = raw_pair.get("prompt", "")
                res_a = raw_pair.get("response_a", "")
                res_b = raw_pair.get("response_b", "")
                
                if len(prompt) < 10 or not res_a or not res_b or res_a == res_b:
                    continue # Reject based on validation rules
                
                processed_pair = {
                    "id": str(uuid.uuid4()),
                    "prompt": prompt,
                    "response_a": res_a,
                    "response_b": res_b,
                    "domain": self.classify_domain(prompt),
                    "difficulty": self.score_difficulty(prompt),
                    "batch_id": f"batch_{batch_count:03d}",
                    "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "validation_status": "valid"
                }
                
                current_batch.append(processed_pair)
                if len(current_batch) >= self.max_batch_size:
                    batches.append(current_batch)
                    batch_count += 1
                    current_batch = []
                    
        if current_batch:
            batches.append(current_batch)
            
        print(f"[Ingestion] Created {len(batches)} valid batches.")
        return batches
