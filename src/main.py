"""Run the required music recommendation demonstration from the repository root."""

import argparse
from pathlib import Path

from .recommender import DEFAULT_WEIGHTS, load_songs, recommend_songs

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
}
EDGE_PROFILE = {"genre": "classical", "mood": "melancholic", "energy": 0.95}


def format_recommendations(name, preferences, songs, weights=DEFAULT_WEIGHTS):
    """Format a plain numbered list of five songs with scores and explanations."""
    lines = [f"Profile: {name}",
             f"Preferences: genre={preferences['genre']}, mood={preferences['mood']}, "
             f"energy={preferences['energy']:.2f}"]
    recommendations = recommend_songs(preferences, songs, k=5, weights=weights)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        lines.extend([f"{rank}. {song['title']} — {song['artist']} | Score: {score:.2f}",
                      f"   Because: {explanation}"])
    if not recommendations:
        lines.append("No songs available.")
    return "\n".join(lines)


def main():
    """Load the catalog and show all three required profiles without API access."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=CATALOG_PATH)
    args = parser.parse_args()
    try:
        songs = load_songs(args.data)
        print(f"Loaded songs: {len(songs)}\n")
        for name, preferences in PROFILES.items():
            print(format_recommendations(name, preferences, songs))
            print()
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
