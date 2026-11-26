# AAI-590 Presentation Outline

This outline is a presentation-planning aid. It uses only committed component evidence and simulated replay artifacts. The final deck must retain the project boundaries in the claims-and-evidence matrix.

| Slide | Purpose | Suggested visualization or evidence | Required boundary |
| --- | --- | --- | --- |
| 1 | Problem, team, and goal | Human-in-the-loop counter-UAS monitoring concept | Offline proof of concept; no live deployment. |
| 2 | Scope and evidence model | Four independently evaluated modalities feeding a simulated replay diagram | Datasets are not synchronized. |
| 3 | Radar method and result | RadarCNN held-out metrics and confusion matrix | Component metric only; grouped split limitation. |
| 4 | Thermal method and result | Dataset 2 held-out recall and bird false-positive result | Dataset 2-only bird-rejection claim. |
| 5 | Acoustic method and result | Clean operating point plus separately labeled noise result | No source/site generalization claim. |
| 6 | RF method and result | Validation-selection trade-off and selected test confusion matrix | `Machine` is a cue, not a confirmed drone. |
| 7 | Integrity and limitations | Split/provenance limitations by modality | Do not hide duplicate, source/site, or access limitations. |
| 8 | Saved-output simulated replay | Scenario-evidence-status matrix | Not measured sensor fusion or combined accuracy. |
| 9 | Human review and coordination interface | Alert states: confirmed, conflicting, unverified, unknown | Every alert requires human review; no fused probability. |
| 10 | Agent comparison status | Fixed-rule versus cascade plan; add results only after PR #57 is merged | Do not imply the comparison is complete before its committed run exists. |
| 11 | Conclusion and next steps | Evidence-supported contributions and remaining validation work | No autonomous decision, field-readiness, or operational-performance claim. |

## Speaking and submission checks

- Assign at least two speaking minutes to each of the three team members.
- Use at least eight substantive visualizations; captions must identify the source artifact and whether evidence is component-level or simulated replay.
- Rehearse from the final slide deck, not from a separately edited draft.
- Before recording, verify all numbers against `reports/claims-evidence-matrix.md` and `docs/cross-model-integrity-review.md`.
