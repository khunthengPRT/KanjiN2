# KanjiN2

Personal JLPT N2 study tools.

## 語彙練習帳 — vocabulary trainer

A speak-aloud N2 vocabulary drill. See the kanji, say it out loud, record
yourself, then tag the word **NEW / SO-SO / BURNT** to set when it comes back.
167 words with readings, meanings, and example sentences.

```
cd vocab-trainer
./SETUP.sh
```

That's it — the script checks your Python, starts a small local server, and
opens the app in your browser. Full instructions, including a walkthrough for
anyone new to the terminal, are in **[vocab-trainer/README.md](vocab-trainer/README.md)**.

**What it does**

- Kanji-first recall with spaced repetition — NEW returns today, SO-SO in 2
  days, BURNT in 7
- Records your voice for each word so you can hear yourself improve
- Daily streak, a 13-week activity heatmap, and a searchable bank of all 167 words
- Saves progress and recordings to disk, not just to your browser
- Runs entirely on your machine: no accounts, no dependencies, no build step

**Requirements:** Python 3.8 or newer, standard library only.
