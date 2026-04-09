# Music Recommender Simulation

## Project Summary

VibeMatch 1.0 is a small content-based music recommender. You give it a genre, a mood, and an energy target. It scores every song in a 20-song catalog against those three preferences and returns the top 5 with a plain-English explanation for each pick. The goal was to build something simple enough to fully understand — and then stress-test it until it broke.

---

## How The System Works

The recommender is a pure content-based system. It looks only at song features and user preferences. It has no listening history, no crowd behavior, and no context signals. Every score is traceable back to a specific feature difference, which makes it a clean model for understanding the math before adding complexity.

**Some prompts to answer:**

- **What features does each `Song` use in your system?**

  Each song carries ten attributes loaded from `data/songs.csv`. Three are identity fields (id, title, artist) used only for display. The seven that drive scoring are:
  - `genre` and `mood` — categorical labels used for binary match bonuses
  - `energy` — the single heaviest feature; immediately felt as calm vs. intense
  - `valence` — emotional tone: happy/bright vs. dark/melancholic (stored but not scored)
  - `tempo_bpm` — governs activity fit like studying or running (stored but not scored)
  - `danceability` — rhythmic feel (stored but not scored)
  - `acousticness` — organic vs. electronic texture (stored but not scored)

- **What information does your `UserProfile` store?**

  The `UserProfile` is a snapshot of current taste — not listening history. It stores:
  - `favorite_genre` — used to award a +1.0 genre-match bonus during scoring
  - `favorite_mood` — used for a +1.0 mood-match bonus
  - `target_energy` — the numeric anchor; songs closest to this value score highest on energy
  - `likes_acoustic` — a boolean flag that is collected but not currently used in scoring

  There is no play history, skip log, or crowd data. This is a pure content-based profile.

- **How does your `Recommender` compute a score for each song?**

  Scoring happens in three steps:

  1. **Genre check** — if the song's genre matches the user's genre, add 1.0 point
  2. **Mood check** — if the song's mood matches the user's mood, add 1.0 point
  3. **Energy similarity** — compute `2.0 × (1.0 − |song.energy − user.energy|)`, which contributes between 0.0 and 2.0 points

  Maximum possible score is 4.0. Genre and mood are binary (match or no match). Energy is continuous — a perfect energy match contributes the full 2.0 points; the most distant possible energy contributes 0.0.

- **How do you choose which songs to recommend?**

  After every song is scored, the ranking layer makes three decisions:
  1. **Sort** all songs by final score, highest first
  2. **Slice** the top k results (default k = 5)
  3. **Return** each result as a (song, score, explanation) tuple

  Scoring and ranking are kept separate so either can be tuned independently — change the weights without touching the ranking logic, or change k without touching the math.

---

### Data Flow Diagram

```mermaid
flowchart TD
    A([User Prefs\ngenre · mood · energy]) --> C
    B([data/songs.csv\n20 songs]) --> LOAD[load_songs]
    LOAD --> C[Pick next song from list]

    C --> D{genre match?}
    D -- yes --> D1[+1.0]
    D -- no  --> D2[+0.0]
    D1 & D2 --> E{mood match?}

    E -- yes --> E1[+1.0]
    E -- no  --> E2[+0.0]
    E1 & E2 --> F[energy similarity\n2.0 × 1 − abs·song − target·]

    F --> G[sum → final score\nattach explanation]
    G --> H{more songs?}
    H -- yes --> C
    H -- no  --> I[sort all scores\ndescending]
    I --> J[slice top K]
    J --> K([Ranked Recommendations\nsong · score · explanation])
```

---

### Algorithm Recipe

This is the exact scoring formula used in `score_song()`:

```
score = genre_points + mood_points + energy_similarity
```

| Signal | Rule | Points |
|---|---|---|
| Genre match | +1.0 if `song.genre == user.genre` | 0 or 1.0 |
| Mood match | +1.0 if `song.mood == user.mood` | 0 or 1.0 |
| Energy similarity | `2.0 × (1.0 − abs(song.energy − user.energy))` | 0.0 – 2.0 |

**Maximum possible score: 4.0**

**Example — user: `pop / happy / energy 0.9`**

| Song | Genre | Mood | Energy score | Total |
|---|---|---|---|---|
| Sunrise City (pop, happy, 0.82) | +1.0 | +1.0 | +1.84 | **3.84** |
| Gym Hero (pop, intense, 0.93) | +1.0 | +0.0 | +1.94 | **2.94** |
| Rooftop Lights (indie pop, happy, 0.76) | +0.0 | +1.0 | +1.72 | **2.72** |
| Storm Runner (rock, intense, 0.91) | +0.0 | +0.0 | +1.98 | **1.98** |

---

### Known Biases and Limitations

**Energy dominates after the first few results.** Energy is worth up to 2.0 points — double genre or mood. Once genre-matched songs run out (most genres have only 1 song), slots #4 and #5 fill with whatever is nearest to the user's energy level regardless of style.

**Mood is all-or-nothing.** A song labeled `relaxed` gets zero mood points for a user who wants `chill`, even though those moods are adjacent. The binary match misses the spectrum between moods — and a one-word typo costs a full point silently.

**Energy is the only continuous signal.** Valence, danceability, tempo, and acousticness are loaded but never used in scoring. A sad-sounding song at the right energy level scores identically to a happy one.

**Small catalog amplifies all biases.** With 20 songs and 17 genres, most genres have only 1 entry. Users whose genre has few catalog entries will almost always see cross-genre fallbacks in their top 5.

---

## Sample Output

Running `python3 src/main.py` with the High-Energy Pop profile:

```
Loaded songs: 20

========================================
  Profile: High-Energy Pop
  (pop / happy / energy 0.9)
========================================

#1  Sunrise City by Neon Echo
    Score : 3.84 / 4.00
    Why   : genre match (+1.0), mood match (+1.0), energy similarity (+1.84)

#2  Gym Hero by Max Pulse
    Score : 2.94 / 4.00
    Why   : genre match (+1.0), energy similarity (+1.94)

#3  Rooftop Lights by Indigo Parade
    Score : 2.72 / 4.00
    Why   : mood match (+1.0), energy similarity (+1.72)

#4  Storm Runner by Voltline
    Score : 1.98 / 4.00
    Why   : energy similarity (+1.98)

#5  Groove Cathedral by Funktown Collective
    Score : 1.96 / 4.00
    Why   : energy similarity (+1.96)
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python3 src/main.py
   ```

### Running Tests

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

**Experiment 1 — Swapping genre and energy weights.**
The original starter code gave genre 2.0 points and energy 1.0 points. I flipped those: genre dropped to 1.0, energy rose to 2.0. The reason was that genre was dominating too much — songs with a matching genre were winning even when the mood and energy felt completely wrong. After the swap, energy became the tiebreaker and recommendations felt more "vibe-accurate" within a genre, though the downside is that energy now dominates cross-genre slots.

**Experiment 2 — Adversarial profiles.**
I ran four edge-case profiles to find failure modes:
- *Sad But Wired* (blues / sad / energy 0.9) — mood and energy directly conflict. The blues song appeared at #1 (genre + mood match), but slots #2–5 were rock, funk, and EDM — the opposite of blues — because high energy mattered more than style.
- *Ghost Genre* (polka / happy / energy 0.8) — "polka" doesn't exist in the catalog. The system still returned 5 songs scoring up to 2.96 out of 4.0 using mood and energy alone. A made-up genre is nearly indistinguishable from a real one.
- *Overclocked* (edm / euphoric / energy 1.5) — energy set above the 0–1 scale. The formula silently produced low energy similarity scores for every song (even the highest-energy ones), but never warned about the invalid input.
- *Blank Slate* (empty dict) — with no preferences supplied, energy defaulted to 0.0 and the quietest songs won: classical, ambient, blues. An empty profile is not neutral — it secretly recommends calm acoustic music.

**Experiment 3 — Mood label mismatch.**
The Chill Lofi profile used mood `"calm"` but the dataset uses `"chill"`. The result: zero mood matches across all 20 songs — silently. The profile still worked well at the top (3 genre matches), but slots #4 and #5 were filled by blues and ambient songs the user never asked for. Fixing this would require either standardizing labels or adding fuzzy matching.

---

## Limitations and Risks

**It only works on a tiny catalog.** 20 songs is not enough for meaningful genre matching. Most genres have 1 song, so genre preference barely influences the bottom half of results.

**It does not understand lyrics, language, or culture.** Two songs can have identical energy and genre labels but feel completely different. The system cannot tell the difference between a joyful pop song and an ironic one.

**It over-favors energy.** Because energy is the only continuous signal and it's weighted at 2×, users with moderate energy preferences end up with recommendations that drift toward whatever genre happens to cluster near their energy value — not their actual taste.

**It treats all users the same.** A new listener and a longtime fan of a genre get the same recommendations. There is no personalization beyond the three inputs provided.

**Exact string matching is fragile.** One spelling difference between a user's mood label and the dataset label means zero mood points for every song, with no feedback to the user.

---

## Reflection

**How recommenders turn data into predictions**

Building this made it clear that a recommender is just a function that turns preferences into a ranked list. The formula looks balanced — 1 point for genre, 1 for mood, up to 2 for energy — but in practice energy almost always wins after the first two results. That gap between what the formula says and what actually shows up in slots #4 and #5 is the most important thing I took from this project. The output can look reasonable even when the underlying logic has a significant imbalance, which means you can't evaluate a recommender just by glancing at the top result.

**Where bias or unfairness could show up**

The Blank Slate experiment showed me that bias doesn't always look wrong. An empty user profile returned a confident, specific playlist — calm, acoustic, classical — because of a silent default I never explicitly chose. In a real product that would mean new users or users who skip preference setup always get steered toward one kind of music, with no indication that their results are based on assumptions rather than their actual taste. Small design decisions in the scoring formula become invisible policies at scale: who gets discovered, what genres get amplified, and whose taste the system was implicitly optimized for. Those questions matter a lot more when a real catalog has millions of songs and the formula runs for millions of users.

---

[**Model Card**](model_card.md)
