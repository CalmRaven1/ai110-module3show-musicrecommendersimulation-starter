# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch recommends songs based on three things you tell it: your favorite genre, your current mood, and how energetic you want your music to feel.

It's a classroom project. It's meant to show how scoring rules can drive — and sometimes break — a recommender. It is not a real app.

It assumes you already know what genre you like and can put a number on how high-energy you want the music to be. It does not learn from your history. It does not change over time.

**What it should NOT be used for:**
- Replacing a real music app like Spotify or Apple Music
- Making recommendations for real users at scale
- Any situation where a wrong recommendation has actual consequences

---

## 3. How the Model Works

The system looks at every song in the catalog and gives it a score. Then it returns the top 5.

Here is how points are assigned:

- **+1.0** if the song's genre matches your preferred genre
- **+1.0** if the song's mood matches your preferred mood
- **0.0 to 2.0** based on how close the song's energy is to your target energy

The maximum possible score is 4.0.

Energy is the biggest factor. It's worth up to 2 points — double what genre or mood are worth. A song from the wrong genre with close energy can beat a genre-matched song that has a slightly different energy level.

The original starter code gave genre 2 points and energy 1 point. This version swapped those weights because genre was dominating the results — songs with a genre match were winning even when the mood and energy were totally off.

---

## 4. Data

The catalog has **20 songs**. Each song has a title, artist, genre, mood, and numeric audio features: energy (0–1), tempo, valence, danceability, acousticness, and speechiness.

There are 17 different genres. Most genres only have 1 song. Lofi has 3, pop has 2, and everything else has exactly 1. That matters a lot — after the first genre-matched result, the rest of your top 5 comes from other genres.

Nothing was added or removed from the starter dataset. The songs and their scores are made up for the purposes of this simulation. They don't come from real streaming data.

Some things are missing entirely from the catalog: Latin music, K-pop, electronic subgenres beyond EDM and synthwave, and anything outside a Western pop/rock/jazz framework.

---

## 5. Strengths

The system works well when your genre exists in the catalog and your energy target is realistic (between 0.0 and 1.0). Profiles like "Chill Lofi" and "High-Energy Pop" get intuitive results at the top of the list.

Every recommendation comes with a plain-English explanation: what matched, how many points it earned, and why. That transparency is actually rare in real recommenders. It makes it easy to understand what the system is doing and where it goes wrong.

The system never crashes on weird input. A fake genre, an empty profile, or an out-of-range energy value all return something rather than an error. That's at least stable behavior, even if the results are off.

---

## 6. Limitations and Bias

**Energy takes over after the first few results.** Energy similarity is worth up to 2 points — double genre or mood. Once your genre-matched songs run out (which happens fast in a 20-song catalog), slots #4 and #5 fill up with whatever is nearest to your energy level, regardless of style. A lofi listener ends up with blues and ambient music not because they asked for it, but because those genres happen to have low energy.

**The `likes_acoustic` field does nothing.** It's part of the user profile but it's never checked during scoring. You can say you love acoustic music and the system ignores it completely.

**Most genres have only one song.** After that one genre match, there's nothing left. The recommender has no choice but to fall back on energy proximity for the rest of the list.

**A blank profile secretly recommends calm music.** If no preferences are given, energy defaults to 0.0. That makes the quietest songs — classical, ambient, blues — rank first. It feels like a neutral result, but it's actually biased toward low-energy, acoustic content.

**Exact string matching breaks on small differences.** The mood "calm" never matches the dataset label "chill." One word off means zero mood matches across all 20 songs, silently, with no warning.

---

## 7. Evaluation

Seven profiles were tested: three normal ones and four adversarial edge cases.

**Normal profiles:**
- *High-Energy Pop* — pop / happy / energy 0.9
- *Chill Lofi* — lofi / calm / energy 0.3
- *Deep Intense Rock* — rock / angry / energy 0.85

**Adversarial profiles:**
- *Sad But Wired* — blues / sad / energy 0.9 (mood and energy conflict)
- *Ghost Genre* — polka / happy / energy 0.8 (genre not in the dataset)
- *Overclocked* — edm / euphoric / energy 1.5 (out of 0–1 range)
- *Blank Slate* — completely empty preferences

For normal profiles, the goal was to check whether the top result made sense and whether the rest of the list stayed in the same stylistic neighborhood.

For adversarial profiles, the goal was to see if the system failed gracefully or did something weird.

**What was surprising:**

- Chill Lofi never got a mood match. The profile said "calm" but the dataset says "chill." One word off, zero mood points — on every song.
- Ghost Genre (polka) scored up to 2.96 out of 4.0. A completely made-up genre performed almost as well as real profiles. The system couldn't tell the difference.
- Blank Slate returned a classical and ambient playlist. It felt less like "no preference" and more like "I specifically like quiet music." The silent default to energy 0.0 caused that.
- Deep Intense Rock put Iron Horizon (metal) at #2. The actual rock song in the dataset has mood "intense" — not "angry" — so the metal song with mood "angry" outranked everything else.

---

## 8. Ideas for Improvement

**Actually use `likes_acoustic`.** It's already stored in the user profile. A small scoring bonus for acoustic songs when the user prefers them would be a quick and meaningful change.

**Fix mood matching so close words count.** Right now "calm" and "chill" are treated as completely different. A simple lookup table of similar moods — or fuzzy matching — would prevent silent misses that the user never knows happened.

**Add more songs per genre.** With only 1 song in most genres, genre matching barely matters. Adding 5–10 songs per genre would make the genre bonus actually useful and reduce the energy-dominance problem naturally.

---

## 9. Personal Reflection

**My biggest learning moment**

The moment that stuck with me most was running the Blank Slate profile — a completely empty user dictionary — and watching the system confidently return a classical and ambient playlist. I expected something random, or maybe an error. Instead, the system had a strong, specific opinion. It just turned out that opinion was a silent assumption I built in without realizing it: when energy is missing, it defaults to 0.0, so the quietest songs always win. The output looked perfectly reasonable. There was no error. No warning. I would not have caught it if I hadn't deliberately tried to break the system.

That is the thing I want to remember from this project. Bias doesn't always look broken. Sometimes it looks fine.

**How AI tools helped me — and when I had to double-check**

I used Claude as a thinking partner throughout this project. It helped me trace through what score_song() would actually produce for each profile, which saved a lot of time compared to working it out by hand. It also helped me name things I noticed but couldn't quite articulate — like calling the energy problem a "filter bubble" instead of just "energy is too strong."

But I learned not to take the output at face value. At one point I had to verify that the `likes_acoustic` field was genuinely unused, not just documented somewhere I hadn't seen. I checked the actual scoring function myself. The AI was right, but the point is I checked — because "it told me so" is not good enough when you're trying to actually understand the system. Using AI tools well means using them to move faster on things you can verify, not to skip the verification.

**What surprised me about simple algorithms feeling like recommendations**

Honestly, the whole thing surprised me. Three scoring rules — genre, mood, energy — and the output genuinely feels like something is listening to you. The High-Energy Pop profile gets Sunrise City first, which is exactly right. The Chill Lofi profile gets three lofi songs in a row. It feels intentional.

But then you look one level deeper and the illusion breaks. Slots #4 and #5 are blues and ambient music in the lofi list — not because the system thinks you'd like them, but because they happen to be quiet. The algorithm isn't understanding you. It's pattern-matching on numbers. The feeling of being understood is a side effect of the math, not the goal.

That gap — between what a simple formula produces and what a person assumes it means — is probably the most important thing I took from this project. When something feels intelligent, it's worth asking: what is it actually doing?

**What I'd try next**

First, I'd fix the mood matching. "Calm" and "chill" should not be treated as completely different. A small synonym table or fuzzy matching would make the system much more forgiving without changing the core logic.

Second, I'd actually wire up `likes_acoustic`. The field is already there. It would take five lines of code to add a small bonus for acoustic songs when the user prefers them. Right now collecting that preference and then ignoring it is just noise.

Third — and this is the bigger one — I'd want to try collaborative filtering. Right now the system only looks at song features. It knows nothing about what other people with similar tastes ended up enjoying. Adding even a simple "users who liked X also liked Y" layer on top of the content-based score would probably catch a lot of the cases where the current system goes sideways.
