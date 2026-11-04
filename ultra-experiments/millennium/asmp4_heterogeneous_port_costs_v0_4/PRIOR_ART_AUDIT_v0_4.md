# ASMP-4 bounded prior-art audit v0.4

## Conclusion

This targeted primary-source audit supports the scope boundary but does not
support a broad mathematical novelty claim.

The scalar causal data-rate object, genuine multi-owner Pareto rate regions,
cascade relay/recompression tradeoffs with middle-node information, and
zero-delay causal prefix effects all have clear prior art. The defensible
repository contribution is narrower: the frozen ASMP-4 architecture combines a
single serial chain, no controller or actuator side information, arbitrary
registered deterministic computation, and the same achieved-transcript cost
on both ports. Under precisely those conventions, the bilateral normal forms
show that the proposed two independent thresholds collapse. The v0.4 prefix
game is an exact boundary illustration, not a claimed first heterogeneous
source-coding frontier. Its exact finite theorem does range over every binary
prefix-free codebook for the registered four-plan law, rather than only two
named formats.

External expert review is still required. This audit used targeted searches and
five directly relevant primary sources; it is not a systematic review or a
priority claim.

## Primary-source comparison

| Source | Established object | Relevance to ASMP-4 | Claim consequence |
| --- | --- | --- | --- |
| Tomar, Rungger, Zamani, *Invariance Feedback Entropy of Uncertain Control Systems* (2017/2019), https://arxiv.org/abs/1706.05242 | Introduces invariance feedback entropy and proves a tight coder-controller data-rate theorem for uncertain invariance. | Supplies the history-dependent causal branching object that v0.2 initially conflated with total terminal-language growth. | The causal entropy and its control interpretation are prior art; v0.3's comb fixture is a definition correction, not a new entropy. |
| Kawan, Delvenne, *Network entropy and data rates required for networked control* (2014), https://arxiv.org/abs/1409.6037 | Defines subsystem invariance entropies and a closed convex set of Pareto-optimal rate vectors for networks of controlled subsystems. | Shows that genuinely multidimensional control-rate regions already exist when distinct subsystems own different information. | ASMP-4 cannot claim novelty from “two rates” alone; its issue is whether its single serial chain actually has two independent information owners. |
| Cuff, Su, El Gamal, *Cascade multiterminal source coding* (2009), https://arxiv.org/abs/0905.1883 | Gives inner/outer rate-region bounds for a cascade where the middle encoder has its own correlated source, with relay versus recompression tradeoffs. | The middle node's source `Y` is exactly the kind of controller-local information that blocks upstream simulation in ASMP-4. | Nonrectangular cascade tradeoffs with middle-node information are prior art. The no-side-information normal form is a degenerate structural specialization, not a replacement for cascade source-coding theory. |
| Kaspi, Merhav, *Zero-Delay and Causal Single-User and Multi-User Lossy Source Coding with Decoder Side Information* (2013), https://arxiv.org/abs/1301.0079 | Characterizes zero-delay causal/instantaneous-code settings and shows optimal time sharing between at most two scalar encoder-decoder pairs in a single-user case. | Closely parallels v0.4's synchronous prefix-factor constraint and two-endpoint time-sharing segment. | The qualitative zero-delay and time-sharing phenomena are prior art; v0.4 contributes only an exact ASMP boundary fixture for its four-plan law and deadline. |
| Guo, Kostina, *Optimal Causal Rate-Constrained Sampling of the Wiener Process* (2019), https://arxiv.org/abs/1909.01317 | Shows that event timing can itself carry free information and changes causal operational performance. | Confirms that ASMP-4 must charge timing or freeze a public schedule before treating transcript symbols as the complete information resource. | Timing-compatible public FIFO delivery is load-bearing; private/event-triggered schedules require a new timing-rate coordinate. |

## What appears classical

The following ingredients should be presented without novelty language:

- deterministic data processing from read words to write words;
- moving a deterministic computation to a node that already has all its
  inputs;
- identity relaying in a cascade without intermediate side information;
- Kraft inequalities and minimax prefix-code recurrences;
- causal prefix-partition refinement as the criterion for a synchronous
  deterministic transducer;
- convexification by public time sharing; and
- Lyapunov/invariance-entropy lower bounds for unstable controlled systems.

## What is specific to this repository result

The useful synthesis is the requirement-level diagnosis:

1. The frozen displayed `R_K` charges the same realized complete-transcript
   functional on both serial ports.
2. The middle and downstream nodes have no independent plant information.
3. Arbitrary registered computation and relabelable alphabets permit both
   upstream and downstream component simulation.
4. Therefore either coordinate-minimizing transcript tree can be copied onto
   both ports, forcing one scalar threshold and a rectangular closed region.
5. Terminal-language, causal-branching, and minimax-prefix costs can have
   different scalar values, but the same bilateral argument applies when one
   such cost is shared and fixed-prefix invariant.
6. Positive unit conversions preserve this structure, while heterogeneous
   cost orderings plus a causal factorization deadline can recover a Pareto
   frontier.

This combination is a strong answer to the internal ASMP-4 wording. Whether an
equivalent normal-form theorem has already appeared verbatim in networked
control or functional cascade coding remains an external-review question.

## Search boundary

The audit intentionally used primary papers and did not infer novelty from a
failure to find an exact phrase. A publishable claim would require, at minimum,
a broader search of output invariance entropy, functional compression over
cascade networks, zero-error causal source coding, decentralized control, and
two-link networked control, followed by review from specialists in both control
and information theory.
