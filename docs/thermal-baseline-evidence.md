# Reported thermal/IR baseline evidence

Jacob reported this Dataset 2-only thermal/IR baseline in the Group 1 Slack channel on 2026-11-02. The underlying code and artifacts are reported as pushed to GitHub, but the repository or pull-request link has not yet been provided to this shared capstone repository. The results below are therefore team-reported and awaiting source-artifact review.

## Dataset and task

- **Source:** [Drone Detection Dataset](https://github.com/DroneDetectionThesis/Drone-detection-dataset)
- **Subset:** Dataset 2 only
- **Task:** one-class object detection, where class `0` is `drone`
- **Positive examples:** drone frames with drone bounding boxes
- **Hard-negative examples:** bird frames retained with empty YOLO label files

The bird examples measure the operational error of incorrectly identifying a bird as a drone. The reported approach may later be assessed for extension to airplanes and helicopters; that extension has not been evaluated here.

## Reported preparation and evaluation

The reported pipeline:

- logs and excludes unreadable or zero-byte JPEG files;
- excludes positive frames with bounding boxes outside the image rather than clipping boxes;
- excludes positive frames with zero or negative bounding-box dimensions rather than converting them to no-drone examples;
- processes only the validated overlap of video frames and annotation entries when their lengths differ;
- uses recording-disjoint training, validation, and test splits; and
- samples every fifth eligible frame to reduce temporal duplication.

Training reportedly uses Mosaic augmentation only during training. It combines four training images and adjusts their boxes; it does not change raw source files or inference images.

## Reported held-out result

At a validation-selected threshold, the Batch-32 baseline reportedly achieved:

| Measure | Reported value |
| --- | ---: |
| Drone-present recall on held-out Dataset 2 test data | 97.44% |
| Bird false-positive rate on held-out Dataset 2 test data | 0.66% |

These values must not be treated as independently reproducible capstone results until the team records the code commit, environment/dependency specification, data-access and license evidence, exact split manifest, saved metrics, threshold-selection procedure, and held-out prediction outputs.

## Integration boundary

Dataset 2 is not synchronized with the RF, radar, or acoustic datasets. If reviewed artifacts are accepted, thermal outputs may be used only in the clearly labeled simulated local replay. They cannot establish measured real-time sensor-fusion performance.
