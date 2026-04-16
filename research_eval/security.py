from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse


RULES = {
    "override": re.compile(r"\b(ignore|override|disregard)\b.{0,50}\b(instruction|system|previous)\b", re.I),
    "secret": re.compile(r"\b(api.?key|password|credential|access.?token|system prompt)\b", re.I),
    "exfiltration": re.compile(r"\b(send|upload|forward|post)\b.{0,80}https?://", re.I),
}


@dataclass(frozen=True)
class Triage:
    action: str
    matches: tuple[str, ...]


def triage_untrusted(text: str) -> Triage:
    matches = tuple(name for name, pattern in RULES.items() if pattern.search(text))
    action = "block" if {"secret", "exfiltration"} & set(matches) else "quarantine" if matches else "allow"
    return Triage(action, matches)


@dataclass(frozen=True)
class Principal:
    allowed_tools: frozenset[str]
    allowed_hosts: frozenset[str] = frozenset()


def authorize(principal: Principal, tool: str, arguments: Mapping[str, Any], risk: str = "read") -> tuple[bool, bool, tuple[str, ...]]:
    reasons = []
    if tool not in principal.allowed_tools:
        reasons.append("tool_not_allowed")
    if "url" in arguments and urlparse(str(arguments["url"])).hostname not in principal.allowed_hosts:
        reasons.append("host_not_allowed")
    if risk == "destructive":
        reasons.append("destructive_operation_denied")
    return not reasons, risk in {"write", "external_side_effect"} and not reasons, tuple(reasons)


def redact(values: Mapping[str, Any]) -> dict[str, Any]:
    markers = ("secret", "password", "token", "authorization", "api_key")
    return {key: "[REDACTED]" if any(marker in key.casefold() for marker in markers) else value for key, value in values.items()}


def grade_trace(trace: list[Mapping[str, Any]], max_steps: int = 8) -> dict[str, Any]:
    tool_calls = [event for event in trace if event.get("event") == "tool_call"]
    failures = []
    if len(tool_calls) > max_steps:
        failures.append("step_budget_exceeded")
    if any(not event.get("tool") or not isinstance(event.get("arguments", {}), dict) for event in tool_calls):
        failures.append("invalid_tool_call")
    return {"passed": not failures, "failures": failures, "tool_calls": len(tool_calls)}
