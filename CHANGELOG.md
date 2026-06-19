# Changelog

## 0.3.0

- Make PDDL source order the default determinization order.
- Add named `source`, `probability-desc`, `effect-count-desc`, and
  `effect-count-asc` ranking strategies.
- Add the numeric `-r MODE` / `--ranking MODE` CLI (`0` through `3`), with
  source order as mode `0` and the default.
- Rank complete probability-based determinizations by joint probability.
- Calculate and retain implicit residual/no-op outcomes from the PPDDL model.
- Validate probabilistic blocks and retain full fraction precision while
  parsing probabilities.
