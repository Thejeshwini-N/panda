from __future__ import annotations
from typing import Any, Dict, List, Tuple
import json
import os


def _normalized_levenshtein(a: str, b: str) -> float:
	if a == b:
		return 1.0
	if not a or not b:
		return 0.0
	len_a = len(a)
	len_b = len(b)
	# Classic DP
	dp = list(range(len_b + 1))
	for i, ca in enumerate(a, start=1):
		prev = i
		for j, cb in enumerate(b, start=1):
			cost = 0 if ca == cb else 1
			cur = min(
				dp[j] + 1,      # deletion
				prev + 1,       # insertion
				dp[j - 1] + cost  # substitution
			)
			dp[j - 1] = prev
			prev = cur
		dp[len_b] = prev
	# distance is dp[len_b]
	dist = dp[len_b]
	max_len = max(len_a, len_b)
	return 1.0 - (dist / max_len)


def _list_similarity(list_a: List[Any], list_b: List[Any]) -> float:
	if not list_a and not list_b:
		return 1.0
	if not list_a or not list_b:
		return 0.0
	# pairwise best matching by position with bounds
	length = min(len(list_a), len(list_b))
	scores: List[float] = []
	for i in range(length):
		a = list_a[i]
		b = list_b[i]
		if isinstance(a, str) and isinstance(b, str):
			scores.append(_normalized_levenshtein(a, b))
		else:
			scores.append(1.0 if a == b else 0.0)
	return sum(scores) / len(scores) if scores else 0.0


def _value_similarity(a: Any, b: Any) -> float:
	if isinstance(a, str) and isinstance(b, str):
		return _normalized_levenshtein(a, b)
	if isinstance(a, list) and isinstance(b, list):
		return _list_similarity(a, b)
	if isinstance(a, dict) and isinstance(b, dict):
		# average over union of keys
		keys = set(a.keys()) | set(b.keys())
		if not keys:
			return 1.0
		s = 0.0
		for k in keys:
			s += _value_similarity(a.get(k), b.get(k))
		return s / len(keys)
	return 1.0 if a == b else 0.0


def generate_plagiarism_report(original_json: str | None, synthetic_json: str | None) -> Dict[str, Any]:
	"""Compute similarity between original and synthetic params.

	Returns dict with overall score (0..1), per-field scores, and flags.
	"""
	report: Dict[str, Any] = {
		"has_original": bool(original_json),
		"has_synthetic": bool(synthetic_json),
		"overall_similarity": None,
		"per_field": {},
		"risk_level": None
	}
	if not original_json or not synthetic_json:
		report["overall_similarity"] = None
		report["risk_level"] = "unknown"
		return report
	try:
		orig = json.loads(original_json)
		synth = json.loads(synthetic_json)
	except Exception:
		report["overall_similarity"] = None
		report["risk_level"] = "invalid_json"
		return report

	if not isinstance(orig, dict) or not isinstance(synth, dict):
		score = _value_similarity(orig, synth)
		report["overall_similarity"] = round(score, 4)
		report["risk_level"] = _risk_from_score(score)
		return report

	# per-field comparison
	keys = set(orig.keys()) | set(synth.keys())
	per_field: Dict[str, float] = {}
	for k in keys:
		per_field[k] = round(_value_similarity(orig.get(k), synth.get(k)), 4)
	report["per_field"] = per_field
	overall = sum(per_field.values()) / len(per_field) if per_field else 0.0
	report["overall_similarity"] = round(overall, 4)
	report["risk_level"] = _risk_from_score(overall)
	return report


def _risk_from_score(score: float) -> str:
	if score >= 0.9:
		return "high"
	if score >= 0.7:
		return "medium"
	return "low"


def save_report(request_id: int, report: Dict[str, Any]) -> str:
	"""Save report JSON under storage/requests/{id}/plagiarism_report.json and return path."""
	output_dir = os.path.join("storage", "requests", str(request_id))
	os.makedirs(output_dir, exist_ok=True)
	path = os.path.join(output_dir, "plagiarism_report.json")
	with open(path, "w", encoding="utf-8") as f:
		json.dump(report, f, ensure_ascii=False, indent=2)
	return path


def load_report(request_id: int) -> Dict[str, Any] | None:
	path = os.path.join("storage", "requests", str(request_id), "plagiarism_report.json")
	if not os.path.exists(path):
		return None
	try:
		with open(path, "r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		return None
