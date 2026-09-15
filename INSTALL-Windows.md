# Installing on Windows

A step-by-step setup for Windows 10 and 11. **No Git Bash required** — this
uses `SETUP.cmd`, a native Windows launcher.

Written for someone who has never used a terminal. If you already have Python
and git, the whole thing is: clone, then double-click `SETUP.cmd`.

---

## Step 1 — Install Python

The app needs **Python 3.8 or newer**. Windows does not ship it.

1. Go to <https://www.python.org/downloads/>
2. Click the big **Download Python** button
3. Run the installer, and **tick "Add python.exe to PATH"** at the bottom of
   the first screen before clicking Install

That tickbox is the one thing people miss. If you skip it, Windows won't find
Python and `SETUP.cmd` will tell you so.

> **If you type `python` and the Microsoft Store opens:** that's a placeholder
> Windows ships, not Python. Install from the link above. If it keeps
> happening, turn the stub off in **Settings → Apps → Advanced app settings →
> App execution aliases**, and switch off both `python.exe` and `python3.exe`.

To check it worked, press <kbd>Win</kbd>+<kbd>R</kbd>, type `cmd`, press Enter,
and type:

```
py --version
```

A version number means you're set.

## Step 2 — Get the app

**Either** download a ZIP — go to
<https://github.com/khunthengPRT/KanjiN2>, click the green **Code** button,
choose **Download ZIP**, then right-click the downloaded file → **Extract
All**. Put the folder somewhere you'll find again, like your Desktop.

**Or** use git, if you want to pull updates later. Install it from
<https://git-scm.com/downloads>, then in a terminal:

```
cd %USERPROFILE%\Desktop
git clone https://github.com/khunthengPRT/KanjiN2.git
```

Git for Windows is worth having for a second reason: it bundles `openssl`,
which the app uses to make a certificate when you study from your phone. The
app finds it automatically — you don't have to configure anything.

## Step 3 — Start it

Open the folder and **double-click `SETUP.cmd`**.

A black window opens, checks your Python, picks a free port, and opens the app
in your browser. You'll see something like:

```
  Goi Renshucho -- N2 Vocabulary Practice
  Setting things up...

  [ok] Found the app files
  [ok] Using Python 3.12.4
  [ok] Your data will be saved in C:\Users\you\Desktop\KanjiN2\data
```

Leave that window open while you study. **Closing it stops the server.**

> **SmartScreen may warn you** the first time — "Windows protected your PC".
> That appears for any script without a paid code-signing certificate. Click
> **More info → Run anyway**. You can read `SETUP.cmd` in Notepad first; it's
> about a hundred lines and all it does is find Python and run `server.py`.

## Step 4 — Allow the microphone

Your browser asks the first time you record. Click **Allow**.

Everything except recording works without it, so you can decline and still use
⌨ Type mode.

## Step 5 — Study

See the main [README](README.md#step-5--study) for how the practice loop works,
the three answer modes, and the keyboard shortcuts.

## Stopping and restarting

Click the black window and press <kbd>Ctrl</kbd>+<kbd>C</kbd>, or just close it.
Your progress is already saved. To study again, double-click `SETUP.cmd` again.

---

## Options

Run these from a terminal in the app folder, rather than double-clicking:

```
SETUP.cmd --port 9000    start on a port you choose
SETUP.cmd --phone        let your phone on the same wifi connect
SETUP.cmd --no-open      don't launch a browser
SETUP.cmd --help         list the options
```

To open a terminal in the right place: click the address bar in File Explorer,
type `cmd`, and press Enter.

## Studying from your phone

```
SETUP.cmd --phone
```

1. **Windows Defender Firewall will ask** whether to allow Python through.
   **Tick "Private networks" and allow it.** If you dismiss this dialog, your
   phone cannot connect and nothing will explain why.
2. The window prints a second address — `https://192.168.x.x:8788`. Type that
   into your phone's browser.
3. Your phone warns the certificate isn't trusted. Tap **Advanced → Proceed**.
   It's signed by your own PC, for your own PC; nothing external vouches for
   it, which is exactly why the warning appears.
4. Allow the microphone.

**Why HTTPS:** browsers only offer the microphone on a secure origin.
`localhost` counts, a plain `http://192.168.…` address does not — on that
address the microphone API doesn't exist at all. `--phone` therefore makes a
certificate and serves over HTTPS so voice works.

If the app can't find `openssl`, it falls back to plain HTTP and says so. ⌨
Type still works perfectly; voice does not. Installing
[Git for Windows](https://git-scm.com/downloads) is the easiest fix, since it
bundles one.

**Anyone on that wifi can read and change your data** — there's no password.
Home network only, not a cafe.

---

## When something goes wrong

| What you see | What it means | Fix |
| --- | --- | --- |
| The window flashes and vanishes | An error scrolled past too fast | Open a terminal in the folder and run `SETUP.cmd` from there so the text stays |
| "Python 3.8 or newer is required" | Not installed, or not on PATH | Redo Step 1 with **Add python.exe to PATH** ticked, then open a *new* terminal |
| The Microsoft Store opens | That's the placeholder, not Python | See the note in Step 1 |
| "Windows protected your PC" | SmartScreen, for any unsigned script | **More info → Run anyway** |
| "Can't find index.html and server.py" | `SETUP.cmd` was moved out of the folder | Keep it beside the other files |
| Phone can't reach the address | Firewall prompt was dismissed, or different wifi | Windows Security → Firewall → Allow an app → tick Python for Private. Check both devices are on the same network |
| Phone: "connection is not private" | Self-signed certificate | Tap **Advanced → Proceed** |
| ▶ Model greyed out | No Japanese text-to-speech voice installed | Settings → Time & language → Language & region → add 日本語 with its Speech pack, then restart the browser |

## A note on line endings

If you edit files on Windows, don't let your editor convert `SETUP.sh` to CRLF
— bash refuses to run it. The repository's `.gitattributes` handles this for
you: `.sh` files stay LF, `.cmd` files get CRLF. You only need to care if you
copy files around by hand outside of git.
