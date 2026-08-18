# ASMP-10 v0.4.2 spike-consequence table

Post-hoc descriptive output over burned v0.4 cells. The spike rule is unchanged from v0.4.1 and no gate consumes this table.

## Aggregate

- Spikes: 15 (7 excursion-causing; 8 not).
- Excursion spikes among the seven largest train-loss ratios: 6/7.
- Excursion spikes among the seven largest gradient ratios: 4/7.
- Median train-loss ratio, excursion versus non-excursion: 66.72 versus 20.52.
- Median gradient ratio, excursion versus non-excursion: 5530.38 versus 1229.00.
- Median steps since crossing, excursion versus non-excursion: 5800 versus 4150.

The seven excursion-causing spikes are not simply the seven largest under either component of the registered spike rule. This leaves state dependence live as a descriptive possibility, but the six-cell pilot cannot identify it.

## Records

| run | step | since crossing | loss ratio | gradient ratio | loss rank | gradient rank | excursion | down threshold |
|---|---:|---:|---:|---:|---:|---:|:---:|:---:|
| seed07_tf055_wd100 | 2400 | 500 | 92.45 | 5816.60 | 2 | 4 | yes | yes |
| seed07_tf055_wd100 | 4000 | 2100 | 87.15 | 5940.39 | 3 | 3 | no | no |
| seed07_tf055_wd100 | 4400 | 2500 | 504.74 | 11614.88 | 1 | 1 | yes | yes |
| seed07_tf055_wd100 | 7700 | 5800 | 66.72 | 6923.40 | 5 | 2 | yes | yes |
| seed07_tf055_wd100 | 9300 | 7400 | 21.11 | 890.59 | 9 | 11 | no | no |
| seed07_tf055_wd100 | 11300 | 9400 | 20.42 | 188.55 | 11 | 15 | no | no |
| seed07_tf055_wd100 | 14800 | 12900 | 53.26 | 979.04 | 6 | 10 | yes | no |
| seed07_tf055_wd200 | 3200 | 1900 | 20.61 | 462.17 | 10 | 12 | no | no |
| seed07_tf070_wd100 | 3100 | 2200 | 17.26 | 1567.40 | 12 | 9 | no | no |
| seed07_tf070_wd100 | 3400 | 2500 | 11.34 | 369.66 | 15 | 13 | no | no |
| seed07_tf070_wd100 | 4700 | 3800 | 39.08 | 5530.38 | 7 | 6 | yes | no |
| seed07_tf070_wd100 | 6700 | 5800 | 26.59 | 5232.10 | 8 | 7 | no | no |
| seed07_tf070_wd100 | 7000 | 6100 | 82.91 | 2742.48 | 4 | 8 | yes | yes |
| seed07_tf070_wd100 | 13200 | 12300 | 13.15 | 5635.44 | 13 | 5 | no | no |
| seed07_tf070_wd200 | 13200 | 12800 | 12.89 | 195.67 | 14 | 14 | yes | no |

## Boundary

Describes the burned v0.4 cells only. Magnitude ranks and timing do not define a predictor, causal mechanism, or confirmation hypothesis.
