import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai # type: ignore
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class ConsensusAgent:
    def __init__(self, config: dict):
        self.config = config
        self.model: Optional[Any] = None
        if HAS_GENAI:
            try:
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
                self.model = genai.GenerativeModel(
                    config["models"]["pro"],
                    system_instruction=self._system_prompt()
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize Arbiter GenAI model: {e}")

    def _system_prompt(self) -> str:
        return """You are the final decision-making agent in an RLHF data pipeline. You receive preference pairs with multiple human annotations and quality metrics. Your job is to produce the definitive, final preference judgment. Decision logic: 1. If majority human preference is clear (>= 60% agreement) -> use majority 2. If split 50/50 with high-quality annotators -> use AI pre-annotation as tiebreaker 3. If quality is low or pair is ambiguous -> EXCLUDE 4. If safety flag is set -> EXCLUDE unless clearly safe response wins unanimously EXCLUDE reason codes: - LOW_QUALITY: insufficient annotator agreement and low kappa - SENSITIVE: content requires domain review before inclusion - ADVERSARIAL: annotator manipulation suspected - AMBIGUOUS: both responses are genuinely equivalent — no signal value
Output ONLY valid JSON: { "final_preference": "A|B|EXCLUDE", "exclude_reason": "LOW_QUALITY|SENSITIVE|ADVERSARIAL|AMBIGUOUS|null", "decision_basis": "MAJORITY|AI_TIEBREAK|ARBITER_JUDGMENT", "confidence": 0.0-1.0, "provenance": { "human_votes": {"A": 0, "B": 0, "TIE": 0}, "ai_preference": "A|B|TIE|null", "ai_confidence": 0.0 } }"""

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def _call_api_with_retry(self, prompt: str) -> dict:
        if self.model is None:
            return {}
        response = self.model.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:-3]
        elif text.startswith("```"): text = text[3:-3]
        return json.loads(text)

    async def arbitrate(self, batches: list) -> list:
        logger.info(f"Arbitrating {len(batches)} batches.")
        final_pairs = []
        excluded_pairs = []
        
        for batch in batches:
            for pair in batch:
                human_votes = pair.get("human_votes", {})
                a_votes = human_votes.get("A", 0)
                b_votes = human_votes.get("B", 0)
                
                exclude_reason = None
                decision_basis = "MAJORITY"
                
                if pair.get("quality_flag") == "POOR":
                    exclude_reason = "LOW_QUALITY"
                    final_pref = "EXCLUDE"
                elif a_votes > b_votes:
                    final_pref = "A"
                elif b_votes > a_votes:
                    final_pref = "B"
                else:
                    # Tiebreak
                    decision_basis = "AI_TIEBREAK"
                    # Call Gemini Pro for tiebreak if model is available
                    result_json = None
                    if self.model is not None:
                        prompt = f"""Evaluate these two AI responses. PROMPT: {pair["prompt"]} RESPONSE A: {pair["response_a"]} RESPONSE B: {pair["response_b"]}"""
                        try:
                            result_json = self._call_api_with_retry(prompt)
                        except Exception as e:
                            logger.error(f"API error during tiebreak after retries: {e}")
                    
                    if result_json:
                        final_pref = result_json.get("final_preference", "EXCLUDE")
                        exclude_reason = result_json.get("exclude_reason")
                    else:
                        # Fallback if API fails
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
                        "kappa_score": pair.get("kappa_score"),
                        "annotator_ids": pair.get("annotator_ids", []),
                        "pipeline_version": self.config.get("pipeline", {}).get("version", "1.0.0")
                    },
                    "safety_flag": pair.get("safety_flag", False),
                    "exported_at": datetime.now(timezone.utc).isoformat()
                }
                
                if final_pref == "EXCLUDE":
                    excluded_pairs.append({
                        "id": pair["id"],
                        "exclude_reason": exclude_reason,
                        "kappa_score": pair.get("kappa_score"),
                        "human_votes": human_votes,
                        "excluded_at": final_pair["exported_at"]
                    })
                else:
                    final_pairs.append(final_pair)
                    
        # Export logs
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/exclude_log.jsonl", "w") as f:
            for p in excluded_pairs:
                f.write(json.dumps(p) + "\n")
                
        print(f"[Arbiter] Arbitration complete. {len(excluded_pairs)} excluded.")
        return final_pairs
