import json


def _check_type(value, schema_entry: dict, path: str) -> list[str]:
    errors: list[str] = []
    expected = schema_entry.get("type")

    if expected == "array":
        if not isinstance(value, list):
            errors.append(f"{path}: expected array, got {type(value).__name__}")
        else:
            items_schema = schema_entry.get("items", {})
            for i, item in enumerate(value):
                if items_schema:
                    item_type = items_schema.get("type")
                    if item_type == "string" and not isinstance(item, str):
                        errors.append(f"{path}[{i}]: expected string, got {type(item).__name__}")
                    elif item_type == "number" and not isinstance(item, (int, float)):
                        errors.append(f"{path}[{i}]: expected number, got {type(item).__name__}")
    elif expected == "object":
        if not isinstance(value, dict):
            errors.append(f"{path}: expected object, got {type(value).__name__}")
    elif expected == "string":
        if not isinstance(value, str):
            errors.append(f"{path}: expected string, got {type(value).__name__}")
        else:
            enum_vals = schema_entry.get("enum")
            if enum_vals and value not in enum_vals:
                errors.append(f"{path}: expected one of {enum_vals}, got '{value}'")
    elif expected == "number":
        if not isinstance(value, (int, float)):
            errors.append(f"{path}: expected number, got {type(value).__name__}")
        else:
            minimum = schema_entry.get("minimum")
            maximum = schema_entry.get("maximum")
            if minimum is not None and value < minimum:
                errors.append(f"{path}: {value} is less than minimum {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"{path}: {value} is greater than maximum {maximum}")

    return errors


def validate(data: dict, schema: dict) -> list[str]:
    errors: list[str] = []

    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"missing required field: '{field}'")

    addl = schema.get("additionalProperties", True)
    allowed = set(schema.get("properties", {}).keys())
    for key in data:
        if not addl and key not in allowed:
            errors.append(f"unexpected field: '{key}'")

    for key, prop_schema in schema.get("properties", {}).items():
        if key in data:
            errors.extend(_check_type(data[key], prop_schema, f"'{key}'"))

    return errors


def validate_or_fail(data: dict, schema: dict) -> dict:
    errors = validate(data, schema)
    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")
    return data


def load_schema(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
