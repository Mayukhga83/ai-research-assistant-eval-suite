# Add rate limit handling and bounded retries

**Reconstructed study session:** 2026-04-04

## Purpose

Add rate limit handling and bounded retries as an auditable component of the research-assistant evaluation framework.

## Acceptance criteria

- The change has a deterministic local verification path.
- Inputs and outputs use versioned, provider-neutral contracts.
- Failures preserve enough context for case-level diagnosis.
- No benchmark or model-quality result is claimed without recorded evidence.
