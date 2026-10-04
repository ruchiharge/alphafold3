# AlphaFold3 — VEGFA / VEGFR / Bevacizumab Project

A research scratchpad for studying antibody-mediated inhibition of antigen binding using **AlphaFold3** (predictions on the BITS Hyderabad HPC cluster), **ChimeraX** (interface analysis) and **OpenMM** (potential-energy scoring). The scientific subject is the VEGFA / VEGFR / Bevacizumab (rhuMAB) complex — the interaction targeted by the anti-angiogenic antibodies Bevacizumab and Ranibizumab.

The full write-up is in [`FinalReport.md`](FinalReport.md) (also bundled with every figure and animation it references in [`report/`](report/)).

## Project at a glance

The work is split into two phases:

- **Phase 1 — pipeline validation and antibody studies.** Reproduce the wild-type VEGFA–VEGFR complex (PDB [5T89](https://www.rcsb.org/structure/5T89)) using AF3 on the BITS Hyderabad HPC cluster, then build ternary models adding the Bevacizumab Fab and the full Ranibizumab antibody. Question: does the antibody mechanically displace the receptor in the predicted geometry?
- **Phase 2 — saturation mutagenesis at VEGFA Glu 74.** ChimeraX H-bond / contact analysis on the wild-type model identified Glu 74 as the load-bearing residue at the receptor interface (5 of 11 inter-chain H-bonds on each canonical pair). Two pilot mutations (E74Q, E74G) plus the full 19-residue saturation scan were submitted via SLURM job arrays, with each mutant ranked by AF3 confidence and OpenMM Amber19 potential energy.

Headline findings: AF3 reproduces the wild-type interface with high confidence (ipTM 0.83, ranking 0.89) and recovers the same key residues as the crystal structure; the antibodies do **not** displace VEGFR in the predicted complex; only the closest chemical relatives of Glu (Q, D, N) preserve the wild-type interface, while bulky / non-polar substitutions (W, L, V, I) clearly disrupt it.

## Directory layout

```
.
├── 5T89.cif                                # Reference crystal structure (PDB 5T89)
├── 5T89_VEGF_VEGFR_Complex/                # Run 2 — wild-type reference (best AF3 output)
├── VEGFR_VEGFA_complex_seed{1,2}/          # Run 1 — single-chain pilots (superseded)
├── fold_2026_02_03_21_48/                  # AF3-server output feeding demo2.json
├── demo3/                                  # Run 3 — Bevacizumab Fab + VEGFA / +VEGFR
├── demo4/                                  # Run 4 — Ranibizumab + VEGFA / +VEGFR
├── demo5/                                  # Run 5 — pilot mutations at E74 (Q, G)
├── demo6/                                  # Run 6 — saturation scan at E74 (19 mutants)
├── openMM/                                 # OpenMM Amber19 energy scripts + outputs
├── report/                                 # Self-contained report bundle (md + figures + videos)
│
├── alphafold3_demo2*.slurm                 # SLURM submission scripts (H100 + A100 fallback)
├── demo2.json                              # AF3 input for Run 2
│
├── chimeraX_script.py                      # Atom-distance enumeration (run inside ChimeraX)
├── h_bond_sorter.py                        # Sort H-bonds by donor–acceptor distance
├── comparison.txt                          # Cross-model H-bond / contact notebook
│
├── image*.png                              # Figures referenced from FinalReport.md
├── *_animation.mp4                         # Structure animations (Runs 2–4)
├── distances_under_5A.txt                  # ChimeraX contact dump
├── input_h_bond.txt / contacts_list.txt    # ChimeraX H-bond / contact dumps
│
├── FinalReport.md                          # Final project report
├── PresentationScript.md                   # Presentation script
├── Midsem_Report_OptimalAntibodyAntigen.pdf
└── done till now.txt                       # Running narrative of every experiment
```

Every `demoN/` directory contains its own `demoN_stats.txt` documenting the chain-letter convention for that run (e.g. `A, C = light chain; B, D = heavy chain; E, F = VEGFA; G, H = VEGFR`). These conventions are biologically meaningful and must match the AF3 input JSONs and any ChimeraX `/<letter>` selectors.

## Pipeline

One experimental iteration goes through these steps:

1. **Author input** — hand-write a `demoN_M.json` in the AF3 v1 dialect (`dialect: "alphafold3"`, `version: 1`, list of `sequences` with per-chain IDs).
2. **Submit on HPC** — upload to `~/af3_input/` on the cluster and `sbatch alphafold3_demoN_M.slurm`. SLURM scripts bind `~/af3_input`, `~/af3_output`, `~/alphafold3/alphafold3_databases`, `~/alphafold3/alphafold3_model_params` and run `~/alphafold3/alphafold3.sif` via `singularity --nv`. The `_a100.slurm` variant is the A100 fallback (5-day walltime) when `gpu_h100_4` is saturated.
3. **Job arrays for saturation scans** — for the 19-mutant Run 6, a single `#SBATCH --array=0-18` script (`demo6/slurm_files_demo6/alphafold3_demo6_all.slurm`) queues every mutant with `sbatch alphafold3_demo6_all.slurm`.
4. **Download output** — AF3 returns `<name>_model.cif` (best model), `<name>_ranking_scores.csv`, `<name>_summary_confidences.json`, plus per-seed/sample subdirectories `seed-N_sample-M/`.
5. **Pick best model** — `5T89_VEGF_VEGFR_Complex/script_best_score.py` reads `<name>_ranking_scores.csv` and prints the seed/sample with the maximum `ranking_score`.
6. **Analyse in ChimeraX** (1.11.1) — load the best CIF, then per chain pair:
   ```
   contacts /A restrict /C distanceOnly 4.0 log true
   hbonds   /A restrict /C showDist true   log true
   ```
   Repeat for `/A`↔`/D`, `/B`↔`/C`, `/B`↔`/D`. The Log panel output is copied into `comparison.txt` / `input_h_bond.txt`.
7. **Sort H-bonds** — `python h_bond_sorter.py` rewrites `input_h_bond.txt` sorted by donor–acceptor distance (strongest contacts first).
8. **Energy check with OpenMM** — `python openMM/script.py` for a single hard-coded CIF; `python demo6/script.py` for batch energies of every `demo6/demo6*/<X>_model.cif`, written to `demo6/output.txt`. Both use Amber19 (`amber19-all.xml`, `amber19/tip3pfb.xml`) on the as-predicted geometry, so the resulting potential energies are coarse comparative scores rather than absolute thermodynamic quantities.

## Requirements

- AlphaFold3 (DeepMind container — runs on HPC under Singularity)
- ChimeraX 1.11.1 — interface analysis, `contacts`, `hbonds`, `swapaa`, `matchmaker`
- OpenMM with the Amber19 force field (`amber19-all.xml`) and TIP3P-FB water model
- Python 3.12 (for `h_bond_sorter.py`, `script_best_score.py`, the OpenMM drivers)
- SLURM (cluster-side) — `gpu_h100_4` (24 h walltime) or `gpu_a100_8` (5-day fallback)

## Reference

Final report and bibliography: [`FinalReport.md`](FinalReport.md). Key external references — AlphaFold3 [paper / GitHub](https://github.com/google-deepmind/alphafold3), [AlphaFold Server](https://alphafoldserver.com/), [ChimeraX docs](https://www.cgl.ucsf.edu/chimerax/docs/user/index.html), [PDB 5T89](https://www.rcsb.org/structure/5T89).
