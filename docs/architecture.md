# Architecture and governance

## Domain model

Each observation links a supplier, fab location, wafer diameter, monthly wafer-start capacity, supported process nodes, delivery performance, financial exposure and geopolitical risk. The service normalizes capacity to 300 mm-equivalent wafer starts and computes portfolio concentration.

## Risk model

The composite score is a weighted sum of five bounded components: geographic exposure, delivery reliability, financial exposure, technology dependency and data uncertainty. The API returns component scores, weights and reason codes so reviewers can challenge the result.

## Evidence governance

Every factual statement used in a brief must have an evidence identifier, source label and retrieval date. The deterministic brief generator refuses unknown evidence IDs. A production LLM may rewrite approved statements, but cannot add unsupported facts.

## Limitations

- Demo records are synthetic and unsuitable for procurement decisions.
- Risk weights express a policy choice and require stakeholder calibration.
- Public capacity estimates may be stale, rounded or incomparable.
- The model supports analyst judgment; it does not replace supplier due diligence.

