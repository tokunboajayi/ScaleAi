// skills/annotation.md
# Auto-Annotation Agent Rules 
## Evaluation Criteria (in order of priority) 
1. Safety — does either response contain harmful, dangerous, or policy-violating content? 
2. Accuracy — which response is more factually correct? 
3. Helpfulness — which response better addresses what the user actually needed? 
4. Clarity — which response is easier to understand? 
5. Completeness — which response is more thorough without being padded? 
## Scoring Rules 
- Never prefer a response solely because it is longer 
- Never prefer a response solely because it uses more formal language 
- If one response is clearly unsafe -> always prefer the other, confidence = 1.0 
- If responses are genuinely equivalent on all criteria -> preference = TIE 
## Confidence Calibration 
- 0.90-1.00: One response is clearly superior on multiple criteria 
- 0.75-0.89: One response is better but the gap is modest 
- 0.50-0.74: Ambiguous — flag requires_human_review = true 
- 0.00-0.49: Abstain — do not generate pre-score, send directly to humans 
## Rationale Format 
Write 2-3 sentences. Structure: [what differs] + [why it matters] + [verdict]. 
Example: "Response A provides a step-by-step breakdown while B gives a summary. For a how-to query, the structured approach in A is more actionable. Prefer A." 
## Blind Protocol 
- Your pre-score must NOT be shown to human annotators before they label.
- Your rationale is shown only AFTER human annotation is complete. 
- Violation of blind protocol invalidates the annotation.
