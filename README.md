# Music Recommender Simulation

A CLI-first, content-based recommender for a 20-song synthetic catalog. It scores
songs against a taste profile, returns the top five, and explains every score.
This is a classroom simulation with hand-chosen weights, not a trained model,
Spotify integration, or predictor of real listening enjoyment. No API key or
network service is required to run it.

## How The System Works

Real recommendation systems can use item attributes (genre, tempo, mood) and
behavioral signals (plays, likes, skips, playlists). Content-based filtering
matches an item's attributes to a user's preferences. Collaborative filtering
uses patterns in user-item feedback, allowing suggestions based on other users'
behavior. This project implements only the first approach: it has song features
and explicit preferences, but no history or interactions from actual listeners.
A score is a designed relevance measure, not a probability that someone likes a
song. In a large catalog, candidate selection and ranking can be separate stages;
this simulator simply scores all 20 songs.

Sources used for the conceptual review:
- [Google: Content-based filtering](https://developers.google.com/machine-learning/recommendation/content-based/basics)
- [Google: Collaborative filtering](https://developers.google.com/machine-learning/recommendation/collaborative/basics)

### Data and preferences

`data/songs.csv` preserves the original 10 songs and adds 10 fictional, AI-generated
tracks spanning additional genres/moods. Values are illustrative labels, not
measurements of actual audio or real artists. The CSV columns are `id`, `title`,
`artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and
`acousticness`. Normalized features must be in [0, 1]; tempo must be positive;
IDs must be unique positive integers. The loader converts numeric strings to
numbers and reports malformed data with a row number.

The baseline scores **genre, mood, and energy only**. Tempo, valence,
danceability, and acousticness are stored as part of the starter schema but do
not affect ranking. Profile dictionaries contain `genre`, `mood`, and target
`energy`. The starter `UserProfile` names map to these keys. Its `likes_acoustic`
field is retained for compatibility but is not scored; no acoustic preference
is claimed to influence the results.

### Algorithm recipe and design critique

```text
score = 2 * genre_match + 1 * mood_match + 1 * (1 - abs(song_energy - target_energy))
```

A categorical match is 1 and a mismatch is 0. With valid energies, the closeness
term lies between 0 and 1, so the baseline total lies between 0 and 4. This rewards
nearness to the target rather than simply rewarding high energy. For example,
0.3 is a better energy match than 0.9 when the target is 0.35. Genre and mood
labels are stripped and case-insensitive, but synonyms/subgenres are not merged.

The planned tradeoff is explicit: genre gets more weight than mood or energy.
This separates intense rock from chill lofi, but can over-prioritize genre when
preferences conflict. A three-feature profile is explainable but narrow: it
cannot express mixed genres, changing context, lyrics, or acoustic preferences.
The baseline's limitations are examined in `model_card.md` rather than hidden
by adding optional extensions.

Scoring judges one song; ranking compares all scored songs. `score_song` returns
`(numeric_score, reasons)`. `recommend_songs` returns `(song, score, explanation)`
tuples in descending score order. Scores are rounded to 12 decimal places to
remove floating-point noise in mathematical ties, which preserve CSV input order.
This tie-break is deterministic, not evidence that the first tied song is better.
Python's `sorted()` creates a new list; `.sort()` changes an existing list in place.
The implementation uses `sorted()` so ranking does not reorder the input catalog.

Planning flow: CSV + explicit preferences → validate and load → score each song
→ sort scores → return five songs with source feature contributions.

### Files and compatibility

- `src/recommender.py`: CSV loading, scoring, ranking, and the starter class adapter.
- `src/main.py`: three required profile dictionaries and a plain CLI demonstration.
- `src/evaluate.py`: the required adversarial profile and one sensitivity experiment.
- `tests/`: original starter tests plus meaningful regression and invalid-input tests.
- `model_card.md`: interpretation, limitations, evaluation, and reflection for review.

The starter CLI imported `recommender` as a top-level module, which did not match
`python -m src.main`; it now uses a package-relative import. The starter tests
exercise classes, whereas the project instructions use dictionary functions.
Both interfaces now share one scoring function. The original tests are kept,
and additional tests check reversed input, actual scores, and real explanations
because the original two tests could pass the placeholder implementation.

## Getting Started

Use Python 3.11 or 3.12 (the versions verified by CI). From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`.
The application uses the standard library; pytest is the only installed
dependency. Unused starter pandas/Streamlit dependencies were removed.
The default CSV path is anchored to the package, not the working directory;
`python -m src.main --data path/to/songs.csv` can use another compatible catalog.

## Sample Recommendation Output

Actual output of `python -m src.main`, also saved in `evaluation/demo.txt`:

```text
Loaded songs: 20

Profile: High-Energy Pop
Preferences: genre=pop, mood=happy, energy=0.80
1. Sunrise City — Neon Echo | Score: 3.98
   Because: genre match (+2.00); mood match (+1.00); energy 0.82 vs target 0.80: gap 0.02 (+0.98)
2. Gym Hero — Max Pulse | Score: 2.87
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.93 vs target 0.80: gap 0.13 (+0.87)
3. Rooftop Lights — Indigo Parade | Score: 1.96
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.76 vs target 0.80: gap 0.04 (+0.96)
4. Plaza at Sunset — Sol de Abril | Score: 0.99
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.81 vs target 0.80: gap 0.01 (+0.99)
5. Sidewalk Confidence — Copper Verse | Score: 0.98
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.78 vs target 0.80: gap 0.02 (+0.98)

Profile: Chill Lofi
Preferences: genre=lofi, mood=chill, energy=0.35
1. Library Rain — Paper Lanterns | Score: 4.00
   Because: genre match (+2.00); mood match (+1.00); energy 0.35 vs target 0.35: gap 0.00 (+1.00)
2. Midnight Coding — LoRoom | Score: 3.93
   Because: genre match (+2.00); mood match (+1.00); energy 0.42 vs target 0.35: gap 0.07 (+0.93)
3. Focus Flow — LoRoom | Score: 2.95
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.40 vs target 0.35: gap 0.05 (+0.95)
4. Spacewalk Thoughts — Orbit Bloom | Score: 1.93
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.28 vs target 0.35: gap 0.07 (+0.93)
5. Coffee Shop Stories — Slow Stereo | Score: 0.98
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.37 vs target 0.35: gap 0.02 (+0.98)

Profile: Deep Intense Rock
Preferences: genre=rock, mood=intense, energy=0.90
1. Storm Runner — Voltline | Score: 3.99
   Because: genre match (+2.00); mood match (+1.00); energy 0.91 vs target 0.90: gap 0.01 (+0.99)
2. Gym Hero — Max Pulse | Score: 1.97
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.93 vs target 0.90: gap 0.03 (+0.97)
3. Electric Horizon — Prism Current | Score: 0.94
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.96 vs target 0.90: gap 0.06 (+0.94)
4. Sunrise City — Neon Echo | Score: 0.92
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.82 vs target 0.90: gap 0.08 (+0.92)
5. Iron Signal — Black Meridian | Score: 0.92
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.98 vs target 0.90: gap 0.08 (+0.92)
```

## Experiments You Tried

Run the reproducible evaluation:

```bash
python -m src.evaluate
```

It runs all three required profiles plus a deliberately conflicting classical,
melancholic, high-energy profile, then halves genre weight and doubles energy
weight for the pop profile. This is the required sensitivity experiment on the
same scoring rule, not an optional system of selectable ranking strategies.
Actual baseline/changed outputs and all pairwise profile comparisons are in
`model_card.md`; the complete raw report is `evaluation/results.txt`.

## Limitations and Risks

These synthetic songs have no real listener ratings, so there is no empirical
ground truth about enjoyment. Exact genre labels make `pop` and `indie pop`
different even when a listener may like both. A large genre bonus can overpower
mood and energy. The catalog is small and uneven; three lofi songs provide more
choices than the single classical song. See the model card for measured examples.

## Running Tests and CI

```bash
python -m pytest -q
```

The suite covers data types and validation, exact scoring and explanation values,
energy symmetry, preference-dependent ranking, deterministic ties, top-k bounds,
unchanged input data, class/function consistency, the required weight experiment,
and successful/error CLI behavior. It includes all original starter tests.

Actual local output (elapsed time varies by machine):

```text
....................................................                     [100%]
52 passed in 0.19s
```

GitHub Actions runs pytest on Python 3.11 and 3.12 for pushes and pull requests.
It also reruns the CLI/evaluation and compares their output with the committed
reports. Passing tests checks these specified behaviors; it does not prove all
possible edge cases or actual listener satisfaction.

## Reflection and review

See the model card for factual engineering findings and a proposed reflection
prepared with Codex assistance. Alex should review the code, confirm or revise
the musical-intuition discussion, and personalize the reflection before submission.
No personal listening experience or independent authorship is claimed.

## Submission

The portal displayed Nov 2, 2026 at 17:29 GMT+09:30, which is Nov 2 at 02:59
America/New_York (EST), or Nov 1 at 23:59 America/Los_Angeles (PST). Finish Sunday
night. Keep the repository public, review the written evidence, and submit its
URL using CodePath's Submit button. The build itself does not submit the project.
See `REQUIREMENTS_CHECKLIST.md` for the mapping to all 21 core rubric points.
