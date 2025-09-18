from typing import Any, Dict, List
import json
import os
import random
from faker import Faker


_fake = Faker()


def _mask_name_list(names: List[str]) -> List[str]:
	return [_fake.name() for _ in names]


def _mask_country_list(countries: List[str]) -> List[str]:
	# Keep a pool of common countries and ensure variation
	country_pool = [
		"USA", "India", "Brazil", "Mexico", "Canada", "Germany", "France",
		"Spain", "Italy", "Australia", "Japan", "South Korea", "UK", "Netherlands",
		"Sweden", "Norway", "Denmark", "Finland", "China", "South Africa"
	]
	return [random.choice(country_pool) for _ in countries]


def _mask_generic_value(value: Any) -> Any:
	if isinstance(value, str):
		# Replace strings with random words of similar length
		return _fake.word()
	if isinstance(value, (int, float)):
		return value  # keep numeric constraints
	if isinstance(value, list):
		return [_mask_generic_value(v) for v in value]
	if isinstance(value, dict):
		return {k: _mask_generic_value(v) for k, v in value.items()}
	return value


def generate_synthetic_params(params_json: str | None) -> str | None:
	"""Generate a synthetic version of the request params JSON string.

	- Masks known PII-like fields such as 'name' and 'country' when they are lists.
	- Falls back to generic masking for other structures.
	- Returns a JSON string or None if input is None/empty/invalid.
	"""
	if not params_json:
		return None
	try:
		params = json.loads(params_json)
	except (json.JSONDecodeError, TypeError):
		return None

	if not isinstance(params, dict):
		return None

	synthetic: Dict[str, Any] = {}
	for key, value in params.items():
		key_lower = key.lower()
		if key_lower == "name" and isinstance(value, list):
			synthetic[key] = _mask_name_list(value)
		elif key_lower == "country" and isinstance(value, list):
			synthetic[key] = _mask_country_list(value)
		else:
			synthetic[key] = _mask_generic_value(value)

	return json.dumps(synthetic)


def save_original_params(request_id: int, params_json: str | None) -> None:
	"""Persist original params JSON to `storage/requests/{id}/original_params.json`."""
	if not params_json:
		return
	try:
		# validate JSON before saving
		json.loads(params_json)
	except Exception:
		return
	output_dir = os.path.join("storage", "requests", str(request_id))
	os.makedirs(output_dir, exist_ok=True)
	file_path = os.path.join(output_dir, "original_params.json")
	with open(file_path, "w", encoding="utf-8") as f:
		f.write(params_json)


def load_original_params(request_id: int) -> str | None:
	"""Load original params JSON if available, else None."""
	file_path = os.path.join("storage", "requests", str(request_id), "original_params.json")
	if os.path.exists(file_path):
		try:
			with open(file_path, "r", encoding="utf-8") as f:
				return f.read()
		except Exception:
			return None
	return None
