kanji-practice/
├── app/
│   ├── Console/
│   │   └── Commands/
│   │       └── GenerateDailySet.php        # Artisan command for daily set
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── DailySetController.php      # Return today's 100 kanji
│   │   │   ├── PracticeSessionController.php # Handle answer submissions
│   │   │   └── ProgressController.php      # Streak & mastery data
│   │   └── Requests/
│   │       └── SubmitAnswerRequest.php     # Validate voice answer input
│   ├── Models/
│   │   ├── Kanji.php
│   │   ├── DailySet.php
│   │   └── UserProgress.php
│   ├── Services/
│   │   ├── DailySetService.php             # あ→ん selection logic lives here
│   │   ├── AnswerCheckerService.php        # Compare voice input vs readings[]
│   │   └── ProgressTrackerService.php      # Consecutive correct / mastery logic
│   └── Jobs/
│       └── GenerateDailySetJob.php         # Queued job triggered by scheduler
│
├── database/
│   ├── migrations/
│   │   ├── create_kanjis_table.php
│   │   ├── create_daily_sets_table.php
│   │   └── create_user_progress_table.php
│   └── seeders/
│       ├── data/
│       │   └── kanji.json                  # The davidluzgouveia dataset goes here
│       └── KanjiN2Seeder.php
│
├── resources/
│   ├── js/
│   │   ├── Pages/
│   │   │   ├── Practice/
│   │   │   │   ├── Index.vue               # Today's session entry point
│   │   │   │   └── Complete.vue            # End of session / mastery screen
│   │   │   └── Dashboard.vue              # Streak & overall progress view
│   │   ├── Components/
│   │   │   ├── KanjiCard.vue              # The main flashcard component
│   │   │   ├── VoiceRecorder.vue          # Web Speech API wrapper
│   │   │   ├── ProgressBar.vue            # X/100 kanji done today
│   │   │   └── StreakBadge.vue            # Consecutive correct counter
│   │   └── app.js
│   └── views/
│       └── app.blade.php                  # Single Inertia root view
│
├── routes/
│   ├── web.php                            # Inertia page routes
│   └── api.php                            # JSON endpoints for practice session
│
└── config/
    └── kanji.php                          # e.g. daily_set_size: 100, mastery_streak: 5