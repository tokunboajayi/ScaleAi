// skills/quality.md
# Quality Verifier Agent Rules 
## Cohen's Kappa Thresholds 
- >= 0.80: Excellent agreement — pass directly to arbiter 
- 0.65-0.79: Good agreement — pass with quality_flag = GOOD 
- 0.41-0.64: Fair agreement — flag for re-annotation 
- 0.21-0.40: Poor agreement — flag + review annotator performance 
- <= 0.20: Very poor — exclude pair, flag annotators 
## Adversarial Detection Rules 
- Flag annotator if Kappa < 0.40 on 3+ consecutive batches 
- Flag annotator if calibration set accuracy < 70% 
- Flag annotator if annotation time < 8 seconds per pair (speed-clicking) 
- Flagged annotators are suspended pending human review 
## Calibration Set Protocol 
- Every batch includes 5% calibration pairs with known correct answers 
- Calibration pairs are indistinguishable from real pairs 
- Annotator must score >= 70% on calibration to stay in pool 
- Calibration results are never disclosed to annotators 
## Sanity Check: AI vs Human Agreement 
- If human preference consistently opposes ai_preference with high ai_confidence, flag the batch for pipeline review — may indicate domain-specific AI bias
