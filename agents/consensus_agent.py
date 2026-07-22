import json
from datetime import datetime, timezone
import os

class ConsensusAgent:
    def __init__(self, config: dict):
        self.config = config

    async def arbitrate(self, batches: list) -> list:
        print(f"[Arbiter] Arbitrating {len(batches)} batches.")
        final_pairs = []
        excluded_pairs = []
        
        for batch in batches:
            for pair in batch:
                human_votes = pair.get("human_votes", {})
                a_votes = human_votes.get("A", 0)
                b_votes = human_votes.get("B", 0)
                
                exclude_reason = None
                decision_basis = "MAJORITY"
                
                if pair["quality_flag"] == "POOR":
                    exclude_reason = "LOW_QUALITY"
                    final_pref = "EXCLUDE"
                elif a_votes > b_votes:
                    final_pref = "A"
                elif b_votes > a_votes:
                    final_pref = "B"
                else:
                    # Tiebreak
                    decision_basis = "AI_TIEBREAK"
                    final_pref = pair["ai_preference"]
                    if final_pref == "TIE":
                        exclude_reason = "AMBIGUOUS"
                        final_pref = "EXCLUDE"
                        
                final_pair = {
                    "id": pair["id"],
                    "prompt": pair["prompt"],
                    "response_a": pair["response_a"],
                    "response_b": pair["response_b"],
                    "domain": pair["domain"],
                    "difficulty": pair["difficulty"],
                    "final_preference": final_pref,
                    "decision_basis": decision_basis,
                    "confidence": pair["ai_confidence"] if decision_basis == "AI_TIEBREAK" else 1.0,
                    "provenance": {
                        "human_votes": human_votes,
                        "ai_preference": pair["ai_preference"],
                        "ai_confidence": pair["ai_confidence"],
                        "kappa_score": pair["kappa_score"],
                        "annotator_ids": pair["annotator_ids"],
                        "pipeline_version": self.config.get("pipeline", {}).get("version", "1.0.0")
                    },
                    "safety_flag": pair["safety_flag"],
                    "exported_at": datetime.now(timezone.utc).isoformat()
                }
                
                if final_pref == "EXCLUDE":
                    excluded_pairs.append({
                        "id": pair["id"],
                        "exclude_reason": exclude_reason,
                        "kappa_score": pair["kappa_score"],
                        "human_votes": human_votes,
                        "excluded_at": final_pair["exported_at"]
                    })
                else:
                    final_pairs.append(final_pair)
                    
        # Export logs directly here for simplicity
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/exclude_log.jsonl", "w") as f:
            for p in excluded_pairs:
                f.write(json.dumps(p) + "\n")
                
        print(f"[Arbiter] Arbitration complete. {len(excluded_pairs)} excluded.")
        return final_pairs
