# Experiment results

Commit selected figures and small, non-sensitive metric tables here after experiments run. Keep large artifacts and model weights in documented external storage. `.keras` files stay out of git.

The RF notebook writes its outputs to `results/rf-intrusion/`, including `run_config.json` (chosen weight, threshold, temperature, seed, and selection rule). Colab deletes `/content`, so download the results zip before the runtime stops. Commit the small files from that folder and leave the `.keras` weights untracked.

For each result, record the source commit, configuration, model version, data version and split, random seed, hardware, and whether the result is measured or simulated. Do not populate results with invented numbers. Explain denominators for all rates and report limitations when estimating performance from few independent recordings.
