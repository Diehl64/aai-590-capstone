# Reusable Python source

Add reusable data processing, training, evaluation, or integration code here when implemented. Introduce modules based on actual requirements rather than empty placeholder functions. Document their configuration, dependencies, inputs, outputs, and relevant checks.

Reusable implementation currently includes the radar baseline, from-scratch CNN, and the local replay/operator-review contract. Keep model and replay inputs, outputs, versions, and validation evidence documented as they evolve.

`rf_duplicate_sensitivity.py` rescores the committed RF held-out CSV without the test images that have a byte-identical copy in another split. It reads only committed files, retrains nothing, and writes `results/rf-intrusion/rf_v5_test_duplicate_sensitivity.json`. Run it from the repository root with `python src/rf_duplicate_sensitivity.py`.

`agent_interface.py` is the coordination agent: it maps each sensor label to a shared hypothesis, applies the status rules, and recommends which sensors to request next. Tests are in `tests/test_agent_interface.py`. See `docs/agent-coordination.md`.
