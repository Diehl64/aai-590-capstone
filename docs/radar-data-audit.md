# Candidate radar data audit

Status: documentation reviewed, real-data audit executed on 2026-10-21, and radar baseline/CNN evaluation completed. See [audit results](../results/radar-audit-results.md) and [model results](radar-model-results.md).

## Source evidence

- Record: https://zenodo.org/records/5896641 (v2.0; DOI 10.5281/zenodo.5896641).
- Schema: https://zenodo.org/records/5896641/files/ReadMe.txt?download=1
- Associated paper: https://doi.org/10.1109/RadarConf2248738.2022.9764194

Publisher reports 75,868 segments across 130 measurements from a 77 GHz FMCW sensor. The NumPy download is approximately 1.6 GB. Each segment has 1,280 complex values arranged as five range cells by 256 azimuth samples. Labels cover six drone types, bird categories, human motion, and a corner reflector. Metadata includes range, relative time, published split membership, and an edge indicator.

## Decisions to investigate

Propose drone/bird/person as a first coarse classification task, subject to actual class and recording counts. Exclude the reflector from that task with explicit accounting; do not call it an unknown-object benchmark. Preserve fine labels for analysis.

Use measurement IDs as candidate split groups. The audit found that all 130 measurements span multiple published splits: 128 span splits 1, 2, and 3, while measurement IDs 81 and 92 span only splits 1 and 3. The published partition therefore does not evaluate unseen measurements. Session/subject identity beyond measurement rows still needs investigation. Keep preprocessing fitting and threshold selection within training/validation data.

The documentation does not establish synchronized RGB/thermal observations or complete geographic 3D trajectories. Range alone is insufficient for map coordinates. Build any simulated association scenario separately and label it clearly.

## Open gates

License verified on 2026-10-21: the official Zenodo API identifies CC BY 4.0 (`metadata.license.id = cc-by-4.0`). See https://zenodo.org/api/records/5896641 and [saved source metadata](../results/radar-source-metadata.json). Credit Alexander Karlsson (KTH), cite https://doi.org/10.5281/zenodo.5896641, link https://creativecommons.org/licenses/by/4.0/, and identify modifications such as preprocessing or label regrouping. Do not imply publisher endorsement. This dataset license does not choose a license for our project code.

Validate checksum, array schema, counts, missing/nonfinite values, and class coverage in held-out groups. The audit and model runs use the verified real dataset. The loader requires explicit trust because this object array uses pickle.

See [the radar audit notebook](../notebooks/01_radar_data_audit.ipynb). No data is bundled with this repository.
