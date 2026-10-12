"""Plain-text catalog of the diagnostic knowledge base (CLI `list-diagnoses`)."""

from __future__ import annotations

from dedoc.models.diagnosis import Diagnosis

#: Preferred display order; unknown groups are appended in first-seen order.
_GROUP_ORDER = [
    "schema",
    "quality",
    "spark",
    "delta",
    "adf",
    "connectivity",
    "performance",
]

_GROUP_LABELS = {
    "schema": "Schema",
    "quality": "Data quality",
    "spark": "Spark",
    "delta": "Delta",
    "adf": "Azure Data Factory",
    "connectivity": "Connectivity",
    "performance": "Performance",
}


def _group_of(category: str) -> str:
    return category.split(".", 1)[0]


def _group_label(group: str) -> str:
    return _GROUP_LABELS.get(group, group.replace("_", " ").title())


def format_diagnosis_catalog(diagnoses: dict[str, Diagnosis]) -> str:
    """Render diagnoses grouped by category with human-readable names."""
    groups: dict[str, list[Diagnosis]] = {}
    for diagnosis in diagnoses.values():
        groups.setdefault(_group_of(diagnosis.category), []).append(diagnosis)

    order = [group for group in _GROUP_ORDER if group in groups]
    order += [group for group in groups if group not in order]

    lines = [f"Data Engineer Doctor — {len(diagnoses)} diagnosis definition(s)", ""]
    for group in order:
        members = groups[group]
        lines.append(f"{_group_label(group)} ({len(members)})")
        name_width = max(len(diagnosis.name) for diagnosis in members)
        for diagnosis in members:
            platforms = ", ".join(diagnosis.platforms)
            lines.append(
                f"  {diagnosis.id:<18} {diagnosis.name:<{name_width}}  "
                f"{diagnosis.severity.default.value:<8} {platforms}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()
