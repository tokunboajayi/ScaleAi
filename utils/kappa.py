# utils/kappa.py
from collections import defaultdict
from itertools import combinations

def cohens_kappa(labels_a: list, labels_b: list) -> float:
    """Compute Cohen's Kappa between two annotators."""
    assert len(labels_a) == len(labels_b), "Label lists must be same length"
    n = len(labels_a)
    if n == 0:
        return 0.0
    
    # Observed agreement
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    
    # Expected agreement by chance
    categories = set(labels_a + labels_b)
    expected = sum( (labels_a.count(c) / n) * (labels_b.count(c) / n) for c in categories )
    
    if expected == 1.0:
        return 1.0
        
    return (observed - expected) / (1 - expected)


def batch_kappa(annotations: list[dict]) -> dict:
    """
    annotations: list of {"annotator_id": str, "pair_id": str, "label": str}
    Returns kappa scores per annotator pair.
    """
    by_annotator = defaultdict(dict)
    for ann in annotations:
        by_annotator[ann["annotator_id"]][ann["pair_id"]] = ann["label"]
        
    annotators = list(by_annotator.keys())
    kappa_scores = {}
    
    for a, b in combinations(annotators, 2):
        shared_pairs = set(by_annotator[a]) & set(by_annotator[b])
        if len(shared_pairs) < 5: # Need minimum overlap
            continue
        labels_a = [by_annotator[a][p] for p in shared_pairs]
        labels_b = [by_annotator[b][p] for p in shared_pairs]
        kappa_scores[f"{a}_vs_{b}"] = cohens_kappa(labels_a, labels_b)
        
    return kappa_scores
