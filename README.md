# 語彙練習帳 — N2 Vocabulary Practice

A speak-aloud JLPT N2 vocabulary trainer. See the kanji, say it out loud, record
yourself, then tag the word **NEW / SO-SO / BURNT** to drive its review schedule.

167 words with readings, glosses, and example sentences. No dependencies, no
build step, no accounts, and nothing leaves your computer.

```
./SETUP.sh
```

That's the whole setup — the script checks your Python, starts a small local
server, and opens the app. Requires **Python 3.8 or newer**, standard library
only. Never used a terminal? Part 1 walks through it from the beginning.

Prefer containers? **[INSTALL-Docker.md](INSTALL-Docker.md)** — `docker compose
up -d` and you're done, no Python on the host.

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

That folder is everything you need.

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

## Step 2 — Open a terminal in that folder

A terminal is a window where you type commands instead of clicking.

- **Mac** — open **Terminal** (Cmd-Space, type "Terminal"). Type `cd ` (with a
  space after it), then drag the project folder from Finder onto the window —
  it fills in the path for you. Press Enter.
- **Windows** — open the project folder in File Explorer, right-click an empty
  area, and choose **Git Bash Here** (installed with git). If you don't have
  Git Bash, see [Windows without Git Bash](#windows-without-git-bash).
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

You'll see a kanji in a square. Give the reading, and the app checks it.

Three ways to answer — pick one with the buttons under the card. Your choice is
remembered.

| Mode | How it works |
| --- | --- |
| 🎤 **Speak** | Tap **Speak — records and checks**. One tap records your attempt *and* judges it, so you get a verdict and a clip to play back. Needs Chrome or Edge; greyed out elsewhere. Works offline once you download the Japanese model — see below. |
| ⌨ **Type** | Type the reading and press Enter. Accepts kana *or* romaji — `eikyou` counts as えいきょう, so you don't need a Japanese keyboard. |
| **Self-rate** | No checking. Reveal the answer and judge yourself, the way flashcards usually work. |

Then:

1. **Answer** by speaking or typing. Stuck? Click **skip** — it counts as a miss.
2. **See the verdict** — ✓ Correct, ≈ Close (a character or two off), or ✗ Not
   quite, with the reading you were after.
3. **Press `L`** to hear the model reading, and **`P`** to hear yourself.
4. **Press `1`, `2`, or `3`** to set when it comes back. One is marked
   **SUGGESTED** based on how you did — take it or override it:
   - `1` **NEW** — no idea. Comes back later today and again tomorrow.
   - `2` **SO-SO** — shaky. Comes back in 2 days.
   - `3` **BURNT** — solid. Comes back in 7 days.

**In 🎤 Speak mode, speaking is the recording** — one tap records the attempt
and checks it, and **`P`** plays your own take back afterwards. In ⌨ Type and
Self-rate modes, **`R`** (or the red circle) records on its own, without a
verdict.

**The ▶ Model button is different.** It plays the *correct* reading using a
text-to-speech voice from your operating system — not the model you downloaded
for Speak mode. If it's greyed out, no Japanese voice is installed; see
[Installing a Japanese voice](#installing-a-japanese-voice). Nothing else
depends on it.

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

## Studying on your phone

Same wifi, same data — the phone talks to the server on your computer, so
progress and recordings stay in one place.

1. On the computer: `./SETUP.sh --phone`
2. It prints a second line, **From your phone:** `https://192.168.x.x:8788`
3. Type that into Chrome or Safari on the phone
4. It warns the certificate isn't trusted. Tap **Advanced → Proceed** — see
   [why](#why-your-phone-warns-about-the-certificate)
5. Allow the microphone when asked

Leave the terminal running while you study; `Ctrl-C` stops it.

**Why HTTPS and not plain http:** browsers only hand out the microphone on a
"secure origin". `localhost` counts, a plain `http://192.168.…` address does
not — on that address `navigator.mediaDevices` doesn't even exist, so there is
no recording and no 🎤 Speak. `--phone` therefore generates a certificate and
serves over HTTPS so voice works. The app detects an insecure address and says
so rather than showing controls that can't work.

If `openssl` isn't installed, `--phone` falls back to plain http and warns you:
⌨ **Type** still works completely, voice does not.

**Tip:** in Safari, Share → *Add to Home Screen* gives it an icon and opens it
without browser chrome.

## When something goes wrong

| What you see | What it means | Fix |
| --- | --- | --- |
| `command not found: ./SETUP.sh` | You're not in the right folder | Redo Step 2, then `ls` to check you can see `SETUP.sh` |
| `Permission denied` | The script isn't marked runnable | `chmod +x SETUP.sh` |
| `Python 3.8 or newer is required` | Python missing or too old | Install from https://www.python.org/downloads/, then reopen the terminal |
| Browser says "can't connect" | Server isn't running | Check the terminal is still open and hasn't printed an error |
| Microphone doesn't work | Permission was denied | Click the padlock icon in the address bar → allow microphone → reload |
| **Model** button greyed out, shows `—` | No Japanese text-to-speech voice is installed on your computer | Install one (see below), or ignore it — everything else works |
| 🎤 **Speak** button greyed out | Your browser has no speech recognition | Use Chrome or Edge, or switch to ⌨ **Type** |
| "No connection. Download the Japanese speech model below…" | Speak mode is using the browser's online service | Click **⬇ Download Japanese speech model** under the Speak button — after that it runs offline. Or use ⌨ **Type**, which never needs internet |
| `Port 8788 is busy` | Something else is using it | The script picks the next free port automatically; use the URL it prints |
| Phone: "connection is not private" | The certificate is self-signed by your computer | Tap **Advanced → Proceed**. Expected on your own network |
| Phone: 🎤 Speak greyed out, "Voice is off on this address" | You're on a plain `http://` LAN address | Restart with `./SETUP.sh --phone`, which serves HTTPS, and reload |
| Phone can't reach the address at all | Different wifi, or a firewall | Put both devices on the same network; allow the port if your firewall asks |
| Progress vanished | Browser data was cleared | Progress tab → **Pull from server** (works if you'd pushed before) |

### Voice typing without internet

By default, Speak mode streams your audio to your browser vendor's servers, so
it stops working the moment you go offline. There is nothing to cache around
this — every attempt is new audio, so there is no previous answer to reuse.

The real fix is to move the recognition onto your machine. Chrome 138+ can
download a Japanese speech model once and run it locally:

1. Switch to 🎤 **Speak** mode
2. Click **⬇ Download Japanese speech model** underneath
3. Wait. A bar shows it's still running and a clock shows how long it has
   been going. **Stop waiting** backs out at any point without losing anything

After that the line reads **✓ Offline recognition ready**, and voice typing
works with no connection at all. Your audio also stops leaving the computer,
which is the nicer side effect.

**Why there's no percentage.** Chrome exposes no progress information for this
download — the whole API is "is it available yet", with no byte counts and no
progress events. So the bar is deliberately indeterminate: it shows the
download is alive, not how far along it is. Anything claiming a percentage
here would be made up.

**To see the real status**, open `chrome://components` in a new tab and look
for **Speech On-Device API (SODA)**. That is Chrome's own view of the download
and it can retry from there.

**If it never finishes**, the app keeps waiting for up to 30 minutes, then
says so rather than spinning forever. The download belongs to Chrome, not to
this page, so the usual causes are outside the app: a slow or filtered
connection, low disk space, or a managed-device policy. Check that 日本語 is
listed under `chrome://settings/languages` and try again. ⌨ **Type** works
offline throughout.

If your browser can't do this, the app says so and points you at ⌨ **Type**,
which has never needed a connection.

### Installing a Japanese voice

The **Model** button plays the reading using a text-to-speech voice supplied by
your operating system, not by this app. If no Japanese voice is installed there
is nothing to play, and the button says so by greying out and showing `—`.

- **macOS** — System Settings → Accessibility → Spoken Content → System Voice →
  Manage Voices → add a Japanese voice (Kyoko)
- **Windows** — Settings → Time & language → Language & region → add 日本語,
  then install its Speech pack
- **Linux** — install a Japanese voice for `speech-dispatcher`, e.g. `espeak-ng`

Reload the page afterwards. Nothing else depends on this — recording, answer
checking, and scheduling all work without a voice installed.

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
| `Enter` | check a typed answer |
| `Space` | start/stop listening (Speak mode) · reveal (Self-rate mode) |
| `1` `2` `3` | tag NEW / SO-SO / BURNT |
| `R` | start or stop recording |
| `P` | play your recording back |
| `L` | hear the model reading (after answering) |

Scheduling: **NEW** returns later in the same session and again tomorrow,
**SO-SO** in 2 days, **BURNT** in 7. Ten new words are introduced per day.

### What counts as correct

An answer is accepted as any spelling of the right reading:

- **kana** — えいきょう, or エイキョウ
- **the written form** — 影響. Speech recognition usually returns kanji rather
  than kana, so both are accepted
- **romaji** — `eikyou`, `joukyou`, `kekkon`. Doubled consonants and long vowels
  work the way you'd expect
- spacing and punctuation are ignored

One or two characters off is reported as **≈ Close** rather than wrong, so a
slip doesn't read the same as not knowing the word.

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

## Design notes

Everything is deliberately plain: one HTML file, one Python file, no database,
no framework, no build step. That keeps it runnable years from now and editable
without a toolchain.

- **The word list is inlined in `index.html`** rather than loaded from a data
  file, so the app still works if you open it with no server at all.
- **Review state is a three-way tag** on fixed intervals (NEW today, SO-SO +2
  days, BURNT +7) rather than a scored algorithm like SM-2. Easy to reason
  about, and easy to tune — the numbers live in one `INTERVAL` object near the
  top of the script.
- **Recognition runs locally when it can.** If the browser reports a Japanese
  model as installed, the recogniser is switched to `processLocally`, so audio
  never leaves the machine and no connection is needed. Otherwise it falls back
  to the browser's online service, and the app says which one is in use.
- **Answers are checked by transcription, not pronunciation scoring.** Speak
  mode runs your voice through the browser's speech recognition and compares
  the resulting *text* with the reading. It tells you whether you said the
  right word — not how good your accent is. In practice bad enough
  pronunciation does fail to transcribe, which is useful feedback, but treat it
  as a spot check rather than a score. Nothing here grades your pitch accent.
- **Recordings stay unscored on purpose.** They exist so you can hear yourself
  against the model reading and over time. Automatic scoring of
  second-language speech is unreliable enough that a confidently wrong grade
  would be worse than none.
- **Typing accepts romaji** so the app is usable without a Japanese keyboard.
  The converter is a plain lookup table, not a full IME — it handles the
  digraphs, doubled consonants, and ん, which covers every reading in the deck.
- **Sync is same-origin only.** The page talks to the server over relative
  URLs, so there is no CORS setup and no host to configure. Served from
  anywhere else, it quietly falls back to browser-only storage.

---

# Part 3 — Security and privacy

Short version: **you don't need to set anything up.** The defaults keep
everything on your machine. This section is what to know, and the one option
that changes the picture.

## What stays on your computer

| | Where it lives | Leaves your machine? |
| --- | --- | --- |
| Progress and schedule | `data/progress.json` + browser storage | No |
| Voice recordings | `data/clips/*.webm` + browser storage | No |
| Speech recognition audio | processed by Chrome | **Only if the on-device model isn't installed** |
| The word list | inside `index.html` | Nothing to send |

The app makes no outbound requests of its own. There is no analytics, no
account, no telemetry, and no third-party script or font — everything it needs
is in the one HTML file.

## The one real decision: `--phone`

By default the server binds to `127.0.0.1`, which only your own computer can
reach. Running `./SETUP.sh --phone` (or `--host 0.0.0.0`) binds it to your
network instead, and **there is no password**. On that network, anyone who
finds the port can:

- read your progress and download your voice recordings
- overwrite or wipe your progress

Traffic itself is encrypted — `--phone` serves over HTTPS using a certificate
it generates for your machine, because browsers refuse the microphone on a
plain-HTTP address. **Encryption is not authentication**: the connection is
private, but nothing checks *who* is connecting. Use `--phone` on your own home
wifi if you like; don't use it on cafe, hotel, airport, or office wifi. Closing
the terminal (`Ctrl-C`) ends exposure immediately.

The certificate and its private key live in `data/cert/` (the key is written
`0600`, owner-only). They're covered by `.gitignore`, so they're never
committed. Delete the folder to force a fresh one.

## Speech recognition and your voice

Before you download the Japanese model, 🎤 Speak sends your audio to your
browser vendor's servers for transcription. After the download it runs
**on-device** — the status line says *✓ Offline recognition ready — no internet
needed, and your voice never leaves this computer*. If that line isn't showing,
assume audio is leaving the machine.

⌨ **Type** never involves audio at all.

Recordings are ordinary `.webm` files in `data/clips/`, not encrypted. Anyone
with access to your user account on the computer can play them. If that matters
to you, rely on your disk encryption (FileVault, BitLocker, LUKS) — the app
doesn't add its own.

## Things the app guards against

- **`data/` is git-ignored**, so progress and recordings are never committed or
  pushed if you use git.
- **The server serves one file.** Only `index.html` and the `/api` endpoints are
  reachable; `server.py`, `data/`, and anything else in the folder return 404.
  Path traversal (`/../server.py`, `/%2e%2e/…`) is refused.
- **Saved progress is treated as untrusted.** Whatever comes back from
  `localStorage`, an imported file, or the server is validated before use:
  statuses must be one of the three known values, counts must be numbers, dates
  must look like dates, and word ids must be words the app actually ships.
  Anything else is discarded rather than rendered. Uploads are size-capped and
  clip filenames are hashes, so a crafted name can't escape `data/clips/`.

## Why your phone warns about the certificate

The certificate is **self-signed** — made by your computer, vouched for by
nothing else. Your phone can't tell it apart from an impostor's, so it warns
once and you tap through. On your own wifi, connecting to your own machine,
that's the expected cost of getting HTTPS without a public domain name. If you
ever see that warning on a network you don't control, don't tap through.

## What to do if you share the computer

Use a separate operating-system account, or delete `data/` and clear the site's
browser storage when you're done. The app has no login of its own — it assumes
whoever is at the keyboard is you.

