[← README](../README.md)

# The image panel

### Data

MHIST: 3,152 H&E tiles of colorectal polyps (224 x 224 px, Dartmouth-Hitchcock), each labelled with how
many of 7 GI pathologists called it SSL.

| Split | HP | SSL | Total |
|---|---|---|---|
| Train | 1,545 | 630 | 2,175 |
| Test (official, fixed) | 617 | 360 | 977 |

The goal is to match the pathologists' consensus. The headline metric is **balanced accuracy** (SSL and
HP count equally), so the panel cannot score well by leaning toward the more common class.

### Members

Four candidates were trained; the panel-building rule (below) chose **ConvNeXt-Base + MUSK**.

| Candidate | Type | Training | Learning rate | Input | Cross-validated AUC (train) | In the panel |
|---|---|---|---|---|---|---|
| ConvNeXt-Base | ImageNet CNN | Classifier first, then all layers | 1e-4 | 224 px | 0.962 | **Yes** (weight 1.13) |
| MUSK | Pathology vision-language model (ViT-L) | Classifier first, then LoRA (rank 8) on the attention of all 24 layers | 1e-4 | 384 px | 0.946 | **Yes** (weight 0.64) |
| PLIP | Pathology vision-language model | Classifier first, then all layers | 1e-5 | 224 px | 0.951 | No |
| CONCH | Pathology vision-language model | Classifier first, then all layers | 1e-5 | 224 px | 0.949 | No |

### Training recipe (all members)

| Choice | Setting | Why |
|---|---|---|
| Target | Share of the 7 pathologists who called SSL (e.g. 5/7 = 0.71) | Learns the consensus, including how split it was |
| Class balance | Each SSL image weighted 2.45 (= 1,545 HP / 630 SSL) | Both classes carry equal total weight, matching balanced accuracy |
| Classifier first | 1 epoch training only the classifier, then up to 8 fine-tuning epochs, best epoch kept | Fine-tuning starts from a sensible classifier, so the model's existing knowledge is adjusted gently |
| Learning rate | 1e-5 for full fine-tuning of pathology models, 1e-4 for the CNN and for LoRA | Standard rates for each kind of fine-tuning on small data |
| Image variation (training only) | Flips, 90-degree rotations, mild brightness/contrast/saturation/hue jitter | Robust to lighting and stain differences; predictions use the image as-is, so a snip always gets the same score |
| Precision | bf16 activations, fp32 weights | Full fine-tuning fits on an 8 GB laptop GPU |

### Building the panel

| Step | What happens |
|---|---|
| Cross-validation | Each member is trained 5 times on 4/5 of the training images (same folds for all), so every training image gets a prediction from a model that never saw it |
| Every combination | All 15 groups of members are scored, each with one learned weight per member |
| Selection | The best group by AUC; among groups within 0.003 AUC of it, the smallest wins. All four scored 0.9662; ConvNeXt-Base + MUSK scored 0.9655 and was chosen (ConvNeXt-Base alone, 0.9622, was not close enough) |
| Calibration | The displayed percentage is calibrated to the 7-pathologist majority call, so "80%" means the majority says SSL about 80% of the time on MHIST-like fields |
| Cut-off | Set to maximise balanced accuracy on the training images: SSL above a calibrated 27%, which the app displays as a score of 50% |
| Final models | Each chosen member is retrained once on all 2,175 training images; the app runs these |
| Evaluation | The 977 test images are scored once, on the exact version the app runs |

All choices are made on training images; the test split is used only for the final score.
