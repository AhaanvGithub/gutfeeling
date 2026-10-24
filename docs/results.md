[← README](../README.md)

# Performance

On the 977 MHIST test images, scored once with the exact models, weights and cut-off the app runs
([`panel.json`](results/panel.json)):

| | Balanced accuracy | AUC | Accuracy | SSL caught | HP caught | Calibration error | Correlation with vote count |
|---|---|---|---|---|---|---|---|
| **Panel (ConvNeXt-Base + MUSK)** | **0.888** | **0.956** | **0.887** | **89.2%** | **88.5%** | **2.2%** | **0.858** |
| Earlier panel "CLIK" (ConvNeXt-Tiny + PLIP + MUSK, last 2 layers) [c] | 0.877 | 0.959 | 0.863 | 93.1% | 82.3% | 4.7% | 0.860 |
| ConvNeXt-Base alone | 0.853 | 0.948 | 0.827 | 95.3% | 75.4% | 10.0% | 0.840 |
| PLIP alone | 0.862 | 0.946 | 0.858 | 87.8% | 84.6% | 11.2% | 0.838 |
| MUSK alone | 0.820 | 0.936 | 0.781 | 96.7% | 67.3% | 5.4% | 0.825 |
| CONCH alone | 0.831 | 0.932 | 0.804 | 93.3% | 72.8% | 8.4% | 0.816 |
| Fine-tuned CONCH, last 2 blocks (earlier release) | 0.819 | 0.908 | 0.826 | 79.2% | 84.6% | 3.4% | 0.775 |

[c] CLIK was the best group before ConvNeXt-Base and MUSK with LoRA were trained: the average of its 5
cross-validation models, with weights, calibration and cut-off fit on training images
([`preliminary_test_check.json`](results/preliminary_test_check.json)). The final panel replaced it by the same training-data rule.
Single members use a plain 50% cut-off, so they lean toward SSL; the panel's calibrated cut-off balances
the two classes. About 1 in 6 test tiles is a 4-3 split among the pathologists, which caps any model: even
a perfect model would agree with a fresh 7-pathologist majority only about 89-92% of the time. The panel's
0.887 accuracy is at that ceiling. On the 4-3 splits it agrees with the majority 65% of the time.

### Compared with published results on MHIST

In short, on the official MHIST test split (977 tiles):
- **Balanced accuracy:** 0.888, above every published balanced accuracy we found. The best of those that never used
  the test split is Virchow2 at 0.848, a frozen-feature (linear probe) result.
- **Against fine-tuned models:** THUNDER reports no balanced accuracy for its fine-tuned (LoRA) models. Its reported
  LoRA gain puts LoRA-tuned Virchow2 at about 0.875 weighted F1, against the panel's 0.888.
- **Accuracy and F1:** level with PolarHE (0.891 / 0.890), which does not report balanced accuracy or say how its
  model was selected.

No method here trains on test images. What differs is whether the test split was used to *choose* the
model (which epoch or checkpoint to keep), which makes a score look better than it would on new data. The
first table holds only methods that never used the test split, the fair comparison for gutfeeling;
the second holds methods that used it or do not say. Both use the official MHIST test split (977 tiles),
sorted by balanced accuracy; rows that do not report it follow. Blank = not reported.

**Never used the test split to choose the model.** Fine-tuned models first, then frozen features with a linear
classifier (linear probe).

| Method | How the model is adapted | Balanced acc. | Accuracy | AUC | F1 | ECE | Test images used to choose the model | Source |
|---|---|---|---|---|---|---|---|---|
| *Fine-tuned* | | | | | | | | |
| **gutfeeling panel** (ConvNeXt-Base + MUSK) | Fine-tuned ([recipe](model.md)), group chosen on training data | **0.888** | **0.887** | **0.956** | **0.888** | **2.2%** | None | this repo |
| gutfeeling, earlier panel "CLIK" (ConvNeXt-Tiny + PLIP + MUSK) | Fine-tuned; average of 5 cross-validation models | 0.877 | 0.863 | 0.959 | 0.865 | 4.7% | None | this repo [c] |
| gutfeeling, earlier release (fine-tuned CONCH x4) | Last 2 blocks fine-tuned, soft labels, calibrated | 0.819 | 0.826 | 0.908 | 0.827 | 3.4% | None | this repo |
| Virchow2, LoRA fine-tuned | LoRA | | | | ~0.875 (derived) | | None (validation carved from train) | THUNDER [2] |
| CONCH, LoRA fine-tuned | LoRA | | | | ~0.851 (derived) | | None (validation carved from train) | THUNDER [2] |
| UNI, LoRA fine-tuned | LoRA | | | | ~0.847 (derived) | | None (validation carved from train) | THUNDER [2] |
| *Linear probe* | | | | | | | | |
| Virchow2 | Frozen + linear | 0.848 | | | 0.836 | 0.6% | None (validation carved from train) | THUNDER [2] |
| H-optimus-0 | Frozen + linear | 0.837 | | | 0.828 | 1.6% | None (validation carved from train) | THUNDER [2] |
| Virchow | Frozen + linear | 0.827 | | | 0.823 | 3.5% | None (validation carved from train) | THUNDER [2] |
| UNI | Frozen + linear | 0.825 | | | 0.824 | 3.1% | None (validation carved from train) | THUNDER [2] |
| DINOv2-B (natural images) | Frozen + linear | 0.819 | | | 0.826 | 0.6% | None (validation carved from train) | THUNDER [2] |
| CONCH | Frozen + linear | 0.800 | | | 0.797 | 3.2% | None (validation carved from train) | THUNDER [2] |
| MUSK | Frozen + linear | 0.792 | | | 0.800 | 7.0% | None (validation carved from train) | THUNDER [2] |
| PLIP | Frozen + linear | 0.790 | | | 0.785 | 1.7% | None (validation carved from train) | THUNDER [2] |
| QuiltNet | Frozen + linear | 0.735 | | | 0.735 | 1.8% | None (validation carved from train) | THUNDER [2] |

**Used the test split to choose the model, or did not say**

| Method | How the model is adapted | Balanced acc. | Accuracy | AUC | F1 | ECE | Test images used to choose the model | Source |
|---|---|---|---|---|---|---|---|---|
| Virchow2 | Frozen + MLP head | 0.861 | | | | | All 977 (checkpoint selection) | EVA protocol [3] |
| UNI / H-optimus-0 | Frozen + MLP head | 0.843 | | | | | All 977 (checkpoint selection) | EVA protocol [3] |
| CONCH | Frozen + MLP head | 0.832 | | | | | All 977 (checkpoint selection) | EVA protocol [3] |
| Virchow | Frozen + linear | 0.830 | 0.834 | | 0.835 | | Not stated | Virchow paper [4] |
| ImageNet ViT (natural images) | Frozen + linear | 0.821 | 0.826 | | 0.827 | | Not stated | Virchow paper [4] |
| CTransPath | Frozen + linear | 0.801 | 0.817 | | 0.816 | | Not stated | Virchow paper [4] |
| PolarHE (self-supervised) | Frozen + linear |  | 0.891 | 0.941 | 0.890 |  | Not stated | PolarHE [5] |
| UNI (as reported by [5]) | Frozen + linear |  | 0.856 | 0.920 | 0.856 |  | Not stated | PolarHE [5] |
| DiRL (as reported by [5]) | Not stated |  | 0.836 | 0.950 |  |  | Not stated | PolarHE [5] |
| DINO (as reported by [5]) | Frozen + linear |  | 0.831 | 0.898 | 0.816 |  | Not stated | PolarHE [5] |
| ResNet-18, ImageNet-pretrained | Fully fine-tuned | | | 0.927 | | | All 977 (best epochs kept) | MHIST paper [1] |
| ResNet-18, from scratch | Fully trained | | | 0.845 | | | All 977 (best epochs kept) | MHIST paper [1] |

How the protocols differ:
- **gutfeeling**: every choice (members, epochs, weights, calibration, cut-off) is made on training images;
  the test split is scored once. F1 is weighted F1, as in the other rows. The panel has the highest balanced
  accuracy and AUC of any comparable result we found, using only openly available models. Most published rows
  are linear probes, which fine-tuning usually beats; against fine-tuned results (THUNDER's LoRA rows, F1 only)
  the panel is still ahead. Accuracy and F1 are level with PolarHE [5], which does not say how its model was
  selected.
- **[5] PolarHE**: frozen features with a linear classifier; reports the official split sizes (2,175 / 977) but
  not how the model was selected.
- **Not comparable**: a 2026 preprint reporting 90.2% accuracy and 0.955 AUC with vision transformers (CaiT) used
  5-fold cross-validation over all 3,152 images instead of the official test split [6].
- **[1] MHIST paper**: AUC is the mean of each run's 5 best test-set epochs over 10 seeds, so the epoch is
  chosen on the test split. It reports AUC only.
- **[2] THUNDER** (NeurIPS 2025, 23 models): frozen features with a linear classifier, 95% confidence
  intervals of about +-2.5 points on MHIST. LoRA rows are derived as THUNDER's frozen F1 plus its reported
  LoRA gain on MHIST (Virchow2 +3.9, CONCH +5.4, UNI +2.3 points).
- **[3] EVA** (kaiko.ai protocol, values from the MINT paper): frozen features with an MLP head, 5 runs;
  EVA uses the MHIST test split for early stopping and checkpoint selection.
- **[4] Virchow paper**: frozen features with a linear classifier (appendix table A4).

Sources:
[1] Wei et al., *A Petri Dish for Histopathology Image Analysis*, 2021 ([arXiv 2101.12355](https://arxiv.org/abs/2101.12355)).
[2] *THUNDER: Tile-level Histopathology image UNDERstanding benchmark*, NeurIPS 2025, tables S38, S39, S52 and table 3 ([arXiv 2507.07860](https://arxiv.org/abs/2507.07860)).
[3] *MINT: Molecularly Informed Training with Spatial Transcriptomics Supervision for Pathology Foundation Models*, table 2 ([arXiv 2603.07895](https://arxiv.org/abs/2603.07895)); protocol: [kaiko.ai eva](https://kaiko-ai.github.io/eva/main/leaderboards/).
[4] Vorontsov et al., *Virchow: A Million-Slide Digital Pathology Foundation Model*, table A4 ([arXiv 2309.07778](https://arxiv.org/abs/2309.07778)).
[5] *Beyond H&E: Unlocking Pathological Insights with Polarization via Self-supervised Learning* (PolarHE), 2025 ([arXiv 2503.05933](https://arxiv.org/abs/2503.05933)).
[6] *Vision Transformers Based AI Models For Predicting Colorectal Cancer from Digital Pathology WSI: Use Case Of MHIST dataset*, medRxiv 2026 ([link](https://www.medrxiv.org/content/10.64898/2026.02.03.26345516v1.full)).

### Could a general vision LLM do this?

The same 977 MHIST test images were given to **Gemma-4 31B**, a general multimodal LLM, with an expert prompt that
states the WHO 2019 criteria, one image at a time ([`research/vlm_baseline.py`](../research/vlm_baseline.py), [`vlm_baseline.json`](results/vlm_baseline.json)):

| On the 977 MHIST test images | Balanced accuracy | SSL caught | HP cleared | Called SSL |
|---|---|---|---|---|
| **gutfeeling panel** | **0.888** | 89.2% | 88.5% | |
| Gemma-4 31B, expert prompt | 0.554 | 96.4% | 14.4% | 89.6% of images |
| Chance | 0.500 | | | |

The general model calls nearly every field SSL: it describes H&E correctly but cannot separate the two lesions. The
decision here needs models trained on pathologists' calls.
