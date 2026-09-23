# Skill routing evals

`skill-routing-cases.yaml` contains positive, negative, edge, and overlap prompts for
the nine highest-priority skills. Run the deterministic, API-free baseline with:

```bash
python -m evals.run_skill_evals
```

The baseline deliberately measures routing boundaries only. It does not grade research
quality or claim that regex routing is the production host's selection algorithm. A
future optional LLM judge may consume the same corpus, but it must remain outside the
default test suite, record model/version/settings, and never replace these deterministic
regressions.
