"""Reproduce the required profiles, adversarial input, and one weight experiment."""

from .main import CATALOG_PATH, EDGE_PROFILE, PROFILES, format_recommendations
from .recommender import ScoreWeights, load_songs, recommend_songs

EXPERIMENT_WEIGHTS = ScoreWeights(genre=1.0, mood=1.0, energy=2.0)


def evaluation_report():
    """Return deterministic observed output for documentation and regression checks."""
    songs = load_songs(CATALOG_PATH)
    lines = [f"Loaded songs: {len(songs)}", "", "BASELINE: genre=2.0, mood=1.0, energy=1.0", ""]
    profiles = dict(PROFILES, **{"Conflicting Classical": EDGE_PROFILE})
    for name, preferences in profiles.items():
        lines.extend([format_recommendations(name, preferences, songs), ""])
    lines.extend(["SENSITIVITY EXPERIMENT: halve genre and double energy",
                  "genre=1.0, mood=1.0, energy=2.0", ""])
    preferences = PROFILES["High-Energy Pop"]
    lines.extend([format_recommendations("High-Energy Pop (experiment)", preferences,
                                         songs, EXPERIMENT_WEIGHTS), ""])
    before = recommend_songs(preferences, songs)
    after = recommend_songs(preferences, songs, weights=EXPERIMENT_WEIGHTS)
    lines.extend(["Before top 3: " + ", ".join(song["title"] for song, _, _ in before[:3]),
                  "After top 3: " + ", ".join(song["title"] for song, _, _ in after[:3])])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(evaluation_report(), end="")
