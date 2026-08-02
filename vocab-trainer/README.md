# 語彙練習帳 — N2 Vocabulary Practice

A speak-aloud JLPT N2 vocabulary trainer. See the kanji, say it out loud, record
yourself, then tag the word **NEW / SO-SO / BURNT** to drive its review schedule.

167 words with readings, glosses, and example sentences. No dependencies, no
build step, no accounts, and nothing leaves your computer.

---

# Part 1 — Getting started

**Written for someone who has never used a terminal.** If you're already
comfortable with git and the command line, skip to [Part 2](#part-2--reference).

You need one thing: **Python 3.8 or newer**. Most Macs and Linux machines
already have it. The setup script checks for you and tells you what to do if
it's missing.

## Step 1 — Get the files onto your computer

Two ways. **Option A is easier**; pick B if you want to receive future updates.

### Option A — Download a ZIP (no git needed)

1. Go to https://github.com/khunthengPRT/KanjiN2
2. Click the green **Code** button, then **Download ZIP**
3. Unzip it — you'll get a folder called `KanjiN2-main`
4. Move it somewhere you'll remember, like your Desktop

The part you need is the `vocab-trainer` folder inside it.

### Option B — Use git (lets you pull updates later)

Git is a tool for downloading and tracking code. Check whether you have it —
open a terminal (see Step 2) and type:

```
git --version
```

If that prints a version number, you have it. If it says "command not found",
install it: `brew install git` on Mac, `sudo apt install git` on Ubuntu, or from
https://git-scm.com/downloads on Windows.

Then download the project. `cd ~/Desktop` means "go to my Desktop folder" —
change it if you'd rather it live elsewhere:

```
cd ~/Desktop
git clone https://github.com/khunthengPRT/KanjiN2.git
```

That creates a `KanjiN2` folder on your Desktop.

> **Heads up:** at the time of writing this app lives on a branch, not on `main`.
> If `vocab-trainer` isn't in the folder after cloning, run
> `git checkout claude/n2-vocab-tracker-voice-rarz7c` from inside it. Once
> [PR #1](https://github.com/khunthengPRT/KanjiN2/pull/1) is merged, plain
> `git clone` is enough.

## Step 2 — Open a terminal in that folder

A terminal is a window where you type commands instead of clicking.

- **Mac** — open **Terminal** (Cmd-Space, type "Terminal"). Type `cd ` (with a
  space after it), then drag the `vocab-trainer` folder from Finder onto the
  window — it fills in the path for you. Press Enter.
- **Windows** — open the `vocab-trainer` folder in File Explorer, right-click an
  empty area, and choose **Git Bash Here** (installed with git). If you don't
  have Git Bash, see [Windows without Git Bash](#windows-without-git-bash).
- **Linux** — right-click the folder and choose **Open in Terminal**.

To confirm you're in the right place, type `ls` (or `dir` on Windows) and press
Enter. You should see `index.html`, `server.py`, and `SETUP.sh` listed.

## Step 3 — Start it

Type this and press Enter:

```
./SETUP.sh
```

The first time only, you may need to make the script runnable:

```
chmod +x SETUP.sh
```

`chmod +x` means "mark this file as a program I'm allowed to run." You only ever
do it once.

The script checks your Python, finds a free port, creates the `data` folder, and
opens your browser. You'll see something like:

```
  Open this in your browser:  http://localhost:8788
```

If the browser didn't open by itself, click that link or paste it into your
address bar.

## Step 4 — Allow the microphone

Your browser will ask for microphone permission the first time you record. Click
**Allow**. Without it everything else still works — you just can't record
yourself.

## Step 5 — Study

You'll see a kanji in a square. Out loud:

1. **Say the word.** Guess if you don't know it.
2. **Press `R`** (or tap the red circle) to record yourself saying it. Press `R`
   again to stop.
3. **Press `Space`** to reveal the reading, meaning, and an example sentence.
4. **Press `L`** to hear how it should sound, and **`P`** to hear your own take.
5. **Press `1`, `2`, or `3`** to say how well you knew it:
   - `1` **NEW** — no idea. Comes back later today and again tomorrow.
   - `2` **SO-SO** — shaky. Comes back in 2 days.
   - `3` **BURNT** — solid. Comes back in 7 days.

Then the next word appears. Ten new words are introduced per day, on top of
whatever is due for review.

## Step 6 — Stop when you're done

Click the terminal window and press **Ctrl-C** (hold Control, press C). That
shuts the server down. Your progress is already saved.

To study again tomorrow, repeat Steps 2 and 3.

## Keeping your progress safe

Progress is saved in your browser as you go. To also save it to disk — which
survives clearing your browser, and includes your voice recordings — open the
**Progress** tab and click **Push to server**. Tick **Auto-push as I study** and
it happens by itself.

Everything lands in the `data` folder next to `SETUP.sh`. Copy that folder
anywhere to back it up.

## When something goes wrong

| What you see | What it means | Fix |
| --- | --- | --- |
| `command not found: ./SETUP.sh` | You're not in the right folder | Redo Step 2, then `ls` to check you can see `SETUP.sh` |
| `Permission denied` | The script isn't marked runnable | `chmod +x SETUP.sh` |
| `Python 3.8 or newer is required` | Python missing or too old | Install from https://www.python.org/downloads/, then reopen the terminal |
| Browser says "can't connect" | Server isn't running | Check the terminal is still open and hasn't printed an error |
| Microphone doesn't work | Permission was denied | Click the padlock icon in the address bar → allow microphone → reload |
| `Port 8788 is busy` | Something else is using it | The script picks the next free port automatically; use the URL it prints |
| Progress vanished | Browser data was cleared | Progress tab → **Pull from server** (works if you'd pushed before) |

### Windows without Git Bash

`SETUP.sh` needs a Unix-style shell. In Command Prompt or PowerShell, skip the
script and run the server directly:

```
python server.py
```

Then open http://localhost:8788 yourself.

## A little git, if you used Option B

You don't need any of this to study — only if you want updates or to save your
own changes.

| Command | What it does |
| --- | --- |
| `git pull` | Download the latest version of the code |
| `git status` | Show what you've changed |
| `git log --oneline` | List recent changes, newest first |

Your `data` folder is deliberately excluded from git (via `.gitignore`), so your
progress and recordings are never uploaded anywhere.

---

# Part 2 — Reference

## Running it directly

```
python3 server.py                 # http://localhost:8788
python3 server.py --port 9000     # a different port
python3 server.py --host 0.0.0.0  # also reachable from your phone on the LAN
```

`SETUP.sh` accepts `--port`, `--phone` (same as `--host 0.0.0.0`), `--no-open`,
and `--help`.

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

The three tabs are **Practice** (drilling), **Word bank** (all 167 words,
searchable and filterable), and **Progress** (streak, memory mix, a 13-week
activity heatmap, session log, sync, and backup).

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
