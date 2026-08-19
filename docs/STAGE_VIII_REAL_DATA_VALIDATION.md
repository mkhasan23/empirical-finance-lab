# Stage VIII — Real-data external validation

## Status

**Stage VIII-C scientific parity: PASS.**

**Stage VIII real-data external-validation evidence: ACCEPTED on `main` at `a694d49df9716f9f87d359385598237363e4c3fc`.**

Accepted repository tree: `621b0cafdcad3711d2aba3bef698d2e78d022144`.

This record documents a five-case real-data validation exercise performed after the Stage VII release-hardening baseline and main-branch governance were accepted. It is evidence of numerical parity on selected real CRSP cases; it is **not** a claim that CRSP data are redistributed with EFL, that the five events form a representative economic sample, or that event-study identification is causal.

## Acceptance record

The governed Stage VIII branch head was `6122a2b5ff0aaada0acb042b5d8f1d73621d7beb`. Pull request #10 was squash-integrated to `main` at `a694d49df9716f9f87d359385598237363e4c3fc`. The validated branch tree, the pull-request merge-candidate tree, and the resulting squash-merged main tree were identical (`621b0cafdcad3711d2aba3bef698d2e78d022144`).

Fresh main-push validation then passed Stages III–VIII on that exact main baseline:

- Stage III corpus integrity #68;
- Stage IV numerical core #66;
- Stage V browser runtime parity #63;
- Stage VI application UI #53;
- Stage VII release hardening #44; and
- Stage VIII real-data evidence #5.

Stage VI run `32210822522` failed on its first attempt only because the WebKit researcher-journey test stalled during browser-runtime initialization. The failed jobs were rerun on the same commit; attempt 2 passed preflight, Chromium, Firefox, WebKit, and the `stage6-required` wrapper. No source change was made in response, so this is recorded as a transient browser/runtime event rather than a scientific or application correction.

This acceptance record is reporting/governance only. It does not redefine the frozen scientific-core anchor below and does not declare Public Beta, `v0.1.0`, or a DOI.

## Frozen software anchor

The validation targets the EFL scientific-core baseline at:

`ebbb1d0629f9fd1a128ff3d09f1494bbcaf1fb39`

No Stage VIII code changes to the Stage IV numerical authority were used to manufacture the result.

## Prespecified design

The same specification was applied to all five cases before examining the EFL parity results:

- market model;
- estimation window `[-256,-46]` (211 trading observations when complete);
- event window `[-1,+1]` (3 trading observations);
- decimal simple returns;
- CRSP value-weighted market return as benchmark;
- two-sided inference;
- `B=1000` single-firm permutations;
- PCG64 seed `20260817`;
- placebo disabled for this validation tranche; and
- no robustness variants in this validation tranche.

Event-time indexing follows actual trading-row positions around the explicitly confirmed effective event trading date, not calendar-day subtraction.

## Five validation cases

| Case | Company | Event | Calendar announcement date | Effective trading date | Timing classification |
|---|---|---|---|---|---|
| MSFT | Microsoft | Activision Blizzard acquisition announcement | 2022-01-18 | 2022-01-18 | during/before market |
| PG | Procter & Gamble | quarterly dividend increase | 2024-04-09 | 2024-04-10 | after market |
| NVDA | NVIDIA | Q1 FY2025 earnings announcement | 2024-05-22 | 2024-05-23 | after market |
| WMT | Walmart | FY2025 Q3 earnings release | 2024-11-19 | 2024-11-19 | during/before market |
| KO | Coca-Cola | CEO succession announcement | 2025-12-10 | 2025-12-11 | after market |

### Public event-timing sources

- Microsoft acquisition announcement: `https://news.microsoft.com/source/2022/01/18/microsoft-to-acquire-activision-blizzard-to-bring-the-joy-and-community-of-gaming-to-everyone-across-every-device/`
- P&G dividend announcement: `https://www.sec.gov/Archives/edgar/data/80424/000008042424000029/april2024dividendrelease.htm`
- NVIDIA earnings timing: `https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Sets-Conference-Call-for-First-Quarter-Financial-Results/default.aspx`
- Walmart FY2025 Q3 earnings event: `https://corporate.walmart.com/news/events/fy2025-q3-earnings-release`
- Coca-Cola CEO succession announcement: `https://investors.coca-colacompany.com/news-events/press-releases/detail/1147/the-coca-cola-company-announces-ceo-succession-plan-chief-operating-officer-henrique-braun-to-succeed-james-quincey-as-ceo-in-2026`

## Licensed input boundary

The original local CRSP extract is anchored by SHA-256:

`68d365faad1290ac01d9d07b64cdb037375d234aa5298e25b94897989d2a1557`

The private source contained the five intended securities and daily return/benchmark observations over the common extraction period. It is **not included in this repository**. The five derived EFL input CSVs are also private and are not committed.

Only hashes, locked specifications and numerical summaries are public. A hash proves identity of a private artifact if the authorized researcher possesses it; it does not reconstruct or redistribute the underlying observations.

## Parity results

| Company | CAR `[-1,+1]` | Classical t | Classical p | Permutation p | Extreme count | Max absolute comparison delta |
|---|---:|---:|---:|---:|---:|---:|
| MSFT | +0.0206094438 | 1.1913579821 | 0.2348642438 | 0.224 | 224 | 2.2204460493e-16 |
| PG | -0.0008648879 | -0.0537647708 | 0.9571739985 | 0.951 | 951 | 1.1102230246e-16 |
| NVDA | +0.1147782718 | 2.4129990527 | 0.0166846735 | 0.018 | 18 | 4.3368086899e-18 |
| WMT | +0.0271899951 | 1.3037360714 | 0.1937577757 | 0.105 | 105 | 2.2204460493e-16 |
| KO | +0.0054198631 | 0.2818511142 | 0.7783365601 | 0.785 | 785 | 2.7755575616e-16 |

Maximum observed absolute numerical delta across the scientific comparison fields:

`2.7755575615628914e-16`

EFL's established browser-parity tolerances are:

- absolute tolerance: `1e-12`;
- relative tolerance: `1e-10`; and
- p-value/tail-proportion tolerance: `1e-10`.

Every numerical comparison passed, and every permutation extreme count matched exactly.

## What the CI gate proves

`tools/check_stage8_real_data_gate.py` is intentionally a **public-evidence integrity gate**. Because licensed CRSP observations are excluded from the repository, public CI cannot independently reconstruct the five event studies from source observations.

The gate therefore verifies that:

1. the expected five cases and frozen design are present;
2. the evidence and specification files have the expected SHA-256 identities;
3. specification hashes and analysis IDs are internally consistent with EFL's canonical hashing rules;
4. every recorded numerical comparison satisfies the frozen parity tolerance;
5. permutation extreme counts match exactly;
6. JSON and CSV summaries agree on the key scientific quantities;
7. the immutable raw CRSP source hash is preserved; and
8. known private Stage VIII data artifacts have not been committed by filename or exact file hash.

This is deliberately narrower than a live-data replication gate. A full CRSP re-run requires authorized local access to the private input files.

## Interpretation boundary

The Stage VIII exercise validates **numerical implementation and cross-implementation parity** on heterogeneous real events. It does not establish that each event caused the observed return, that the chosen companies constitute a random sample, or that the resulting p-values have causal interpretation. EFL's audit/referee layer remains responsible for keeping computation distinct from identification.

Acceptance of this evidence is also distinct from release-state promotion: EFL remains pre-release, not Public Beta, with no formal `v0.1.0` release and no version-specific DOI.
