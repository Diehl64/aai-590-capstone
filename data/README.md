# Data documentation

No dataset is bundled with the scaffold. Add one row per actual source to `dataset-manifest.csv` after verification. Record the source version, download instructions, license/permission, classes, modality, recording/group identifier, and checksums as appropriate.

Store local raw, interim, and processed data under the ignored directories `data/raw/`, `data/interim/`, and `data/processed/`, or use documented external storage. Commit small non-sensitive metadata only when permitted.

Document split construction, related recordings, duplicates, exclusions, transformations, and preprocessing fitted on training data. Treat paired observations as paired only when their shared event identity and timing are known. Obtain permission before redistributing any dataset.
