# ClickUp session log format

Where: a comment on the starter's task `Training: <Name>` in the **New Starter Training** list (Training space).

Rules:
- One comment per session. No @mentions: this is a quiet log, and the weekly summary notifies the trainer.
- Plain and factual. Don't judge the person; just record what happened.
- Always start with the `[SESSION LOG]` tag and the date, because the weekly summary job finds entries by that tag.

## Template

```
[SESSION LOG] <YYYY-MM-DD>
Modules worked on: <module names, or "general questions">
Questions asked (<n>):
- <short paraphrase> -> answered from <doc name> / NOT IN DOCS
- ...
Not covered by docs (for trainer): <list, or "none">
Asked more than once: <topics the starter came back to, or "none">
Modules completed this session: <names, or "none">
Next up: <what the starter said they'll do next, if known>
```

## Example

```
[SESSION LOG] 2026-11-24
Modules worked on: Walmart listings
Questions asked (4):
- Do we match Walmart price to Amazon? -> answered from Walmart listings guide (no, keep existing Walmart price)
- Where do Prop 65 warnings go? -> answered from Walmart listings guide
- What's the shipping template for oversize items? -> NOT IN DOCS
- How do I find the Amazon twin of a Walmart item? -> answered from Listing parity guide
Not covered by docs (for trainer): Walmart shipping template for oversize items
Asked more than once: none
Modules completed this session: none
Next up: practise optimising one Gourmanity Walmart listing
```

## Weekly summary (written by the scheduled job, not by the starter's session)

```
[WEEKLY UPDATE] w/e <YYYY-MM-DD>
@<trainer>
Status: On track / Needs a check-in / Stuck
Sessions this week: <n>
Modules completed: <list>
Current module: <name>
Gaps in the docs: <list>
Repeated questions: <list>
Suggested follow-up: <one or two lines>
```
