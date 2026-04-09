# Reflection: Profile Pair Comparisons

## Pair 1 — High-Energy Pop vs. Chill Lofi

**High-Energy Pop** (pop / happy / energy 0.9) top 5: Sunrise City, Gym Hero, Rooftop Lights, Storm Runner, Groove Cathedral.  
**Chill Lofi** (lofi / calm / energy 0.3) top 5: Library Rain, Focus Flow, Midnight Coding, Empty Glass Blues, Spacewalk Thoughts.

These two profiles sit at opposite ends of the energy spectrum (0.9 vs. 0.3), and the results reflect that cleanly. High-Energy Pop fills slots #3–5 with songs from synthwave, rock, and funk — none of which are pop — because their energy values (0.75–0.91) are close to 0.9 and earn nearly 2 full energy points. Chill Lofi does something similar: slots #4–5 are blues and ambient, not lofi, because those genres happen to cluster near energy 0.3. In both cases the genre and mood bonuses only determine the top 3 results; after that, energy similarity takes over completely. This makes sense given that the energy term can contribute twice as much as genre or mood. The key takeaway is that both profiles are well-served at the top but exhibit genre drift the moment genre-matched songs run out — and since most genres have only one song, that happens quickly.

---

## Pair 2 — Deep Intense Rock vs. Sad But Wired

**Deep Intense Rock** (rock / angry / energy 0.85) top 5: Storm Runner, Iron Horizon, Crown Heights Anthem, Sunrise City, Groove Cathedral.  
**Sad But Wired** (blues / sad / energy 0.9) top 5: Empty Glass Blues, Storm Runner, Groove Cathedral, Gym Hero, Hyperflux.

Both profiles want high energy (0.85 and 0.9 respectively), so their lower-ranked slots converge on the same high-energy songs: Storm Runner, Groove Cathedral, and Gym Hero appear in both lists. The difference is at the top. Deep Intense Rock puts Storm Runner (rock, genre match) at #1 and Iron Horizon (metal, mood match on "angry") at #2 — a reasonable result. Sad But Wired, however, exposes a conflict: the user wants sad music but high energy, and the blues catalog is inherently low-energy (Empty Glass Blues sits at 0.31). The genre+mood match earns it a score of 2.82, but slots #2–5 are filled by storm, funk, pop, and EDM — all stylistically opposite to blues. The system has no way to recognize that "sad blues at high energy" is nearly impossible to satisfy simultaneously; it just picks the next-best energy matches. This reveals that mood and energy can work against each other with no correction from the model.

---

## Pair 3 — Ghost Genre vs. Blank Slate

**Ghost Genre** (polka / happy / energy 0.8) top 5: Sunrise City, Rooftop Lights, Crown Heights Anthem, Night Drive Loop, Groove Cathedral.  
**Blank Slate** (empty dict) top 5: Moonlight Sonata Reimagined, Spacewalk Thoughts, Empty Glass Blues, Library Rain, Coffee Shop Stories.

These two profiles expose what happens when the system has nothing to anchor on. Ghost Genre loses genre matching entirely (polka appears nowhere in the dataset), so it falls back on mood ("happy") and energy (0.8). The results are actually coherent — two genuinely happy, high-energy songs lead the list — which shows the mood+energy fallback works reasonably. Blank Slate is the opposite failure mode: with no preferences at all, `energy` defaults to 0.0, so the formula rewards the quietest songs. The entire top-5 is acoustic and introspective music (classical, ambient, blues, lofi, jazz). This is not a "blank" or "neutral" output — it is strongly biased toward low-energy content, which is misleading. A user who submitted no preferences expecting a random or diverse result instead gets a playlist that implies they love mellow, acoustic music. The Ghost Genre comparison makes this worse by contrast: even a completely made-up genre still produces a more balanced list than an empty one.

---

## Pair 4 — Overclocked vs. High-Energy Pop (bonus)

**Overclocked** (edm / euphoric / energy 1.5) top 5: Hyperflux, Groove Cathedral, Iron Horizon, Gym Hero, Storm Runner.  
**High-Energy Pop** (pop / happy / energy 0.9) top 5: Sunrise City, Gym Hero, Rooftop Lights, Storm Runner, Groove Cathedral.

Both profiles want high-energy euphoric music, but Overclocked uses an out-of-range energy value (1.5 vs. the 0–1 scale in the dataset). The surprising result is that Overclocked's top-5 scores are much lower (max 2.92) than High-Energy Pop's (max 3.84), and the energy similarity scores for Overclocked drop for every song — because `abs(song.energy - 1.5)` is always at least 0.5 even for the highest-energy songs in the dataset (EDM at 0.96 gives `|0.96 - 1.5| = 0.54`, so energy_sim = 2 * 0.46 = 0.92). In effect, Overclocked is penalized for asking for something that doesn't exist in the catalog. The list still surfaces the right flavor of songs (EDM, funk, metal, pop, rock) because relative energy ordering is preserved, but the formula silently treats 1.5 as a valid target with no warning. The comparison shows that High-Energy Pop (energy 0.9) is actually the "correct" way to ask for maximum energy within this dataset, and that out-of-range inputs degrade quality rather than crashing.
