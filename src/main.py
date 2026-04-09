"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs
except ImportError:
    from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "calm",
        "energy": 0.3,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "angry",
        "energy": 0.85,
    },
}


# Adversarial profiles — each one targets a specific bug in score_song().
#
#  "Sad But Wired"   → conflicting mood/energy: sad mood wants low energy, but
#                       energy:0.9 rewards high-energy songs, so the recommender
#                       ends up ignoring the mood preference in practice.
#
#  "Ghost Genre"     → genre:"polka" never matches any song in the dataset,
#                       so genre contributes 0 for everyone; the top score
#                       possible is 2.0 instead of 4.0.
#
#  "Overclocked"     → energy:1.5 is above the 0–1 range used in the CSV.
#                       For a song at energy 0.22: abs(0.22 - 1.5) = 1.28,
#                       so energy_sim = 1.0 - 1.28 = -0.28 (negative),
#                       which is silently added to the score.
#
#  "Blank Slate"     → empty dict: genre/mood never match (0 pts each);
#                       energy defaults to 0.0, so energy_sim = 1 - song.energy
#                       and the QUIETEST songs win.
ADVERSARIAL_PROFILES = {
    "Sad But Wired": {
        "genre": "blues",
        "mood": "sad",
        "energy": 0.9,
    },
    "Ghost Genre": {
        "genre": "polka",
        "mood": "happy",
        "energy": 0.8,
    },
    "Overclocked": {
        "genre": "edm",
        "mood": "euphoric",
        "energy": 1.5,
    },
    "Blank Slate": {},
}


def _print_recommendations(profile_name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print("\n" + "=" * 40)
    print(f"  Profile: {profile_name}")
    genre = user_prefs.get("genre", "<none>")
    mood  = user_prefs.get("mood",  "<none>")
    energy = user_prefs.get("energy", "<none>")
    print(f"  ({genre} / {mood} / energy {energy})")
    print("=" * 40)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{i}  {song['title']} by {song['artist']}")
        print(f"    Score : {score:.2f} / 4.00")
        print(f"    Why   : {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    print("\n" + "#" * 40)
    print("  NORMAL PROFILES")
    print("#" * 40)
    for profile_name, user_prefs in PROFILES.items():
        _print_recommendations(profile_name, user_prefs, songs)

    print("\n" + "#" * 40)
    print("  ADVERSARIAL / EDGE-CASE PROFILES")
    print("#" * 40)
    for profile_name, user_prefs in ADVERSARIAL_PROFILES.items():
        _print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
