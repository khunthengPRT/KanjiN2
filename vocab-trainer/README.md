# 語彙練習帳 — N2 Vocabulary Practice

A speak-aloud JLPT N2 vocabulary trainer. See the kanji, say it out loud, record
yourself, then tag the word **NEW / SO-SO / BURNT** to drive its review schedule.

167 words with readings, glosses, and example sentences. No dependencies, no
build step, no accounts, no network calls beyond your own machine.

## Run it

```
python3 server.py
```

Then open **http://localhost:8788**.

Python 3.8+ is all you need — the server is standard library only.

```
python3 server.py --port 9000     # different port
python3 server.py --host 0.0.0.0  # also reachable from your phone on the LAN
```

## Why run the server instead of just opening index.html

`index.html` works on its own — double-click it and the app runs, storing
everything in that browser. Two things only work when the server is running:

**The microphone.** Browsers only grant microphone access on a *secure origin*.
`http://localhost` counts as one; a `file://` page does not, and neither does an
embedded page whose host withholds the permission. Serving from localhost is the
reliable way to get recording working.

**Your data outliving the browser.** Clearing site data, switching browsers, or
using a different device otherwise loses your progress. With the server, the
Progress tab gains a **Local server** panel:

- **Push to server** — writes progress and any new voice clips to `./data`
- **Pull from server** — replaces this browser's copy with what's on disk
- **Auto-push as I study** — pushes a few seconds after you stop making changes

## Where your data lives

```
data/progress.json      statuses, review schedule, daily log
data/clips/index.json   word -> {file, date}
data/clips/*.webm       one recording per word
```

`progress.json` is plain JSON — readable, diffable, and fine to keep in git or
back up however you like. Clip filenames are SHA-1 hashes of the word (Japanese
text makes for fragile filenames); `index.json` maps them back.

The **Backup** panel's Export button still works offline and writes the same
progress JSON, but it cannot carry audio — use Push for that.

## Relationship to the Laravel app

This is a standalone prototype, not part of the Laravel application in this
repo. It needs no database, no PHP, and no build step, so it is a place to try
scheduling rules and the record-and-compare flow before committing them to
`DailySetService`, `ProgressTrackerService`, and `VoiceRecorder.vue`.

Notable differences from the planned app: the word list is inlined in
`index.html` rather than seeded from `kanji.json`, review state is keyed to
NEW/SO-SO/BURNT with fixed 0/2/7-day intervals rather than a mastery streak, and
recordings are stored as audio for you to compare by ear — there is no
`AnswerCheckerService` equivalent scoring them.

## Studying

| Key | Action |
| --- | --- |
| `Space` | reveal reading and meaning |
| `1` `2` `3` | tag NEW / SO-SO / BURNT |
| `R` | start or stop recording |
| `P` | play your recording back |
| `L` | hear the model reading (after reveal) |

Scheduling: **NEW** returns later in the same session and again tomorrow,
**SO-SO** in 2 days, **BURNT** in 7. Ten new words are introduced per day.

## A note on the server

It binds to `127.0.0.1` by default and has **no authentication** — it assumes
whoever can reach it is you. It serves exactly one file (`index.html`) plus the
`/api` endpoints; `server.py` and `data/` are not reachable over HTTP. If you
pass `--host 0.0.0.0` to study from your phone, only do it on a network you
trust.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | server info and clip count |
| `GET` | `/api/progress` | current progress JSON |
| `PUT` | `/api/progress` | replace progress JSON |
| `GET` | `/api/clips` | `{word: date}` manifest |
| `GET` | `/api/clips/<word>` | download one clip (webm) |
| `PUT` | `/api/clips/<word>?date=YYYY-MM-DD` | upload one clip |

Word IDs are percent-encoded Japanese, e.g. `/api/clips/%E5%BD%B1%E9%9F%BF` for 影響.
