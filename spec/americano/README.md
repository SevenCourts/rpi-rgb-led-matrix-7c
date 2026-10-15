# Americano views: mockups

Pixel mockups for showing a running Playtomic Americano on M1 and XL1
(`led-0jh`, before `led-u9b` builds the views; epic `hub-uw8l` in
sevencourts.hub). Data: Padel Club Esslingen's "Fortgeschritten Americano" of
2026-10-15, rebuilt in 5-minute steps from Manager snapshots, players replaced
by fake names (`mockup-data.json`). How the data is obtained:
`tennismath.tableau` `docs/playtomic/tournaments.md`.

Rendered by `tools/americano_mockups.py` with the firmware's BDF fonts, its
`DrawText`, `fill_rect` and the Padel Club Esslingen style from
`club_styles.py`. `*.png` is native resolution, `*.leds.png` the same as LED
dots.

## Decisions (Ilya, 2026-10-15)

| Topic | Decision |
|---|---|
| Roles | An M1 stands at a court and shows that court only. The XL1 is central and shows the whole tournament. |
| M1 content | Round number, minutes since the round appeared, clock, the two teams. |
| Between rounds | Once the court's result is entered and until the next round exists, M1 shows the score next to the teams. |
| Elapsed time | From when the server first sees the round. Playtomic stores no round start time; when the organiser creates rounds late or in bulk, this is off. |
| Names | First names. |
| XL1 layout | Side by side: the current round, one row per court, left; the leaderboard right. |
| Leaderboard | Position, name, matches (Sp), wins (S), points (Pkt), sorted by points then wins, as Manager does. Paged through all players, 8 per page. |
| Style | Padel Club Esslingen: cream text, green boxes, lime accents. |

## M1 (192x64), at a court

Round in progress:

![](m1-court-round-in-progress.leds.png)

Result entered, next round not created yet; the winning score in lime:

![](m1-court-result-entered.leds.png)

Long names: both teams drop from Spleen 12x24 to 8x16 together, so the two
lines always match:

![](m1-court-long-names.leds.png)

Layout: a 12 px header (round in the booking views' court box, elapsed time in
lime, clock in cream at the right), then two 24 px team rows split by a green
line. With a score, the names give up the width of two 12x24 digits.

## XL1 (320x96), central

Leaderboard page 1 and page 2:

![](xl1-overview-page1.leds.png)

![](xl1-overview-page2.leds.png)

Round 1, before any result: no ranking yet, players alphabetically, positions
shown as dashes:

![](xl1-overview-round1.leds.png)

Layout: a 12 px header across the panel (round, elapsed time, tournament
name, clock); left of x=186 one 27 px row per court (court box, the two teams in
Spleen 6x12, the score at the right once entered); right of it the
leaderboard in Spleen 5x8 with the top three in lime.

## Open questions

- **Court name on M1.** Left out (the panel stands at the court). Room for it
  in the header if wanted.
- **Language.** Labels are German (Runde, Sp, S, Pkt); the firmware has `de`
  and `en` locales, the views should go through them.
- **Name clashes.** Two players with the same first name are not told apart
  yet. Proposal: add the surname's initial to both, only when they clash.
- **More than 3 courts on XL1.** 27 px rows fit three courts; four need
  20 px rows with the teams on one line.
- **Page interval.** 8 s per leaderboard page is a guess.
- **Compensation points** for players sitting out a round (player counts not a
  multiple of four) are not in this data; the columns stay the same.
- **After the last round.** Manager only marks a tournament finished when the
  organiser presses Finish, which may never happen; the end needs to come
  from the booking's end time too. A final podium screen is not designed yet.
