# AAI-590 Capstone Report Outline

## 1. Executive summary
- State the counter-UAS monitoring proof-of-concept goal.
- Explain that radar, thermal-IR, acoustic, and RF evidence are evaluated separately.
- State that replay scenarios are simulated because source datasets are not synchronized.
- State that every alert requires human/operator review.

## 2. Problem and scope
- Describe the need to detect possible drone activity while avoiding unsupported operational claims.
- Define the project boundaries: no live sensor control, interception, field deployment, or measured real-world sensor fusion.
- Describe the human-in-the-loop decision requirement.

## 3. Data sources and provenance
- Describe each dataset separately: radar, thermal-IR, acoustic, and RF.
- Record licenses, access limits, split policies, and known dataset limitations.
- Explain why outputs from different datasets cannot be treated as synchronized observations.

## 4. Methods
### 4.1 Radar
- Describe the measurement-disjoint split and corner-reflector exclusion.
- Describe the nearest-centroid baseline and RadarCNN.
- State that saved held-out predictions are used for replay evidence.

### 4.2 Thermal-IR
- Describe the recording-disjoint export, Dataset 2 bird hard negatives, and Dataset 1 target-absent backgrounds.
- Describe the Dataset 2-only baseline, Dataset 1-only, transfer-learning, and balanced-joint experiments as separate designs.
- Explain the validation-selected or fixed operating threshold for each experiment.
- Document that Dataset 1 access/reuse terms remain subject to confirmation before publication beyond internal course review.
- State that only Dataset 2 supports bird-rejection claims and that the Dataset 2 baseline handoff is the replay input.

### 4.3 Acoustic
- Describe the independently evaluated acoustic model and held-out output format.
- Document the selected operating point only after validation-based threshold confirmation.
- Describe clean evaluation and controlled-noise robustness separately.

### 4.4 RF
- Describe the v4 versus v5 comparison after the official selected checkpoint, threshold, and class semantics are confirmed.
- Do not describe raw model scores as calibrated confidence without calibration evidence.

## 5. Individual-model results
- Present radar metrics, confusion matrix, figures, and error analysis.
- Present thermal Dataset 2 baseline and balanced-joint results on their shared held-out test set; report thermal Dataset 1 results separately as internal-source evidence.
- Include source-specific thermal error panels and explain that they are selected examples, not additional metrics.
- Present thermal provenance, license status, and limitations.
- Present acoustic and RF results only from committed, reproducible artifacts.
- Keep all individual-model results separate.

## 6. Simulated replay and operator review
- Describe the replay input contract and held-out-output validation.
- Explain that scenarios are explicitly simulated.
- Cover agreement, disagreement, missing evidence, delayed evidence, and low-quality evidence.
- State that replay does not establish synchronized sensor fusion or combined detection accuracy.
- State that every alert requires human review.

## 7. Limitations, ethics, and risk controls
- Discuss dataset bias, split limitations, source/site generalization, and data-access constraints.
- Explain the remaining radar session/subject/target-overlap limitation.
- Explain why simulated replay cannot prove operational performance.
- Describe privacy, safety, and human-review controls.

## 8. Conclusion and next steps
- Summarize validated component-model evidence.
- Identify remaining integration blockers.
- Describe only approved future work, such as evaluation on suitably paired observations.
