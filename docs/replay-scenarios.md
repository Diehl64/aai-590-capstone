# Local replay scenarios

The four scenarios in `src/run_replay_scenarios.py` exercise the local event contract without claiming paired real-world imagery or ground truth. Each output is marked `simulated: true` and is separate from the radar model metrics.

| Scenario | Expected review state | Meaning |
| --- | --- | --- |
| Agreement | accepted | Simulated verification class matches the radar result. |
| Conflict | required | Simulated evidence disagrees; an operator must decide. |
| Timeout | required | No verification arrived before the deadline. |
| Unavailable | required | No verification result was received. |

Run from the repository root:

```powershell
python src/run_replay_scenarios.py --output results/replay-scenarios
```

The generated JSON records event IDs, model version, evidence references, reasons, and review state. It does not establish classifier truth, calibration, location, continuous detection rates, or deployment readiness.
