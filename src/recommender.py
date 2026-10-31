"""A small, explainable content-based recommender with one shared scoring rule."""

import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Song:
    """Store the starter catalog attributes; only genre, mood, and energy score."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Keep the starter interface; likes_acoustic is reserved, not scored."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool = False


@dataclass(frozen=True)
class ScoreWeights:
    """Hold nonnegative feature weights for the required sensitivity experiment."""

    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.0

    def __post_init__(self):
        """Reject nonfinite, negative, boolean, or all-zero weights."""
        for name in ("genre", "mood", "energy"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} weight must be a number")
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} weight must be finite and nonnegative")
        if self.genre + self.mood + self.energy == 0:
            raise ValueError("At least one feature weight must be positive")


DEFAULT_WEIGHTS = ScoreWeights()
COLUMNS = tuple(Song.__dataclass_fields__)
NORMALIZED_FEATURES = ("energy", "valence", "danceability", "acousticness")


def _text(value, name):
    """Require nonblank text while preserving display spelling."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonblank text")
    return value.strip()


def _number(value, name, unit_interval=False):
    """Parse a finite number and optionally require the interval [0, 1]."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    if unit_interval and not 0 <= number <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return number


def _profile_values(user_prefs):
    """Validate the three required dictionary preferences."""
    try:
        return (
            _text(user_prefs["genre"], "preferred genre").casefold(),
            _text(user_prefs["mood"], "preferred mood").casefold(),
            _number(user_prefs["energy"], "target energy", True),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("Preferences require genre, mood, and energy") from exc


def load_songs(csv_path: str) -> List[Dict]:
    """Read and validate the starter CSV schema, converting numeric columns."""
    songs, seen_ids = [], set()
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or sorted(reader.fieldnames) != sorted(COLUMNS):
            raise ValueError(f"CSV must have these columns exactly: {', '.join(COLUMNS)}")
        for line, row in enumerate(reader, start=2):
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Incorrect number of CSV fields")
                song = {key: _text(row[key], key) for key in COLUMNS}
                song["id"] = int(song["id"])
                if song["id"] <= 0 or song["id"] in seen_ids:
                    raise ValueError("Song IDs must be unique positive integers")
                for key in NORMALIZED_FEATURES:
                    song[key] = _number(song[key], key, True)
                song["tempo_bpm"] = _number(song["tempo_bpm"], "tempo_bpm")
                if song["tempo_bpm"] <= 0:
                    raise ValueError("tempo_bpm must be positive")
                songs.append(song)
                seen_ids.add(song["id"])
            except ValueError as exc:
                raise ValueError(f"CSV row {line}: {exc}") from exc
    if not songs:
        raise ValueError("CSV must contain at least one song")
    return songs


def score_song(user_prefs: Dict, song: Dict,
               weights: ScoreWeights = DEFAULT_WEIGHTS) -> Tuple[float, List[str]]:
    """Return weighted genre/mood matches plus energy closeness and real reasons."""
    genre, mood, target = _profile_values(user_prefs)
    try:
        song_genre = _text(song["genre"], "song genre").casefold()
        song_mood = _text(song["mood"], "song mood").casefold()
        energy = _number(song["energy"], "song energy", True)
    except (KeyError, TypeError) as exc:
        raise ValueError("Songs require genre, mood, and energy") from exc
    genre_points = weights.genre if genre == song_genre else 0.0
    mood_points = weights.mood if mood == song_mood else 0.0
    gap = abs(energy - target)
    energy_points = weights.energy * (1.0 - gap)
    reasons = [
        f"genre {'match' if genre == song_genre else 'mismatch'} (+{genre_points:.2f})",
        f"mood {'match' if mood == song_mood else 'mismatch'} (+{mood_points:.2f})",
        f"energy {energy:.2f} vs target {target:.2f}: gap {gap:.2f} (+{energy_points:.2f})",
    ]
    # Round only machine-scale noise so mathematical ties remain stable.
    return round(float(genre_points + mood_points + energy_points), 12), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    weights: ScoreWeights = DEFAULT_WEIGHTS) -> List[Tuple[Dict, float, str]]:
    """Score every song and return top k descending, preserving input order on ties."""
    _profile_values(user_prefs)
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    if k == 0:
        return []
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]


class Recommender:
    """Adapt the starter's class interface to the same functional scoring logic."""

    def __init__(self, songs: List[Song]):
        """Copy the catalog list to avoid reordering the caller's collection."""
        self.songs = list(songs)

    @staticmethod
    def _preferences(user: UserProfile) -> Dict:
        """Translate starter profile field names into the functional interface."""
        return {"genre": user.favorite_genre, "mood": user.favorite_mood,
                "energy": user.target_energy}

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return original Song objects ordered by the shared scoring function."""
        rows = [asdict(song) for song in self.songs]
        ranked = recommend_songs(self._preferences(user), rows, k)
        # Dictionaries keep identity through recommend_songs, even with equal IDs.
        originals = {id(row): song for row, song in zip(rows, self.songs)}
        return [originals[id(row)] for row, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the same score that determines the object's ranking."""
        _, reasons = score_song(self._preferences(user), asdict(song))
        return "; ".join(reasons)
