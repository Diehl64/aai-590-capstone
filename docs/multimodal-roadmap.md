# Multimodal capstone roadmap

## Locked scope claim

The capstone evaluates RF intrusion classification, 77 GHz radar micro-Doppler classification, thermal/vision feasibility for drone detection, and acoustic drone-sound detection. The datasets are not synchronized. Multisensor work is limited to an evidence-based comparison and local replay; it does not validate real-time sensor fusion or field performance.

## Work phases

1. **Individual evaluation.** Preserve a held-out test split and document metrics, limitations, provenance, and model version for each selected modality.
2. **Thermal/vision feasibility.** Assess whether the available thermal data and labels support a defensible drone-detection baseline. If not, report the limitation rather than expanding the scope.
3. **Evidence-based comparison.** Use saved model outputs only in explicitly simulated local-replay scenarios. Include agreement, disagreement, delayed, missing, and low-quality evidence cases. Mark every scenario and output as simulated.
4. **Operator review.** Present model evidence, uncertainty, verification status, and a human-review decision. Do not present a combined probability as a validated physical-world fusion result.

## Current state

Radar audit, measurement-disjoint split, nearest-centroid baseline, from-scratch RadarCNN, CUDA run, and radar replay states are complete. RF evaluation, thermal/vision feasibility, acoustic-model evidence review, evidence-based comparison, and report integration remain scheduled work. Lattice publishing remains outside the capstone scope.

## Decision gates

- Record dataset license, labels, recording-level split policy, and access before thermal/vision implementation.
- Keep synchronized multimodal datasets and Lattice integration outside this capstone unless the submitted plan is formally revised.
- Follow the dated owner and reviewer windows in the [project management plan](project-management-plan.md).
