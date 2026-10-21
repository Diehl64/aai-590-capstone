# Candidate radar data audit

Status: documentation review only, 2026-10-20. Binary dataset not downloaded or executed.

## Source evidence

- Record: https://zenodo.org/records/5896641 (v2.0; DOI 10.5281/zenodo.5896641).
- Schema: https://zenodo.org/records/5896641/files/ReadMe.txt?download=1
- Associated paper: https://doi.org/10.1109/RadarConf2248738.2022.9764194

Publisher reports 75,868 segments across 130 measurements from a 77 GHz FMCW sensor. The NumPy download is approximately 1.6 GB. Each segment has 1,280 complex values arranged as five range cells by 256 azimuth samples. Labels cover six drone types, bird categories, human motion, and a corner reflector. Metadata includes range, relative time, published split membership, and an edge indicator.

## Decisions to investigate

Propose drone/bird/person as a first coarse classification task, subject to actual class and recording counts. Exclude the reflector from that task with explicit accounting; do not call it an unknown-object benchmark. Preserve fine labels for analysis.

Use measurement IDs as candidate split groups. Check whether the published split shares measurements; do not assume its evaluation design fits our question. Session/subject identity beyond measurement rows still needs investigation. Keep preprocessing fitting and threshold selection within training/validation data.

The documentation does not establish synchronized RGB/thermal observations or complete geographic 3D trajectories. Range alone is insufficient for map coordinates. Build any simulated association scenario separately and label it clearly.

## Open gates

License: unresolved. The retrieved record exposed a license heading without readable license terms. Confirm the actual license before training or redistributing data. Public availability alone is not permission.

Validate checksum, array schema, counts, missing/nonfinite values, and class coverage in held-out groups. Do not publish model results until the notebook runs on the real dataset. The loader requires explicit trust because this object array uses pickle.

See `notebooks/01_radar_data_audit.ipynb`. No data is bundled with this repository.
