# Repository setup

## Create the GitHub repository

Suggested owner: `Diehl64`. Suggested name: `aai-590-capstone`.

Suggested description: `USD AAI-590 capstone: sensor classification, visual verification, and human-reviewed monitoring.`

1. Open https://github.com/new while signed in to the intended account.
2. Choose the owner, name, and description above. Start with Private visibility.
3. For importing this scaffold, leave GitHub's README, .gitignore, and license initialization options off; the scaffold supplies its own files.
4. Create the repository. Import the contents of this directory at the repository root, including `.gitignore` and `.github/`. Do not upload the ZIP as the project code.
5. Confirm `README.md` appears on the repository home page and `main` is the default branch.

The repository has not been created by this package. The URL becomes valid only after creation.

## Team access

After confirming their GitHub usernames with them, invite Mostafa and Jacob as collaborators. Do not infer accounts from display names. Confirm the instructor's GitHub username and provide access if the repository remains private.

Access and invitations are not configured by this scaffold. A documented review process does not itself enable branch protection. Where the account plan permits, configure main-branch protection or a ruleset requiring pull requests and a teammate's review. Keep an owner recovery path and verify that settings do not prevent the team from working.

## Local setup after publication

GitHub Desktop is a convenient option for managing commits and branches. Clone the new repository to your own computer. Alternatively, after the repository exists:

```bash
git clone https://github.com/Diehl64/aai-590-capstone.git
cd aai-590-capstone
git switch -c docs/initial-data-audit
```

Use a project-specific Python environment when code is introduced. The team should agree on the Python version and framework, test installation, and commit the resulting dependency specification. This scaffold intentionally contains no guessed package versions or runnable-model claim.

## First team tasks

Create unassigned issues from the task template, then agree on owners:

1. Confirm capstone classes, scope, and original contribution beyond AAI-540.
2. Inspect the proposed radar dataset, access rights, labels, recording groups, and split strategy.
3. Select the first visual dataset and define what paired observations are available.
4. Choose and validate a shared Python environment and a neural-network training baseline.
5. Define the local replay interface and the distinction between measured and simulated outputs.
6. Reconcile the Week 1 introduction with the approved scope and course template.

No deadlines are assigned here because the Canvas calendar must supply the actual due dates.
