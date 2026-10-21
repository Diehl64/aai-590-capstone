# Contributing

## Normal workflow

1. Agree on an issue with a clear owner and completion evidence.
2. Update your local `main` from GitHub and create a short-lived branch, such as `data/radar-audit`, `model/radar-baseline`, or `docs/week1-introduction`.
3. Make a focused change. Document how to run it and which inputs it uses.
4. Review the diff before committing. Use your own GitHub identity and meaningful commit messages.
5. Push the branch and open a pull request. Ask another teammate to review it.
6. Resolve feedback, merge the approved change, and update the issue and contribution record.

Use `main` for reviewed work. These are team conventions until GitHub rules enforce them; no branch rules or automated checks have been configured by the scaffold.

## Notebooks and experiments

- Coordinate notebook ownership to avoid editing the same notebook simultaneously.
- Keep code in a reproducible order and document inputs, environment, seeds, and hardware.
- Retain useful plots and evaluated outputs for final submissions. Remove credentials, account-specific paths, and excessive logs before committing.
- Keep training, validation, and final test use distinct. Do not tune against the final test results.
- Put reusable logic in `src/` once it exists, with notebooks used for analysis and explanation.
- Add meaningful tests when behavior warrants them; do not report an unimplemented test suite as passing.

## Files to keep outside Git

Keep datasets, model binaries, local configuration, tokens, and temporary artifacts outside the repository history. Use approved external storage and document access and checksums. `.gitignore` is an aid, not a security control: review staged files before every commit and never force-add credentials.

## Attribution and participation

Record meaningful contributions in `docs/contributions.csv`, with links to issues, commits, pull requests, report sections, or presentation material. Keep actual peer-evaluation forms out of the shared repository; the course treats those evaluations as confidential.

Document reused code and its license. Update the AI-assistance record accurately and follow the instructor's policy. An AI-generated scaffold does not establish that a teammate completed model training or evaluation.
