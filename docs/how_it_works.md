[← README](../README.md)

# How it works

| Stage | What happens |
|---|---|
| Capture | The screen is captured in true colour (Windows GDI, through the backend) the moment the hotkey is pressed; the snip view shows that screenshot, so it looks like the live screen |
| Field size | The viewer's scale bar is read first in the bottom-left corner (QuPath draws a see-through bar there), then anywhere: the bar is found as a thin line, its label with Windows' built-in OCR. A label must be a round scale value and must sit centred on its bar, so a misread gives no scale rather than a wrong one. The field is then exactly 448 um; without a bar, tissue is separated from glass and viewer chrome by colour |
| Image panel | ConvNeXt-Base (88M parameters) and MUSK (305M, LoRA) each score the field; a learned, calibrated combination gives the probability that a 7-pathologist majority would call SSL. The displayed score puts the cut-off at 50%, so an SSL call always reads above 50%; the underlying probability is one click away |
| Unlike-training-data check | The field's ConvNeXt features are compared with the 2,175 training images; beyond what 99% of training images reach, the field is flagged. Far beyond anything real tissue reached (photos, noise, screen content), the crypts and the literature reading are skipped |
| Evidence map | Each region of the field is blurred out in turn and the change in ConvNeXt's score is recorded: 16 x 16 regions first, refined to 32, 64 and 128 while the rest runs |
| Crypts | A U-Net (ConvNeXt-Base encoder) trained on GlaS expert gland outlines finds the crypts; each is measured in um and labelled dilated (wider than the field's other crypts and above the MHIST threshold) or round and regular |
| Similar cases | The field's ConvNeXt features are compared with 454 labelled reference fields from other labs: 214 SSL (pathologist-labelled SPIDER fields from 71 slides, plus HunCRC) and 240 HP (UniToPatho). The three most similar of each class are shown, with which class is closer |
| Literature reading | An LLM (Gemma-4 31B on Lumen) explains the panel's call from what was measured on this field (crypts, their positions, the evidence map, the unfamiliar-slide flag) and from five excerpts retrieved from a curated library. It never sees the image and never overrules the panel: it gives a confidence (capped at 92%), at most two measured points for the call and one against, and at most two located things to check by eye. Three runs; the answer shown is the cleanest, checked in code for invented citations, overclaiming, unmeasured evidence and claims of absence |

### Design decisions

| Decision | Why |
|---|---|
| Score one square field, the size MHIST tiles show (448 um) | The models learned SSL vs HP at that field; a different size or shape changes what they see (a bigger field was tested and did not help: [other labs](other_labs.md)) |
| Read the scale bar to size the field | Viewers zoom freely; a known scale is the direct way to show the models exactly one training-sized field |
| Panel of an ImageNet CNN and a pathology model | They make different mistakes; together they beat any single model on training data |
| Fine-tune instead of frozen features | Frozen features reach ~0.80 balanced accuracy on MHIST; fine-tuning reaches 0.89 ([results](results.md)) |
| Calibrate to the 7-pathologist consensus | There is no clean ground truth for SSL vs HP: on MHIST two pathologists agree 73% of the time and all seven on 34% of fields. The panel learns the consensus, including how split it was |
| Display score with the cut-off at 50% | The balanced cut-off is a calibrated 27%; showing "SSL 30%" for an SSL call reads as a contradiction |
| The image models decide; the LLM explains | The image models are trained and validated; a general vision LLM given the same images scores 55% balanced accuracy ([results](results.md#could-a-general-vision-llm-do-this)). The literature reading always takes the panel's call |
| Confidence capped at 92% | Experts don't agree more than that: a single pathologist matches the MHIST majority 83% of the time |
| Similar cases from other labs, per class | Real labelled precedent instead of an opinion; per-class nearest neighbours, because the pools differ in size |
| Fast and quiet | Pathologists read ~100 slides a session: no splash, no counting-up numbers, no streaming text; transitions are short fades |
| No stain normalisation | Every method tested scored slightly worse than none, on MHIST and on simulated labs |
| Evidence map by blurring regions out | It measures what actually moved this call, at the field size the model was trained on |
| Crypts measured, not matched to text | Text-matched "feature scores" (CONCH) located features poorly and contradicted each other; they were dropped. Measured outlines follow real glands |
| Warn on unfamiliar input | Trained on two classes only, the panel would otherwise call anything (glass, photos, other stains) HP |
| Every number from training data; the test split scored once | So the reported results show what to expect on new slides |
