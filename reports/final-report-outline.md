# AAI-590 Capstone Report Outline

## 1. Executive summary
- State the counter-UAS monitoring proof-of-concept goal.
- Explain that radar, thermal-IR, acoustic, and RF models are evaluated separately.
- Describe replay as simulated decision-support testing because the source datasets are not synchronized.
- State that every alert requires human/operator review and that the system does not control sensors or take autonomous action.

## 2. Problem and scope
- Describe the need to identify possible drone activity while avoiding unsupported operational claims.
- Define the project boundaries: no live sensor control, interception, field deployment, measured real-world sensor fusion, or combined detection-performance claim.
- Describe the human-in-the-loop decision requirement.

## 3. Data sources and provenance
- Describe each dataset separately: radar, thermal-IR, acoustic, and RF.
- Record licenses, access limits, split policies, and known dataset limitations.
- Explain why outputs from different datasets cannot be treated as synchronized observations.
- For RF, state that the dataset has no recording/session identifier and that exact duplicate-image checks cannot establish recording-level split independence.

## 4. Methods

### 4.1 Radar
- Describe the measurement-disjoint split and corner-reflector exclusion.
- Describe the nearest-centroid baseline and RadarCNN.
- State that saved held-out predictions are used for replay evidence.

### 4.2 Thermal-IR
- Describe the recording-disjoint export, Dataset 2 bird hard negatives, and Dataset 1 target-absent backgrounds.
- Describe Dataset 2-only, Dataset 1-only, transfer-learning, and balanced-joint experiments as separate designs.
- Explain the validation-selected or fixed operating threshold for each experiment.
- Document that Dataset 1 access/reuse terms remain subject to confirmation before publication beyond internal course review.
- State that only Dataset 2 supports bird-rejection claims and that the Dataset 2 baseline handoff is the replay input.

### 4.3 Acoustic
- Describe the independently evaluated acoustic model and held-out output format.
- Report the validation-selected operating point.
- Describe clean evaluation and controlled-noise robustness separately.
- Disclose that the DADS source/site label is unavailable, so the result does not establish new-site performance.

### 4.4 RF
- Describe v5 as the first-stage Machine screen and v4 as the stand-alone reference.
- Record the selected v5 configuration: weight 1.50, seed 42, Machine threshold 0.45, and validation-fitted temperature 1.2933.
- Define Machine as a mechanical/UAV-like RF cue, not a confirmed drone.
- Explain the validation selection rule and report the substantial Benign→Machine trade-off.
- Disclose that earlier exploratory test scores were viewed before the screen rule was written; the final test score is therefore not fully blind.
- Describe the 41 exact cross-split test duplicates and the sensitivity result after excluding them. State that this does not resolve unknown recording/session overlap.

## 5. Individual-model results
- Present radar metrics, confusion matrix, figures, and error analysis.
- Present thermal Dataset 2 baseline and balanced-joint results on their shared held-out test set; report Dataset 1 results separately as internal-source evidence.
- Include source-specific thermal error panels and explain that they are selected examples, not additional metrics.
- Present thermal provenance, license status, and limitations.
- Present acoustic results from committed artifacts, with clean and noise results separated.
- Present RF results from committed artifacts: test accuracy 0.8513, macro F1 0.8442, Machine recall 0.9050, and Machine precision 0.5586. Show that 249 of 400 Benign test images were called Machine.
- For RF, report the duplicate sensitivity result: after removing the 41 test images with byte-identical copies outside the test split, Machine recall is 0.9048 and the Benign→Machine/Machine→Benign counts remain 249/16. Keep the no-session-ID and prior-test-use caveats beside these figures.
- Keep all individual-model results separate; do not calculate a combined model score.

## 6. Simulated replay and operator review
- Describe the replay input contract and held-out-output validation.
- Include the RF four-sensor replay only after its branch is rebased, reviewed, and merged.
- Describe the 25 scenarios as software-behavior cases built by pairing independent saved outputs, not as real events.
- Cover agreement, disagreement, missing evidence, delayed evidence, low-quality evidence, RF false alarms/misses, and jamming.
- State that replay does not establish synchronized sensor fusion, combined detection accuracy, or operational detection performance.
- State that every alert requires human review.

## 7. Limitations, ethics, and risk controls
- Discuss dataset bias, split limitations, source/site generalization, and data-access constraints.
- Explain the RF exact-duplicate findings, the sensitivity check, the absence of session IDs, and the earlier exploratory test-set exposure.
- Explain the remaining radar session/subject/target-overlap limitation.
- Explain why simulated replay cannot prove operational performance.
- Describe privacy, safety, and human-review controls.

## 8. Conclusion and next steps
- Summarize validated component-model evidence without implying measured sensor fusion.
- Identify remaining work: rebase/review the RF replay branch, complete the four-sensor replay and agent comparison, perform a cross-model integrity review, and finish report/presentation source checks.
- Describe only approved future work, such as evaluation on suitably paired observations.
