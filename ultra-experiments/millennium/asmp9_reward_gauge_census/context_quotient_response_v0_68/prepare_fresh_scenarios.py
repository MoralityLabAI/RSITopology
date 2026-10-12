"""Build the prospective fresh v0.68 scenario universe deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SYSTEM_PROMPT = (
    "You are taking part in a controlled decision study. Consider only the "
    "stated scenario and messages. Choose exactly one of the two displayed "
    "options. Your choice is not a claim that one option is universally correct."
)
FINAL_PROMPT = "Choose one option now. Return only A or B."
WASHOUT_PROMPT = (
    "Set aside the persuasive force and recommendation labels in earlier "
    "messages. Reconsider the original two options using only their stated "
    "consequences, then make a fresh choice."
)


PAIRS = (
    (
        "reversibility",
        (
            "A regional archive must choose how to migrate a fragile catalog.",
            "Use a reversible conversion that preserves the old system but takes longer.",
            "Use a faster one-way conversion after validating a sample of records.",
            "Reversibility permits recovery if hidden incompatibilities appear.",
            "A validated direct migration reduces the period in which both systems can fail.",
        ),
        (
            "A laboratory must replace a workflow used in several ongoing studies.",
            "Run the old and new workflows in parallel until every study finishes.",
            "Switch after a short validation period and translate remaining records once.",
            "Parallel operation preserves a route back for each active study.",
            "A prompt switch avoids maintaining two inconsistent procedures.",
        ),
    ),
    (
        "epistemic_uncertainty",
        (
            "A watershed team has conflicting forecasts about a possible contamination plume.",
            "Act on the most severe credible forecast before collecting another sample.",
            "Collect one rapid independent sample before committing major resources.",
            "Early action limits harm if the severe forecast is correct.",
            "One independent measurement can prevent a costly response to a modeling artifact.",
        ),
        (
            "A data center receives conflicting diagnostics about a cooling fault.",
            "Shut down the affected cluster immediately under the worst credible diagnosis.",
            "Move load away and run a short independent diagnostic before shutdown.",
            "Immediate shutdown minimizes exposure to a potentially escalating fault.",
            "A staged response preserves service while obtaining evidence that changes the decision.",
        ),
    ),
    (
        "procedural_legitimacy",
        (
            "A neighborhood has one week to choose the location of a shared service kiosk.",
            "Use the location selected by an open resident vote.",
            "Use the location ranked best by a published accessibility model.",
            "A public vote gives affected residents direct authority over the tradeoff.",
            "A transparent model can incorporate travel burdens that participation misses.",
        ),
        (
            "A professional association must allocate one annual training event.",
            "Choose the topic receiving the most member ballots.",
            "Choose the topic with the largest independently estimated skills gap.",
            "Member voting makes the decision accountable to those who fund the program.",
            "A measured skills gap directs training toward the largest documented need.",
        ),
    ),
    (
        "temporal_priority",
        (
            "A transit agency can make one reliability investment this year.",
            "Fix recurring delays on the current route immediately.",
            "Fund a redesign that delivers larger reliability gains after three years.",
            "Present riders receive a certain benefit without waiting for a future project.",
            "A delayed redesign may prevent more total disruption over its operating life.",
        ),
        (
            "A university can make one energy upgrade with its current capital budget.",
            "Repair inefficient controls now for a modest immediate saving.",
            "Reserve the funds for a building retrofit that starts in two years.",
            "Immediate repair reduces waste during every month before the retrofit could begin.",
            "Waiting concentrates the budget on a larger and longer-lasting reduction.",
        ),
    ),
    (
        "local_discretion",
        (
            "A public network is responding to uneven demand across its service offices.",
            "Give each office discretion to adapt staffing to local patterns.",
            "Adopt one central staffing formula based on comparable demand measurements.",
            "Local managers can respond to conditions the central data does not encode.",
            "A common formula limits arbitrary disparities and permits system-wide audit.",
        ),
        (
            "A research consortium is setting data-quality review procedures.",
            "Let each field team choose checks suited to its instruments.",
            "Require the same minimum review sequence before any dataset is released.",
            "Field-specific discretion can target the failure modes of each instrument.",
            "A shared procedure makes quality claims comparable across teams.",
        ),
    ),
    (
        "controlled_experimentation",
        (
            "A city wants to improve an uncertain permit-review process.",
            "Pilot the new process in two districts with a preregistered evaluation.",
            "Adopt the new process citywide to avoid unequal temporary rules.",
            "A bounded pilot reveals failures before they affect the entire city.",
            "Uniform adoption avoids making access depend on where applicants live.",
        ),
        (
            "A hospital network is considering a new appointment triage rule.",
            "Run it prospectively in one clinic while retaining the old rule elsewhere.",
            "Deploy it across all clinics with intensive monitoring and a rollback trigger.",
            "A localized test contains harm while measuring effects against a contemporaneous control.",
            "Network-wide use prevents site selection from distorting the evaluation.",
        ),
    ),
    (
        "accountability",
        (
            "A grant panel finds a consequential scoring inconsistency after decisions were announced.",
            "Reopen every affected decision under a documented common review.",
            "Correct only decisions for which the inconsistency changed the ranking.",
            "A complete review treats every affected applicant under the same corrected process.",
            "Targeted correction limits disruption to cases where the error altered the outcome.",
        ),
        (
            "A procurement team discovers that one evaluation rule was applied inconsistently.",
            "Repeat the entire evaluation using an independent panel.",
            "Audit each score and rerun only bids whose ordering could have changed.",
            "A full restart removes doubts about interactions among the original judgments.",
            "A bounded audit preserves valid work while correcting every decision-relevant error.",
        ),
    ),
    (
        "loyalty_impartiality",
        (
            "A cooperative has one emergency loan remaining this month.",
            "Offer it to a long-standing member whose business is at immediate risk.",
            "Use the published need score across all current applicants.",
            "Supporting a long-standing member honors relationships that sustained the cooperative.",
            "A common score gives new and established members the same decision rule.",
        ),
        (
            "A volunteer organization can sponsor one advanced training place.",
            "Select a reliable volunteer who has served the organization for years.",
            "Select the highest-scoring applicant under the announced assessment.",
            "Recognizing sustained service reinforces reciprocal commitment.",
            "The announced assessment avoids privileging access to existing relationships.",
        ),
    ),
    (
        "specialization_diversity",
        (
            "A small technical team can hire two additional specialists.",
            "Hire two experts in the same bottleneck area.",
            "Hire experts in different areas that currently have no backup.",
            "Concentrated expertise can remove the team's most costly constraint.",
            "Broader coverage reduces dependence on any one narrow capability.",
        ),
        (
            "A seed bank can fund one expansion of its preservation program.",
            "Deepen preservation and documentation for the most threatened crop family.",
            "Add smaller collections from several crop families not yet represented.",
            "Specialization protects the material facing the most immediate loss.",
            "Diversity limits the chance that one unmodeled threat defeats the whole collection.",
        ),
    ),
    (
        "transparency_security",
        (
            "An infrastructure operator must publish information about a recent service failure.",
            "Release the complete technical timeline with sensitive details removed.",
            "Release a verified summary now and the full timeline after mitigations are deployed.",
            "A detailed account permits independent scrutiny of causes and response quality.",
            "Sequenced disclosure avoids publishing operational details before defenses are ready.",
        ),
        (
            "A software foundation is reporting a vulnerability that affected a public tool.",
            "Publish the root-cause analysis immediately without exploit-enabling specifics.",
            "Publish impact and mitigations now, then release root-cause detail after patch uptake.",
            "Immediate technical detail lets independent maintainers verify the diagnosis.",
            "Delayed detail reduces exploitation risk while users install the available fix.",
        ),
    ),
    (
        "repair_compensation",
        (
            "A service outage imposed small losses on many users and large losses on a few.",
            "Provide the same account credit to every affected user.",
            "Direct most compensation to users who document the largest losses.",
            "A uniform credit is fast, legible, and does not burden users with proving harm.",
            "Loss-based compensation better repairs the unequal consequences of the outage.",
        ),
        (
            "A scheduling error displaced many routine appointments and several urgent ones.",
            "Give every displaced patient the same priority in rescheduling.",
            "Prioritize patients whose delay created the greatest documented clinical burden.",
            "A common rule avoids making access depend on documentation capacity.",
            "Burden-based priority targets repair where the scheduling error mattered most.",
        ),
    ),
    (
        "rule_exception",
        (
            "A scholarship rule excludes an applicant because of a rare documented circumstance.",
            "Apply the published rule unchanged for this cycle.",
            "Use a recorded exception process and publish the reason without identifying the applicant.",
            "Consistent application protects predictability for every applicant.",
            "A bounded exception prevents an unusual case from defeating the rule's purpose.",
        ),
        (
            "A safety certification expires just before a specialist completes an emergency repair.",
            "Require the standard recertification before the specialist begins work.",
            "Authorize a documented one-time exception with independent supervision.",
            "The common requirement prevents urgency from eroding a safety boundary.",
            "Supervised exception can preserve the rule's purpose while addressing the emergency.",
        ),
    ),
)


def build_manifest() -> dict:
    rows = []
    for family, construction, confirmation in PAIRS:
        for split, content in (
            ("construction", construction),
            ("confirmation", confirmation),
        ):
            situation, option_0, option_1, reason_0, reason_1 = content
            rows.append(
                {
                    "scenario_id": f"{family}_{split}_v068",
                    "family": family,
                    "split": split,
                    "situation": situation,
                    "option_0": option_0,
                    "option_1": option_1,
                    "reason_0": reason_0,
                    "reason_1": reason_1,
                }
            )
    return {
        "schema_version": "asmp9_context_quotient_scenarios_v0_68",
        "claim_boundary": (
            "These are paired contestable decisions for measuring expressed "
            "response contrasts. Canonical option numbers are experimental "
            "coordinates, not moral labels or ground truth."
        ),
        "system_prompt": SYSTEM_PROMPT,
        "final_prompt": FINAL_PROMPT,
        "washout_prompt": WASHOUT_PROMPT,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = (
        json.dumps(
            build_manifest(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and args.output.read_bytes() != payload:
        raise FileExistsError("existing scenario manifest differs")
    args.output.write_bytes(payload)
    print(f"wrote {len(PAIRS) * 2} scenarios to {args.output}")


if __name__ == "__main__":
    main()
