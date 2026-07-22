class RouterAgent:
    def __init__(self, config: dict):
        self.config = config
        self.expert_domains = config.get("routing", {}).get("expert_domains", ["legal", "medical"])

    async def route(self, batches: list) -> list:
        print(f"[Router] Routing {len(batches)} batches.")
        routed_batches = []
        
        for batch in batches:
            routed_batch = []
            for pair in batch:
                domain = pair["domain"]
                
                # Routing logic
                if domain in self.expert_domains:
                    annotator_pool = "expert_sme"
                    min_annotators = 2
                elif domain in ["code", "math"]:
                    annotator_pool = "technical"
                    min_annotators = 1
                else:
                    annotator_pool = "crowdsource"
                    min_annotators = 1
                
                # Sensitive check heuristic
                prompt_lower = pair["prompt"].lower()
                if any(w in prompt_lower for w in ["violence", "adult", "pii", "secret"]):
                    annotator_pool = "restricted"
                    min_annotators = 1
                
                routed_pair = dict(pair)
                routed_pair["annotator_pool"] = annotator_pool
                routed_pair["min_annotators"] = min_annotators
                routed_pair["priority"] = "high" if pair["difficulty"] == "high" else "normal"
                routed_pair["routed_at"] = "2026-07-22T12:00:00Z"
                
                routed_batch.append(routed_pair)
            routed_batches.append(routed_batch)
            
        print(f"[Router] Routing complete.")
        return routed_batches
