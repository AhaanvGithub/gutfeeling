[← README](../README.md)

# Other labs' slides

None of these were used for training. They test how far the MHIST-trained panel carries to other hospitals.

| Dataset | What it is | Result |
|---|---|---|
| UniToPatho (Turin) | 545 HP crops, 41 slides; also adenoma and normal colon | 99.6% of HP called HP, and every adenoma and normal field; crypt measurements follow the biology (serrated crypts 27% of labelled crypts in HP, 6% in adenoma, 3% in normal colon); 11-21% flagged unfamiliar. No SSL, so SSL detection is untested here ([`unitopatho_panel_check.json`](results/unitopatho_panel_check.json)) |
| SPIDER-colorectal | 10,886 fields from many slides, SSL and HP labelled by region | HP cleared 99.8% (5,893 fields), SSL caught 6.0% (4,993 fields); 9.5% flagged unfamiliar. Its SSL fields measure the same as its HP fields on every crypt measure (in MHIST and HunCRC, SSL halves crypt density), consistent with region-level labels ([`spider_panel_rows.jsonl`](results/spider_panel_rows.jsonl), [`scale_audit.md`](results/scale_audit.md)) |
| HunCRC (Budapest) | 24 HP slides and one SSL slide (lesion area not marked) | HP slide fields 93% called HP; 4% of the SSL slide's fields called SSL, partly because much of that slide is normal or unusable tissue ([`field_size_sweep.md`](results/field_size_sweep.md)) |

The honest picture: the panel is strong where it was trained and conservative elsewhere: it keeps HP right but
under-calls SSL on other labs' slides. Two causes were tested:

- **Scale.** MHIST's tiles are likely about 720-860 um, not the nominal 448 um: crypt geometry and lymphocyte size,
  two independent rulers, both read about 1.9x against UniToPatho's known scale ([`scale_audit.md`](results/scale_audit.md)). But scoring
  outside fields at 650 and 790 um did not bring out SSL ([`field_size_sweep.md`](results/field_size_sweep.md)), so scale is not the reason.
- **Labels and labs.** Each outside set is labelled by its own lab, sometimes by region; pathologists themselves
  agree on SSL vs HP only about three-quarters of the time. Shared consensus labels, or molecular markers such as
  BRAF, are what the field needs to measure this properly.
