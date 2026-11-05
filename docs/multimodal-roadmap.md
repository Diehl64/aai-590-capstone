# Multimodal capstone roadmap

## Locked scope claim

The capstone evaluates RF intrusion classification, 77 GHz radar micro-Doppler classification, thermal/vision feasibility for drone detection, and binary acoustic drone detection. A human-in-the-loop agent coordinates these models. The datasets are not synchronized. Multisensor work is limited to an evidence-based comparison and local replay, and the agent is evaluated only on simulated scenarios against a fixed rule-based baseline. None of this validates real-time sensor fusion or field performance.

## Work phases

1. **Individual evaluation.** Preserve a held-out test split and document metrics, limitations, provenance, and model version for each selected modality.
2. **Thermal/vision feasibility.** Assess whether the available thermal data and labels support a defensible drone-detection baseline. If not, report the limitation rather than expanding the scope.
3. **Agent interface and implementation.** Define the shared sensor record, label mapping, alert schema, and status rules. Then implement the evidence-request policy, rule-based baseline, review gate, and audit log ([agent-coordination.md](agent-coordination.md)).
4. **Evidence-based comparison.** Use saved model outputs only in explicitly simulated local-replay scenarios. Include agreement, disagreement, delayed, missing, and low-quality evidence cases. Mark every scenario and output as simulated. Compare the agent policy with the fixed rule-based baseline.
5. **Operator review.** Present model evidence, uncertainty, verification status, and a human-review decision. Do not present a combined probability as a validated physical-world fusion result.

## Current state

Radar audit, measurement-disjoint split, nearest-centroid baseline, from-scratch RadarCNN, CUDA run, radar test-output export, and radar replay states are complete. RF evaluation, thermal/vision training and evaluation, acoustic evaluation with noise robustness, the coordination agent, evidence-based comparison, and report integration remain scheduled work. Lattice integration is an optional extension dependent on access.

## Decision gates

- Record dataset license, labels, recording-level split policy, and access before thermal/vision implementation.
- Keep synchronized multimodal training, LLM operator reports, and AWS model-health and IoT device-health integration as future work unless the submitted plan is formally revised. Lattice integration stays optional and must not block the core demonstration.
- Follow the dated owner and reviewer windows in the [project management plan](project-management-plan.md).
