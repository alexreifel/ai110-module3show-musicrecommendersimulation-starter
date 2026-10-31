# Project 3 core requirement audit

Sources re-read in the cloud browser on October 31, 2026:
- [Assignment: all five required phases](https://courses.codepath.org/courses/ai110/unit/7#!projects)
- [Official Project 3 rubric](https://courses.codepath.org/courses/ai110/pages/grading#heading-project-3-music-recommender-simulation)

Deadline shown: November 2, 2026, 17:29 GMT+09:30. Converted deadline:
November 2, 02:59 EST in New York / November 1, 23:59 PST in Los Angeles.
This is a reviewable build on GitHub, not a completed CodePath submission.

## All 21 required rubric points

Each subitem below is worth one point in the published rubric. This mapping is
a self-audit of evidence, not a guarantee of the instructor's grade.

| Category | Required subitem | Evidence |
|---|---|---|
| Recommender explanation | Describe how real systems use features/history | README: How The System Works, with Google primary sources |
| Recommender explanation | Distinguish data, user preferences, and ranking | README: data, preferences, scoring versus ranking |
| Recommender explanation | Specific and coherent ML explanation | Explicit content-based baseline, collaborative contrast, no training/accuracy claims |
| Dataset | At least 15–20 songs | `data/songs.csv`: 20 songs, preserving original 10 |
| Dataset | At least 3 meaningful attributes | Genre, mood, energy scored; remaining original attributes retained |
| Dataset | Valid and loads without errors | CSV loader plus schema/type/range/unique-ID tests |
| Scoring | Weighted/matching/similarity function | `score_song`: categorical matches plus energy closeness |
| Scoring | Consistent numeric output across catalog | Exact-value tests; all 20 songs evaluated |
| Scoring | Actual scoring reflects designed preferences | Genre/mood/energy explanations and feature-sensitive tests |
| Recommendations | Function ranks/sorts songs | `recommend_songs`, reused by class adapter |
| Recommendations | At least top 3 | CLI returns top 5 per profile |
| Recommendations | Works for different profiles | Three baseline profiles and adversarial case |
| Explanations | Every recommendation has a reason | Actual per-feature point contributions, including mismatches |
| Explanations | Accurate explanations saved as text | README output and model-card report match the executed scoring |
| Explanations | At least three readable explanations | Fifteen baseline song explanations in README plus evaluation evidence |
| Profiles | At least 3 distinct profiles | Pop/happy/0.80, lofi/chill/0.35, rock/intense/0.90 in `src/main.py` |
| Profiles | Run each and save outputs in code blocks | README and model card contain generated fenced text |
| Profiles | Comment on output differences | Model-card pairwise comparisons of all 3 required profiles, plus edge profile |
| Model card | Data, attributes, purpose | Model card sections 2 and 4 |
| Model card | Plain-language algorithm | Model card section 3 |
| Model card | Limitations/bias and improvement | Model card sections 6 and 8 |

## Phase-by-phase instruction checks

### Phase 1: Understand the problem

- Fork/clone: the existing personal fork was cloned; its 20-row catalog was kept.
- Research: README distinguishes collaborative and content-based filtering,
  identifies likes/skips/playlists as possible behavior data, and links Google's
  primary educational sources. This project does not claim to reproduce a
  specific proprietary platform's architecture.
- Feature choice and critique: genre, mood, and energy chosen for explainability;
  the other existing attributes are explicitly unscored. Narrow tastes, exact
  category matching, and genre dominance are documented limitations.
- Scoring and ranking are separately explained, including why closeness rather
  than raw high energy should be rewarded.
- README's How The System Works contains the concept and feature definitions.
- Source is ready to open in VS Code; no claim is made about operating Alex's
  local editor or about his having reviewed the code yet.

### Phase 2: Design

- The earlier data commit added 10 diverse synthetic songs, giving 20 total.
  No additional columns or optional advanced features were added.
- Explicit dictionary preferences differentiate pop, lofi, and rock; a conflicting
  classical profile tests the weaknesses of that representation.
- Recipe: 2 points genre, 1 point mood, 1 minus energy gap.
- A compact input → scoring → ranking → explained output plan is in README.
  The instructions explicitly say this sketch is not graded.
- Expected bias and the plan are documented in How The System Works.
- AI design discussions are represented by the build conversation and documented
  choices; no invented prompt logs or human actions are presented as executed.

### Phase 3: Implement

- Python `csv` loads dictionaries and converts ID/numeric music features.
- `Loaded songs: 20` appears in real CLI output.
- Scoring returns a numeric result plus a list of real reasons.
- Ranking loops through every song and returns top k descending.
- `.sort()` versus `sorted()` is explained; the input catalog is not reordered.
- `python -m src.main` runs and prints titles, scores, and reasons.
- Actual output is a fenced text block under Sample Recommendation Output.
- New functions have docstrings; model card explains the algorithm plainly.
- The implementation commit explicitly names a working CLI-first simulation.
- Starter import mismatch fixed; OOP and functional interfaces share scoring.

### Phase 4: Evaluate

- Three baseline dictionaries plus one adversarial/conflicting profile are run.
- Each prints top 5, with actual outputs committed as text and fenced in Markdown.
- A specific winner is explained with exact arithmetic (Sunrise City, 3.98).
- The required sensitivity experiment halves genre and doubles energy weight.
  It is a one-off evaluation on the same rule, not optional selectable strategies.
- The before/after rankings and point changes are recorded and interpreted.
- Model card includes 3–5 sentences describing observed bias/limitations.
- Every pair of the three required profiles is compared; the adversarial profile
  is also compared with each baseline.
- The musical-intuition discussion is explicitly a metadata-based assessment
  for Alex's review, not a fabricated claim of listening to fictional music.

### Phase 5: Model card and reflection

- All 9 sections in the starter model card are filled, including purpose,
  non-intended use, data, algorithm, strengths, bias, evaluation, and improvements.
- A proposed engineering/personal reflection answers all four website prompts
  using observed facts from the build. It identifies the AI assistance and does
  not claim Alex authored or tested the implementation independently.
- **Alex's review remains:** confirm/revise the reflection and the intuition
  assessment so they accurately reflect his own understanding and experience.

## Validation, scope, and submission

- 52 pytest cases pass locally; the original two tests are retained.
- CSV/header errors, numerical bounds, missing values, duplicate IDs, empty
  catalogs, invalid k, unknown categories, case/spacing, and stable ties tested.
- CLI/evaluation output saved in `evaluation/` and embedded in README/model card.
- CI runs pytest on Python 3.11/3.12 and verifies saved outputs reproduce exactly.
- The runtime is standard-library Python; only pytest needs installation.
- Public GitHub repository; three new coherent commits separate implementation,
  tests/evaluation, and documentation/CI. The earlier dataset commit remains.
- No optional additional attributes, diversity penalty, ranking-strategy system,
  or formatted result table was implemented. The starter stretch-only
  `ai_interactions.md` was left unchanged.
- A passing suite covers the specified cases, not all conceivable inputs or
  actual listener enjoyment. No measured recommendation accuracy is claimed.
- **Final submission still requires the user-reviewed repository URL in CodePath's
  Submit flow.** The user requested review and iteration before that step.
