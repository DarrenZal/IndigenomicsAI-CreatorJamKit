---
doc_kind: team-playbook
status: draft
visibility: public_sample
last_updated: 2026-05-25
---

# Team Playbook: Using the Vision Spec Template

This playbook describes how any Creator Jam team can create a team branch, collaborate on that branch, write a Vision Spec, and later open specific pull requests for polished documents. AI agents can read this document directly and help a team carry it out.

## What This Is For

The Creator Jam Spec Kit is a shared repository for participant specs, templates, examples, and review patterns. This playbook gives every team the same clean path into that shared repo.

It answers:

- How does a team claim its own workspace?
- How does a team write a Vision Spec that another participant, mentor, builder, reviewer, or agent can understand?
- How does a team keep collaboration on its own branch while preparing only polished, review-ready documents for pull requests to `main`?

## Prerequisites

Each team needs:

- A GitHub account with push access to `indigenomicsxyz/CreatorJamSpecKit`
- Git installed on a local machine or in an agent environment
- The shared Vision Spec pattern in this kit
- A short team slug, such as `team-2`, `team-v5`, or another facilitator-approved name

## Step 1: Create the Team Branch

Each team should work on its own shared branch. Use the naming pattern `team/<team-slug>`.

```bash
git clone git@github.com:indigenomicsxyz/CreatorJamSpecKit.git
cd CreatorJamSpecKit
git checkout -b team/<team-slug>
```

If the branch already exists:

```bash
git fetch origin
git checkout team/<team-slug>
git pull origin team/<team-slug>
```

The team branch is the team's collaboration home. Team members should merge their own work into this branch throughout the Jam. Do not treat the team branch as a temporary branch that must be merged wholesale into `main`.

## Step 2: Collaborate on the Team Branch

Teams can collaborate in two clean ways.

### Simple shared-branch flow

Use this when one person or one agent session is editing at a time:

```bash
git checkout team/<team-slug>
git pull origin team/<team-slug>
# edit files
git add specs/<team-slug>/vision-spec.md
git commit -m "<commit message>"
git push origin team/<team-slug>
```

Before another person edits, they should pull the latest team branch:

```bash
git checkout team/<team-slug>
git pull origin team/<team-slug>
```

### Personal work branch flow

Use this when multiple team members or agents are editing at the same time:

```bash
git checkout team/<team-slug>
git pull origin team/<team-slug>
git checkout -b team/<team-slug>/<your-name-or-task>
```

After editing:

```bash
git add specs/<team-slug>/vision-spec.md
git commit -m "<commit message>"
git push origin team/<team-slug>/<your-name-or-task>
```

Then open a pull request from `team/<team-slug>/<your-name-or-task>` into `team/<team-slug>`, not into `main`. The team reviews and merges that work into the team branch first.

## Step 3: Create the Team Folder and Vision Spec

Create a folder under `specs/` named after the team slug. Inside it, create the Vision Spec file:

```text
specs/<team-slug>/vision-spec.md
```

Start the file with frontmatter:

```yaml
---
doc_kind: vision-spec
status: draft
visibility: public_sample
last_updated: 2026-05-25
team: <team-slug>
---
```

## Vision Spec Sections

A Vision Spec should cover these sections:

1. **Context and Problem Statement**: Why does this vision exist now?
2. **North Star Vision**: What larger possibility does the team want to make visible?
3. **Design Principles**: What values, boundaries, and commitments guide choices?
4. **Current-State Assumptions and Unknowns**: What does the team believe, what needs checking, and what should remain open?
5. **Research Notes or Evidence**: What sources, stories, links, observations, or examples shaped the vision?
6. **Proposed Architecture or Operating Model**: How could it work across people, roles, screens, flows, data, prompts, tools, or handoffs?
7. **Multi-Phase Roadmap**: What can happen during the Jam, on demo day, after the Jam, and after review?
8. **Acceptance Criteria**: What would show the prototype honoured the vision?
9. **Risks, Constraints, and Mitigations**: What could go wrong, and how can the team reduce that risk?
10. **Dependencies and Open Questions**: What does the team need from mentors, organizers, permissions, tools, data, cultural guidance, models, or time?
11. **First 3-5 Next Actions**: What are the concrete next moves?

Teams can fill the sections in any order. Empty sections are fine during drafting; they simply mark where the team still needs to think.

## Step 4: Write the Vision Spec

The most reliable team workflow is:

1. One person or one agent session owns the file at a time.
2. Team members contribute inputs through conversation, notes, sketches, or edits.
3. The owner drafts one meaningful section or subsection.
4. The team reviews the wording.
5. The owner commits and pushes before moving to the next major change.

Commit messages should be short and specific:

```text
<name or initials>: section <number> - <what changed>
```

Example:

```text
DJ: section 1 - added problem statement about student isolation
```

## Step 5: Push Team Work

After each meaningful update:

```bash
git add specs/<team-slug>/vision-spec.md
git commit -m "<commit message>"
git push origin team/<team-slug>
```

Other team members can stay current with:

```bash
git fetch origin
git pull origin team/<team-slug>
```

## Step 6: Validate Shape

Run the kit's lightweight validation scripts before calling the work merge-ready:

```bash
python3 scripts/validate-frontmatter.py
python3 scripts/validate-bundle-links.py
```

These scripts check document shape and bundle references. They do not check permission, authority, cultural appropriateness, factual correctness, or readiness for public display.

## Step 7: Prepare Polished Pull Requests

Most team work should stay on the team branch during drafting. When the team has a polished document that is safe and useful for the shared kit, open a narrow pull request to `main`.

Do not open one broad pull request that merges the whole team branch into `main`. Instead, open specific pull requests for specific polished artifacts.

Good pull request examples:

- `specs/<team-slug>/vision-spec.md`
- one reviewed spec fragment
- one display-approved example
- one corrected document that has already passed team review

Before opening a PR to `main`:

1. Pull the latest `main` and the latest team branch.
2. Confirm the document is polished enough to share.
3. Confirm the permission/review state is accurate.
4. Run validation scripts.
5. Open a PR that includes only the intended file or small set of files.

Ask a facilitator or reviewer to check:

   - **Fit state**: Is this ready to compose into a candidate bundle?
   - **Permission state**: Is the material public sample, display approved, review required, protected, or refused?
   - **Review state**: Has the right review happened for the stated use?

Merge into `main` only after the team and reviewer agree the specific artifact belongs in the shared kit.

## AI Agent Rules

If you are an AI agent helping a team, follow these rules:

1. **Never push protected, cultural, linguistic, ceremonial, private, or review-required material as if it were public.** The safest material is public sample, fictional, or explicitly display-approved.
2. **Stay in the team lane.** Write team work under `specs/<team-slug>/` on the team branch unless a facilitator explicitly asks for shared docs, templates, or examples.
3. **Do not compute on refused or do-not-compute content.** If a team member marks something private, protected, or review-required, record the boundary without processing the content.
4. **Require frontmatter.** Every markdown file under `specs/` should start with YAML frontmatter.
5. **Work one section at a time.** Help the team fill one section, commit, and push to the team branch before broad rewrites.
6. **Ask instead of inventing.** If a section is ambiguous, surface questions back to the team.
7. **Preserve team voice.** Edit for clarity, but do not replace the team's language with generic AI summary language.
8. **Do not hide uncertainty.** Use open questions, assumptions, and review notes rather than pretending the team has resolved something it has not resolved.

## When the Vision Spec Is Ready for the Kit

A Vision Spec is not automatically a bundle or a build. After a Vision Spec is complete, the next possible steps are:

1. **Wrap as a Spec Fragment**: Use `templates/spec-fragment.md` to add permission state, fit state, review state, and bundle context.
2. **Offering Integration Session**: The team presents the fragment to the group. A facilitator records fit, review, and bundle decisions.
3. **Build Attempt**: If selected for build, the team creates `templates/build-attempt-instructions.md` and attempts a scoped build.
4. **Reviewer Check and Witness Rollup**: Record what passed, what was partial, what failed, and what was refused.
5. **Display Review**: Before any story, receipt wall item, public slide, or showcase artifact, run `templates/display-review-checklist.md`.

## Troubleshooting

- **Branch push fails with permission denied**: A repo owner needs to grant the team or agent push access.
- **Validation reports missing frontmatter**: Add a YAML frontmatter block at the top of the file.
- **Merge conflicts during pull**: Pull often, resolve conflicts together, and commit the merged result to the team branch.
- **Agent cannot push**: The agent environment may lack SSH key access. A human team member can push, or the team can configure an SSH key for that environment.
- **Team material should not be public**: Keep it out of the shared kit until the correct permission and review path is clear.
- **A PR to main includes too much**: Close it or narrow it. Team branches can contain messy drafting; `main` should receive specific polished documents.

## Source

This playbook is part of the Creator Jam Spec Kit: `github.com/indigenomicsxyz/CreatorJamSpecKit`.
