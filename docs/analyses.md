[← README](../README.md)

# Supporting analyses

| Question | Finding | File |
|---|---|---|
| How much do pathologists agree? | On MHIST, a single pathologist agrees with the 7-pathologist majority 83% of the time, two pathologists agree 73%, all seven on 34% of fields. About 1 in 6 test tiles is a 4-3 split, which caps any model at roughly 89-92% agreement with a fresh majority; the panel's 0.887 accuracy is at that ceiling | `data/mhist/annotations.csv` |
| Does weighting SSL vs HP differently change how well cases are ranked? | No: AUC is the same for every weight from 30/70 to 70/30; only the cut-off moves | [`weight_sweep_learning_curve.json`](results/weight_sweep_learning_curve.json) |
| Does more training data help? | Yes: AUC 0.878 / 0.896 / 0.906 with 25 / 50 / 100% of train | [`finetune_learning_curve.json`](results/finetune_learning_curve.json) |
| Do brightness/contrast/zoom adjustments at prediction time help? | No: all within +-0.002 AUC of the plain image | [`research/image_tta_sweep.py`](../research/image_tta_sweep.py) |
| Does the crypt finder outline crypts correctly? | On expert GlaS outlines (patients never seen in training), benign glands are found at F1 0.91, against 0.36 for the earlier rule-based finder, and a raw tile and a screen snip of it give nearly the same crypts (0.94) | [`crypt_finder.md`](results/crypt_finder.md) |
| Do the measured crypt labels agree with the pathologists? | Yes, modestly: dilated crypts track the pathologists' SSL votes (Spearman 0.45 on 1,575 held-out training images). Each alone separates SSL from HP weakly, so they explain, they don't decide | [`gland_check.json`](results/gland_check.json) |
| Is the scale bar read correctly? | Generated viewer screens (fonts 11-22 pt, black/white/yellow labels, um and mm, 125-150% display scaling): no wrong scales; QuPath's see-through corner bar is read on real QuPath screens (0.64 and 0.81 um/px), and on a demo sheet at four display sizes within 1%. When a bar can't be read, the app falls back to the tissue square | [`scale_stress.json`](results/scale_stress.json) |
| Does the app reproduce the reported test result? | Yes: the 977 test tiles sent through the app's own path as screen snips give balanced accuracy 0.886 (0.892 through a 150% display-scaling round trip) vs 0.888 reported | [`app_panel_check.json`](results/app_panel_check.json) |
| Is it fast and stable? | The panel's call is on screen in about 2 s; the literature reading follows in about 7-10 s; 25 analyses in a row plus overlapping re-snips complete with flat GPU memory | [`stability_check.json`](results/stability_check.json) |
| Does the evidence map show what drove the call? | Yes, by the deletion test on 120 held-out images: blurring the 15% the map ranks highest moves the score 4.5x more than a random 15% (98% of images) | [`map_faithfulness.json`](results/map_faithfulness.json) |
| Do the map and the crypt measurements agree? | In SSL fields, dilated crypts sit on SSL-pushing evidence about 3x more than round regular crypts (p = 0.009) | [`evidence_vs_crypts.json`](results/evidence_vs_crypts.json) |
| Does stain normalisation help? | No: Reinhard, Macenko, Vahadane and a derived method all score slightly below none | [`stain_compare.json`](results/stain_compare.json) |
| Does the unlike-training-data check work? | It flags all 16 non-tissue and wrong-stain test images and about 1% of MHIST fields; on other labs 9-21% of fields | [`research/export_panel.py`](../research/export_panel.py) |
| Is the literature reading well-behaved? | Rule breaks (invented citations, overclaiming, unmeasured evidence, absence claims, papers cited for the field itself) 0.80 per answer across 5 test fields x 3 runs, down from 1.13; about 7 s per field | [`literature_reading_eval.md`](results/literature_reading_eval.md) |
| Could a general vision LLM make the call? | No: Gemma-4 31B scores 0.554 balanced accuracy on the MHIST test images, calling 90% of them SSL | [`vlm_baseline.json`](results/vlm_baseline.json) |
| Is MHIST at its nominal scale? | Likely not: ~3.2-3.8 um/px (tiles ~720-860 um), from two independent rulers that agree | [`scale_audit.md`](results/scale_audit.md) |
| Would a bigger field help on other labs? | No: 448, 650 and 790 um give the same outside results | [`field_size_sweep.md`](results/field_size_sweep.md) |

Scope: trained on MHIST (one lab). It is strongest on MHIST-like fields and conservative on other labs' slides
([other labs](other_labs.md)); slides that look very different, e.g. much higher power or another stain, are flagged as unfamiliar. The
crypt finder can miss crypts cut lengthwise or open to the surface. Future work: predicting the mutation profile
(e.g. BRAF) from the image, which needs SSL slides with genotype labels (none are public yet), larger models, and
shared multi-lab consensus labels.
