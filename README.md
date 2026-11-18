# The World Today — 17 November 2026 in one image

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Dhikas182/news-image-17-nov/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Dhikas182/news-image-17-nov/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Built for [make.fun bounty news-image-20261117](https://make.fun/bounty/news-image-20261117).

A newspaper front page that sums up the world's news of Tuesday
17 November 2026 in a single 1024x1024 image, drawn from scratch in
pure Python (standard library only — no network, no fonts, no image
files). The program draws every pixel itself: a hand-written 5x7
bitmap font, flat-colour scenes, and a PNG encoder built on `zlib`
and `struct`.

## The day in the image

- **Lead — Ukraine cuts the Kerch Bridge.** Overnight, Ukrainian
  drones and missiles brought down a road span of the bridge linking
  Russia to occupied Crimea; the rail arch was damaged.
- **The Gulf — drones over Bahrain.** Iran fired drones at a US
  radar in Bahrain; US jets struck back on Qeshm Island; tankers
  were hit in and near the Strait of Hormuz.
- **Manila — Trump lands in Manila** for the ASEAN-US summit and
  Quad talks, on his way to Shenzhen.
- **Markets — Nvidia beats and guides $130bn.** Q3 revenue
  $115.8bn, up 103% — its first report since Jensen Huang resigned.
- **Space — Vulcan fails: 40 satellites lost.** ULA's first
  account: its first stage faltered just after liftoff.
- **Money — a bug stalls America's banks.** A JPMorgan software
  bug slowed transactions at US banks; the bank says it is not a
  cyberattack.
- **Also on Tuesday:** Japan scrambles jets after a Russian
  airspace incursion; Houthis advance in Yemen; the UK sanctions
  firms building West Bank settlements.

Every story was checked against live reporting of 17 November 2026
before it was drawn; where an event happened the day before, the
image says so (the Vulcan failure was Sunday; Tuesday brought ULA's
first explanation. The JPMorgan bug was reported on Tuesday).

## Run it

```
python3 main.py [output-path]
```

Without an argument it writes `/output/entry.png` (or
`$MAKEFUN_OUTPUT_DIR/entry.png`). The output is a 1024x1024 PNG
of about 23 KB, well under the 1 MiB limit. The program is fully
deterministic: two runs write byte-identical files.

## License

0BSD, see LICENSE.
