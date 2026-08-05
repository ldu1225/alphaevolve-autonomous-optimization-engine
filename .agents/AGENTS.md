# AlphaEvolve Project Rules & Guidelines

## CRITICAL MANDATORY RULES (STRICT ENFORCEMENT)

1. **ABSOLUTELY ZERO HARDCODING, PRE-DEFINED TEMPLATES, OR FALLBACKS**:
   - NEVER create pre-defined code snippet arrays, templates, fallback arrays (`sample_candidates`), or hardcoded strings for candidate generation (e.g. `evolved_results`, `GENERATION_PROCS`, `sample_candidates`).
   - NEVER add fallback mock data logic even if Cloud API latency takes time.
   - All evolved candidates MUST come purely from the official evolutionary search process.

2. **NO DIRECT GEMINI SDK CALLS FOR EVOLUTION**:
   - NEVER call `google.generativeai` or `gemini-2.5-flash` directly in evolution scripts.
   - All evolutionary operations MUST use the official `alpha_evolve` SDK framework (`AlphaEvolveClient`, `AlphaEvolveExperiment`).

3. **OFFICIAL ALPHAEVOLVE FRAMEWORK INTEGRATION**:
   - Follow the exact architecture of `examples/circle_packing/src/run_evolution.py`.
   - Register the evaluation callback (`verilog_fir_evaluation`) with `AlphaEvolveExperiment`.
   - Read problem instructions from `instructions.md`.
   - Ensure evaluated results are updated cleanly to `live_verilog_data.json` for web dashboard rendering.
