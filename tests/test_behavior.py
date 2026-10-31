"""Verify actual scores, rankings, data failures, and the public CLI contracts."""

import copy
import csv
import math
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

from src.main import CATALOG_PATH, PROFILES
from src.recommender import (COLUMNS, Recommender, ScoreWeights, Song,
                             UserProfile, load_songs, recommend_songs, score_song)

ROOT = Path(__file__).resolve().parents[1]
PREFS = {"genre": "pop", "mood": "happy", "energy": 0.8}


@pytest.fixture
def songs():
    return load_songs(CATALOG_PATH)


def write_catalog(tmp_path, rows, headers=COLUMNS):
    path = tmp_path / "songs.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_catalog_meets_project_requirements(songs):
    assert len(songs) == 20
    assert len({song["id"] for song in songs}) == 20
    assert len({song["genre"] for song in songs}) >= 10
    assert all(isinstance(song["id"], int) for song in songs)
    assert all(isinstance(song["energy"], float) for song in songs)


def test_exact_score_and_honest_reasons():
    score, reasons = score_song(PREFS, {"genre": "pop", "mood": "happy", "energy": 0.8})
    assert score == 4.0
    assert reasons == ["genre match (+2.00)", "mood match (+1.00)",
                       "energy 0.80 vs target 0.80: gap 0.00 (+1.00)"]


def test_mismatches_do_not_award_match_points():
    score, reasons = score_song(PREFS, {"genre": "rock", "mood": "sad", "energy": 0.8})
    assert score == 1.0
    assert reasons[:2] == ["genre mismatch (+0.00)", "mood mismatch (+0.00)"]


def test_energy_rewards_closeness_symmetrically():
    prefs = {**PREFS, "energy": 0.5}
    score = lambda energy: score_song(prefs, {**prefs, "energy": energy})[0]
    assert score(0.4) == score(0.6) == 3.9
    assert score(0.5) > score(0.9)


def test_labels_are_case_and_whitespace_insensitive():
    assert score_song({"genre": " POP ", "mood": "Happy", "energy": 0.8},
                      {"genre": "pop", "mood": " happy ", "energy": 0.8})[0] == 4.0


@pytest.mark.parametrize("name,winner", [
    ("High-Energy Pop", "Sunrise City"),
    ("Chill Lofi", "Library Rain"),
    ("Deep Intense Rock", "Storm Runner"),
])
def test_rankings_depend_on_preferences_not_input_order(songs, name, winner):
    ranked = recommend_songs(PROFILES[name], list(reversed(songs)), 5)
    assert len(ranked) == 5
    assert ranked[0][0]["title"] == winner
    assert [score for _, score, _ in ranked] == sorted(
        [score for _, score, _ in ranked], reverse=True)


def test_ranking_keeps_input_and_preferences_unchanged(songs):
    original, prefs = copy.deepcopy(songs), dict(PREFS)
    recommend_songs(prefs, songs)
    assert songs == original and prefs == PREFS


def test_ties_preserve_input_order():
    rows = [{"title": title, **PREFS} for title in ["B", "A", "C"]]
    assert [r[0]["title"] for r in recommend_songs(PREFS, rows)] == ["B", "A", "C"]


def test_mathematically_equal_energy_gaps_tie():
    rows = [{**PREFS, "energy": energy} for energy in [0.82, 0.98]]
    ranked = recommend_songs({**PREFS, "energy": 0.9}, rows)
    assert ranked[0][1] == ranked[1][1]
    assert ranked[0][0] is rows[0]


@pytest.mark.parametrize("k,expected", [(0, 0), (1, 1), (100, 20)])
def test_top_k_boundaries(songs, k, expected):
    assert len(recommend_songs(PREFS, songs, k)) == expected


@pytest.mark.parametrize("k", [-1, 2.5, True, "5"])
def test_invalid_k_fails_clearly(songs, k):
    with pytest.raises(ValueError, match="k must"):
        recommend_songs(PREFS, songs, k)


def test_empty_catalog_has_no_recommendations():
    assert recommend_songs(PREFS, []) == []


@pytest.mark.parametrize("energy", [-0.1, 1.1, math.nan, math.inf, True, "loud", None])
def test_invalid_profile_energy_rejected(energy):
    with pytest.raises(ValueError):
        score_song({**PREFS, "energy": energy}, PREFS)


@pytest.mark.parametrize("prefs", [{}, {"genre": "pop", "energy": 0.8},
                                    {**PREFS, "genre": " "}])
def test_missing_or_blank_preferences_rejected(prefs):
    with pytest.raises(ValueError):
        recommend_songs(prefs, [])


def test_unknown_categories_are_explicit_mismatches():
    score, reasons = score_song({"genre": "unknown", "mood": "unknown", "energy": 0.8}, PREFS)
    assert score == 1 and "mismatch" in reasons[0] and "mismatch" in reasons[1]


@pytest.mark.parametrize("change", [
    {"energy": "nan"}, {"energy": -1}, {"valence": 2}, {"danceability": "bad"},
    {"acousticness": "inf"}, {"tempo_bpm": 0}, {"title": " "}, {"id": 0},
])
def test_bad_csv_values_have_row_number(tmp_path, songs, change):
    path = write_catalog(tmp_path, [{**songs[0], **change}])
    with pytest.raises(ValueError, match="CSV row 2"):
        load_songs(path)


def test_duplicate_ids_are_rejected(tmp_path, songs):
    with pytest.raises(ValueError, match="unique positive"):
        load_songs(write_catalog(tmp_path, [songs[0], songs[0]]))


def test_invalid_header_and_empty_catalog_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("title,energy\nSong,0.5\n")
    with pytest.raises(ValueError, match="columns"):
        load_songs(path)
    path.write_text(",".join(COLUMNS) + "\n")
    with pytest.raises(ValueError, match="at least one song"):
        load_songs(path)


@pytest.mark.parametrize("trailer", [",EXTRA", ""])
def test_extra_or_missing_csv_cells(tmp_path, songs, trailer):
    path = write_catalog(tmp_path, [songs[0]])
    lines = path.read_text().splitlines()
    lines[1] = lines[1] + trailer if trailer else ",".join(lines[1].split(",")[:-1])
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="number of CSV fields"):
        load_songs(path)


@pytest.mark.parametrize("weights", [(-1, 1, 1), (math.nan, 1, 1), (0, 0, 0), (True, 1, 1)])
def test_invalid_weights_rejected(weights):
    with pytest.raises(ValueError):
        ScoreWeights(*weights)


def test_class_and_functional_interfaces_agree(songs):
    user = UserProfile("lofi", "chill", 0.35)
    catalog = [Song(**row) for row in reversed(songs)]
    rec = Recommender(catalog)
    expected = recommend_songs(PROFILES["Chill Lofi"], [asdict(s) for s in catalog])
    actual = rec.recommend(user)
    assert [s.id for s in actual] == [row["id"] for row, _, _ in expected]
    assert rec.explain_recommendation(user, actual[0]) == expected[0][2]


def test_required_sensitivity_experiment_changes_ranking(songs):
    from src.evaluate import EXPERIMENT_WEIGHTS
    before = recommend_songs(PREFS, songs)
    after = recommend_songs(PREFS, songs, weights=EXPERIMENT_WEIGHTS)
    assert before[1][0]["title"] == "Gym Hero"
    assert after[1][0]["title"] == "Rooftop Lights"
    assert score_song(PREFS, songs[0], EXPERIMENT_WEIGHTS)[0] == 3.96


def test_module_cli_runs_and_prints_three_profiles():
    process = subprocess.run([sys.executable, "-m", "src.main"], cwd=ROOT,
                             capture_output=True, text=True, check=True)
    assert "Loaded songs: 20" in process.stdout
    assert process.stdout.count("Because:") == 15
    assert all(name in process.stdout for name in PROFILES)


def test_bad_cli_catalog_is_a_clean_error(tmp_path):
    process = subprocess.run([sys.executable, "-m", "src.main", "--data", str(tmp_path / "missing.csv")],
                             cwd=ROOT, capture_output=True, text=True)
    assert process.returncode == 2
    assert "Error:" in process.stderr and "Traceback" not in process.stderr
