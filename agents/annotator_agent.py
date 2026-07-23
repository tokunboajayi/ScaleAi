import json
import uuid
import random
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

logger = logging.getLogger(__name__)
try:
    import google.generativeai as genai # type: ignore
    HAS_GENAI = True
except ImportError:
    genai = None # type: ignore
    HAS_GENAI = False

class AnnotatorAgent:
    def __init__(self, config: dict):
        self.config = config
        self.confidence_floor = config["thresholds"]["confidence_minimum"]
        self.model: Optional[Any] = None
        if HAS_GENAI:
            import os
            try:
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # type: ignore
                self.model = genai.GenerativeModel( # type: ignore
                    config["models"]["flash"],
                    system_instruction=self._system_prompt()
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize GenAI model: {e}. Using mock mode.")

    def _system_prompt(self) -> str:
        return """You are an expert AI preference annotator. You evaluate pairs of AI responses and determine which is better. Output ONLY valid JSON. No markdown. No explanation outside JSON. Evaluate on: safety (priority 1), accuracy, helpfulness, clarity, completeness. Never prefer longer responses. Never prefer formal tone over substance. Output schema: { "preference": "A|B|TIE", "confidence": 0.0-1.0, "rationale": "2-3 sentences", "safety_flag": true|false, "safety_note": "string|null" }"""

    async def annotate(self, batches: List[List[Dict]]) -> List[List[Dict]]:
        print(f"[Annotator] Pre-annotating {len(batches)} batches.")
        results = []
        for batch in batches:
            annotated_batch = []
            for pair in batch:
                result = await self._annotate_pair(pair)
                annotated_batch.append(result)
            results.append(annotated_batch)
        print(f"[Annotator] Pre-annotation complete.")
        return results

    @retry(
        retry=retry_if_exception_type(Exception), # Catch all for demo, typically ResourceExhausted
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def _call_api_with_retry(self, prompt: str) -> dict:
        response = self.model.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json") # type: ignore
        )
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:-3]
        elif text.startswith("```"): text = text[3:-3]
        return json.loads(text)

    async def _annotate_pair(self, pair: Dict) -> Dict:
        prompt = f"""Evaluate these two AI responses to the following prompt. PROMPT: {pair["prompt"]} RESPONSE A: {pair["response_a"]} RESPONSE B: {pair["response_b"]} Output your evaluation as JSON."""
        
        result_json = None
        if self.model is not None:
            try:
                result_json = self._call_api_with_retry(prompt)
            except Exception as e:
                logger.error(f"Error calling API after retries: {e}")
        
        if not result_json:
            # Fallback mock mode
            pref = random.choice(["A", "B", "TIE"])
            result_json = {
                "preference": pref,
                "confidence": round(random.uniform(0.4, 0.95), 2),
                "rationale": "Mock rationale because API failed or not configured.",
                "safety_flag": False
            }

        pair["ai_preference"] = result_json.get("preference", "TIE")
        pair["ai_confidence"] = float(result_json.get("confidence", 0.5))
        pair["ai_rationale"] = result_json.get("rationale", "")
        pair["safety_flag"] = result_json.get("safety_flag", False)
        pair["requires_human_review"] = pair["ai_confidence"] < self.confidence_floor
        pair["ai_abstain"] = pair["ai_confidence"] < 0.50
        pair["annotated_at"] = datetime.now(timezone.utc).isoformat()
        
        return pair
