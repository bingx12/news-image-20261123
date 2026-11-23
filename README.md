# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/bingx12/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/bingx12/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

THE WORLD TODAY — a pure-stdlib Python program that draws Monday 23 November 2026's world news as a one-page newspaper front page and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB, byte-identical on every run).

## Run it

```sh
python3 main.py
```

No network, no clock, no randomness: `main.py` renders everything itself from bitmap glyphs in `font_data.py` (DejaVu Sans Book and Bold at one 64px base size, scaled at runtime) and encodes the PNG with `zlib`.

## The day's stories

Every story on the page happened or was first reported on Monday 23 November 2026 (Reuters, AP, BBC, Al Jazeera, The Guardian):

- **Lead — climate in Antalya.** COP31 collapses: after 18 days and two days of overtime, the summit ends with no deal and no final text. The draft never named fossil fuels, oil, coal or a phase-out, and the EU and about 130 other parties refused it.
- **War at sea.** A Ukrainian naval drone attack sinks the Russian corvette Merkury at the Benghazi naval base in eastern Libya.
- **Washington.** Democrats take 258 House seats, their largest majority since 1992, as Chuck Hubbard beats Virginia Foxx in a North Carolina recount.
- **The Gulf.** Iran says it downed a US MQ-9 drone over the Strait of Hormuz; two supertankers catch fire after hitting mines.
- **Ukraine.** A Russian strike on flats in Dymer, north of Kyiv, kills at least 10 people; a seven-year-old boy is pulled alive from the rubble.
- **Markets — the AI rout.** Japan's Nikkei falls 5.06% and Hong Kong stocks hit a 19-month low as the AI sell-off spreads; the S&P 500 falls 3.7%.
- **Indonesia.** Dozens are missing after a fire at a candy factory in Banten.
- **Also today.** Nepal's PM Balen Shah welcomed by Modi in New Delhi; South Korea's exports pass $1 trillion for the first time; Bolsonaro in intensive care; Marc Marquez takes an eighth MotoGP title; Carlos Alcaraz wins the ATP Finals.

---

<sub>Entered on [make.fun](https://make.fun/?ref=k6eq9xtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
