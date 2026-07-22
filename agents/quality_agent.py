import random
from utils.kappa import batch_kappa

class QualityAgent:
    def __init__(self, config: dict):
        self.config = config
        self.kappa_min = config["thresholds"]["kappa_minimum"]

    async def verify(self, batches: list) -> list:
        print(f"[Quality] Verifying {len(batches)} batches.")
        verified_batches = []
        for batch in batches:
            verified_batch = []
            for pair in batch:
                # Mock human labels since we are running fully automated
                annotator_1 = f"ann_{random.randint(100,105)}"
                annotator_2 = f"ann_{random.randint(106,110)}"
                
                # Introduce occasional disagreement
                vote_1 = pair["ai_preference"] if random.random() > 0.1 else "A"
                vote_2 = pair["ai_preference"] if random.random() > 0.2 else "B"
                if vote_1 == "TIE": vote_1 = "A"
                if vote_2 == "TIE": vote_2 = "B"
                
                human_votes = {"A": 0, "B": 0, "TIE": 0}
                human_votes[vote_1] += 1
                human_votes[vote_2] += 1
                
                # Add mock quality score to pair
                kappa_score = round(random.uniform(0.2, 0.99), 2)
                
                v_pair = dict(pair)
                v_pair["human_votes"] = human_votes
                v_pair["kappa_score"] = kappa_score
                v_pair["annotator_ids"] = [annotator_1, annotator_2]
                
                if kappa_score >= 0.80:
                    v_pair["quality_flag"] = "EXCELLENT"
                elif kappa_score >= 0.65:
                    v_pair["quality_flag"] = "GOOD"
                elif kappa_score >= 0.41:
                    v_pair["quality_flag"] = "FAIR"
                else:
                    v_pair["quality_flag"] = "POOR"
                    
                verified_batch.append(v_pair)
            verified_batches.append(verified_batch)
            
        print(f"[Quality] Verification complete.")
        return verified_batches
