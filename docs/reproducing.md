[← README](../README.md)

# Reproducing

Use `.venv\Scripts\python.exe` (Python 3.12, CUDA) with `requirements.txt`. The app needs Node.js (`cd app`,
`npm install`). Requires Hugging Face access to CONCH (`MahmoodLab/CONCH`) and MUSK (`xiangjx/musk`), the MHIST
dataset in `data/mhist/`, GlaS for the crypt finder, and for the outside checks and similar cases UniToPatho, SPIDER
and HunCRC under `data/`. MUSK's code is loaded from a clone of github.com/lilab-stanford/MUSK via `MUSK_SRC`. The
literature reading needs a Lumen key (`LUMEN_API_KEY`).

```bash
# 5-fold cross-validation per candidate
python research/kfold_cv.py --backbone conch         --blocks -1 --lr 1e-5 --batch 8 --accum 2 --tag conch_full
python research/kfold_cv.py --backbone convnext_base --blocks -1 --lr 1e-4 --batch 8 --accum 2 --tag convnext_base
python research/kfold_cv.py --backbone plip          --blocks -1 --lr 1e-5 --tag plip_full
MUSK_SRC=<MUSK clone> python research/kfold_cv.py --backbone musk_lora --lr 1e-4 --batch 2 --accum 8 --tag musk_lora

# final model per candidate on all training images (N = median best epoch from its folds), e.g.
python research/kfold_cv.py --backbone convnext_base --blocks -1 --lr 1e-4 --batch 8 --accum 2 --tag convnext_base --final-epochs N

# choose the panel on training data, then score the test split once
python research/panel.py --members conch_full convnext_base plip_full musk_lora

# export what the app needs (standardisation, calibrations, cut-off chart, unlike-training-data reference)
python research/export_panel.py

# crypt finder (U-Net on GlaS) and its label thresholds from MHIST training crypts
python research/train_gland_net.py
python research/gland_thresholds.py

# similar-cases reference set (other labs' labelled fields at the app's field size)
python research/build_reference_cases.py --field-um 448 --gpu

# demo sheet: six other-lab fields with a 100 um bar
python research/make_outside_demo.py

# checks of the app as built (nothing is chosen from these)
python research/eval_app_panel.py            # test tiles through the app's own path
python research/unitopatho_panel_check.py    # another hospital's slides
python research/scale_stress.py 0            # scale-bar reading on generated viewer screens
python research/map_faithfulness.py          # deletion test for the evidence map
python research/evidence_vs_crypts.py        # evidence map vs crypt measurements
python research/vlm_baseline.py              # a general vision LLM on the MHIST test images (uses Lumen)
python research/scale_audit.py measure       # dataset scale audit (then: python research/scale_audit.py summary)
python research/field_size_panel_sweep.py    # outside results by field size
python research/stability_check.py           # repeated and overlapping analyses against a running backend
```
