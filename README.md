# careercoach-archetype

The **Career Coach** archetype bundle for [protoAgent](https://github.com/protoLabsAI/protoAgent):
a job-hunt copilot. Paste your resume, get a profile and fresh roles in minutes, then
triage an inbox, track your pipeline, and prepare for applications and interviews.

**It never submits an application.** It prepares an apply kit — a tailored resume,
cover letter, and every answer — and the operator files the form. Browser fill is an
opt-in beta, default off, and still never submits. You review the kit and submit yourself.

## What it does

| Phase | What happens | You see |
|---|---|---|
| **First run** | Paste a resume or provide a LinkedIn PDF → build your profile → confirm targets and location once → seed draft answers → run the first keyless scan | Your profile and fresh roles in the **Career Coach** view |
| **Inbox** | Review discovered roles and decide which deserve attention | Roles to keep or dismiss, with fit information |
| **Pipeline** | Track chosen roles, application progress, and follow-ups | A pipeline you control |
| **Apply kit** | Tailor a resume and cover letter and prepare application answers from your profile | A kit to review and copy into the form yourself |
| **Interview prep** | Practice interviews and develop grounded stories from your experience | Mock questions, feedback, and preparation notes |
| **Strategy** | Discuss positioning, target roles, skill gaps, offers, and negotiation | Concrete next steps and honest tradeoffs |

## The rules it keeps

The persona is protoAgent's `career-coach` soul preset:

1. **Never fabricates experience or metrics.** Missing evidence is a question for you,
   never an invitation to invent an achievement.
2. **Your operator profile is the single source of truth.** Drafts and answers draw
   from confirmed experience, preferences, and constraints.
3. **Never auto-submits.** You review the apply kit and file the application yourself,
   including when you opt into browser fill.
4. **Honest fit scoring.** It explains gaps and tradeoffs instead of treating every
   posting as a strong match.
5. **Verifies company facts.** Research needs sources; uncertain claims stay uncertain.

## What's inside

| plugin | source | role |
|---|---|---|
| `careercoach` | [careercoach-plugin](https://github.com/protoLabsAI/careercoach-plugin), floor `v0.13.4` | First-run onboarding, profile, role discovery, inbox, pipeline, apply kits, interview prep, and the **Career Coach** view |
| `artifact` | builtin | Renders CVs and cover letters |
| `notes` | builtin | Ideas and loose ends between sessions |
| `agent_browser` | builtin | `browser_open` and `browser_pdf` turn the tailored resume into the kit's PDF. Browser fill stays off, and the submit gate blocks any submit click |

The bundle explicitly enables all four members: `careercoach` and `agent_browser` are
disabled by author default. The persona lives in core as the `career-coach` preset; the picker catalog row
also lives in core and supplies the id `career-coach`.

No configuration overrides or setup inputs are needed. The plugin defaults to
`jobs_provider: auto`, which uses keyless Himalayas when no API key is configured.
Browser fill stays off, and the agent inherits the host's model connection.

## Create an agent

**Core floor: protoAgent ≥ 0.34.0.** Career Coach declares
`min_protoagent_version: 0.34.0`; the loader refuses it on older cores. The bundle
targets `0.224.0` for verification. Bundles cannot enforce a core floor themselves.

The `career-coach` soul preset ships with the protoAgent PR adding the catalog row.
On older cores without that preset, `soul_preset` falls back to the base persona.
Pass `soul` inline as below to supply the Career Coach persona explicitly.

### From the picker (once the archetype is listed)

Choose **Fleet ▸ New agent ▸ Career Coach ▸ Create** once the core catalog lists it.

You can also use **Settings ▸ Plugins ▸ Install from URL** →
`https://github.com/protoLabsAI/careercoach-archetype`. An installed bundle with an
`archetype:` block registers a picker card and installs its members on the hub.
Enable the suggested members on the agent you intend to use. If the host lacks the
preset, paste the persona into **Advanced ▸ Persona** during setup.

### From the API

Fetch the core persona and send it inline, so the host need not already ship the preset:

```bash
curl -fsSL https://raw.githubusercontent.com/protoLabsAI/protoAgent/main/config/soul-presets/career-coach.md -o career-coach.md

jq -n --rawfile soul career-coach.md '{
  name: "career-coach",
  bundle: "https://github.com/protoLabsAI/careercoach-archetype",
  soul: $soul,
  requires_tools: ["careercoach_find_roles", "careercoach_save_apply_kit", "browser_pdf"]
}' | curl -s -X POST http://127.0.0.1:7870/api/fleet \
      -H 'content-type: application/json' \
      ${PROTOAGENT_TOKEN:+-H "authorization: Bearer $PROTOAGENT_TOKEN"} \
      -d @-
```

`7870` is the default instance port; use your hub's port. The member inherits the hub's
model connection (`inherit_config: true` by default). Add `"port": 7880` to choose
its port. This route requires a core with the fleet API and bundle support.

### Install onto an existing agent

Run from a protoAgent environment:

```bash
python -m server plugin install https://github.com/protoLabsAI/careercoach-archetype
```

Then enable `careercoach, artifact, notes, agent_browser`. Direct install uses `soul_preset` on hosts
that ship it; otherwise supply the persona explicitly.

## First run

1. Paste your resume or provide a LinkedIn PDF in chat. Career Coach builds your
   operator profile; correct anything missing or inaccurate.
2. Confirm your target roles and location constraints once. These guide the search
   and fit assessment.
3. Review the seeded draft answers. Keep them grounded in your profile and resolve
   unknowns before using them in an application.
4. Let the first keyless scan find roles, then open the **Career Coach** view to
   triage the inbox and start your pipeline.
5. Pick a role and request an apply kit. Review the tailored resume, cover letter,
   and answers, then fill and submit the application yourself.

`v0.13.4` is the first release with first-run onboarding (S5a), a per-agent workspace,
kit validation and the grounding check all in place.

## Optional JSearch API key

No API key is needed to start. With `jobs_provider: auto`, an empty `jobs_api_key`
uses the Himalayas remote-jobs board. For JSearch, add your RapidAPI key under
**Settings ▸ Plugins ▸ Career Coach ▸ Job-source API key** (`careercoach.jobs_api_key`).
The key is stored in `secrets.yaml`; with it, `auto` selects JSearch. Keep secrets
out of the bundle manifest. Targets and location constraints remain yours to confirm.

## Pin lifecycle (ADR 0049)

External members pin release tags. On core ≥ 0.146, each pin is a **floor**: installs
take the newest compatible release (caret semantics; for 0.x, the minor is the
boundary). The `v0.13.4` floor admits compatible `0.13.x` releases.

The shared scripts and workflow are copied verbatim from
[brand-launch-archetype](https://github.com/protoLabsAI/brand-launch-archetype/tree/27b0775c34859203718ba221c43a32236968a62d).
On every PR and weekly, `verify-bundle.yml` installs the bundle into a scratch agent
on a fresh protoAgent checkout, loads its members, probes declared views for HTTP
200, and verifies that `careercoach_find_roles`, `careercoach_save_apply_kit` and
`browser_pdf` bind.
The update checker proposes a pin bump only for an out-of-range release.

### Pin-bump PR lifecycle

The `bump` job runs weekly, on manual dispatch, and on `member-released` dispatch.
It reuses one `bump-pins` branch and PR, rewritten on each bump; do not hand-edit
that branch. A PR opened with the repository `GITHUB_TOKEN` does not automatically
start its `pull_request` workflow. The job flags a missing or approval-required run
with a label, comment, and failed job. A maintainer must approve the verify run
or close the PR; merge only after verification passes.

If verification needs core changes that have not merged, set the repository variable
`PROTOAGENT_REF` to that ref (for example, `refs/pull/<n>/head`). Remove it once the
changes land so verification tracks `main` again.

Run locally from a protoAgent checkout with dependencies synced:

```bash
uv run --no-sync python /path/to/careercoach-archetype/scripts/verify_bundle.py /path/to/careercoach-archetype
```

The bundle path must be a git checkout containing the committed manifest, because
the installer clones it. Lightweight checks from this bundle checkout:

```bash
python3 -c "import yaml; yaml.safe_load(open('protoagent.bundle.yaml'))"
python3 -m py_compile scripts/*.py
bash -n scripts/bump_pins_pr.sh
```
