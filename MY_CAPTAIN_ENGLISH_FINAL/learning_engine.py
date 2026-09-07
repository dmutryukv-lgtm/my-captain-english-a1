from datetime import datetime, date
from excel_manager import REQUIRED_SHEETS

LOCAL_USER_ID = "LOCAL_USER"

def clean(v):
    if v is None:
        return ""
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v

class LearningEngine:
    def __init__(self, db):
        self.db = db

    def lessons(self):
        rows = self.db.read("LESSONS")
        return [self._json(r) for r in rows]

    def lesson(self, lesson_id):
        lessons = self.db.read("LESSONS")
        lesson = next((r for r in lessons if str(r.get("LESSON_ID")) == str(lesson_id)), None)
        if not lesson:
            return {"ok": False, "error": "Урок не знайдено"}

        steps = [
            r for r in self.db.read("LESSON_STEPS")
            if str(r.get("LESSON_ID")) == str(lesson_id)
        ]
        steps.sort(key=lambda x: (x.get("STEP_NO") or 0))
        return {
            "ok": True,
            "lesson": self._json(lesson),
            "steps": [self._json(x) for x in steps]
        }

    def words(self):
        return [self._json(r) for r in self.db.read("WORDS")]

    def phrases(self):
        return [self._json(r) for r in self.db.read("PHRASES")]

    def grammar(self):
        return [self._json(r) for r in self.db.read("GRAMMAR")]

    def listening(self):
        return [self._json(r) for r in self.db.read("LISTENING")]

    def speaking(self):
        return [self._json(r) for r in self.db.read("SPEAKING_SCENARIOS")]

    def achievements(self):
        return [self._json(r) for r in self.db.read("ACHIEVEMENTS")]

    def settings(self):
        rows = self.db.read("SETTINGS")
        row = next((r for r in rows if str(r.get("USER_ID")) == LOCAL_USER_ID), None)
        return self._json(row or {
            "USER_ID": LOCAL_USER_ID,
            "INTERFACE_LANGUAGE": "uk",
            "PRONUNCIATION_ACCENT": "en-US",
            "REMINDERS": "YES",
            "SOUND_ON": "YES"
        })

    def dashboard(self):
        progress_rows = self.db.read("PROGRESS")
        row = next((r for r in progress_rows if str(r.get("USER_ID")) == LOCAL_USER_ID), None)

        if row is None:
            row = {
                "USER_ID": LOCAL_USER_ID,
                "LEVEL_ID": "A1",
                "LESSONS_DONE": 0,
                "WORDS_LEARNED": 0,
                "SPEAKING_MIN": 0,
                "LISTENING_MIN": 0,
                "XP": 0,
                "STREAK_DAYS": 0,
                "LAST_ACTIVITY": ""
            }

        levels = self.db.read("LEVELS")
        level = next((x for x in levels if str(x.get("LEVEL_ID")) == str(row.get("LEVEL_ID"))), None)

        lessons = self.db.read("LESSONS")
        active_lessons = [x for x in lessons if str(x.get("ACTIVE")).upper() in ("YES", "TRUE", "1")]

        return {
            "ok": True,
            "user_id": LOCAL_USER_ID,
            "progress": self._json(row),
            "level": self._json(level or {}),
            "lessons_count": len(active_lessons),
            "words_count": len(self.db.read("WORDS")),
            "phrases_count": len(self.db.read("PHRASES")),
            "grammar_count": len(self.db.read("GRAMMAR"))
        }

    def record_activity(self, data):
        user_id = str(data.get("USER_ID") or LOCAL_USER_ID)
        xp = int(data.get("XP") or 0)
        speaking = int(data.get("SPEAKING_MIN") or 0)
        listening = int(data.get("LISTENING_MIN") or 0)
        lessons_done = int(data.get("LESSONS_DONE") or 0)
        words_learned = int(data.get("WORDS_LEARNED") or 0)

        rows = self.db.read("PROGRESS")
        row = next((r for r in rows if str(r.get("USER_ID")) == user_id), None)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current = row or {
            "USER_ID": user_id,
            "LEVEL_ID": "A1",
            "LESSONS_DONE": 0,
            "WORDS_LEARNED": 0,
            "SPEAKING_MIN": 0,
            "LISTENING_MIN": 0,
            "XP": 0,
            "STREAK_DAYS": 0,
            "LAST_ACTIVITY": ""
        }

        values = dict(current)
        values["LESSONS_DONE"] = int(values.get("LESSONS_DONE") or 0) + lessons_done
        values["WORDS_LEARNED"] = int(values.get("WORDS_LEARNED") or 0) + words_learned
        values["SPEAKING_MIN"] = int(values.get("SPEAKING_MIN") or 0) + speaking
        values["LISTENING_MIN"] = int(values.get("LISTENING_MIN") or 0) + listening
        values["XP"] = int(values.get("XP") or 0) + xp
        values["LAST_ACTIVITY"] = now

        self.db.upsert_by_keys("PROGRESS", {"USER_ID": user_id}, values)
        return {"ok": True, "progress": values}

    def record_word_result(self, data):
        user_id = str(data.get("USER_ID") or LOCAL_USER_ID)
        word_id = str(data.get("WORD_ID") or "")
        correct = bool(data.get("CORRECT"))
        if not word_id:
            return {"ok": False, "error": "WORD_ID не вказаний"}

        rows = self.db.read("USER_WORDS")
        existing = next(
            (r for r in rows
             if str(r.get("USER_ID")) == user_id and str(r.get("WORD_ID")) == word_id),
            None
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = dict(existing or {
            "USER_ID": user_id,
            "WORD_ID": word_id,
            "STATUS": "learning",
            "CORRECT_COUNT": 0,
            "WRONG_COUNT": 0,
            "LAST_REVIEW": "",
            "NEXT_REVIEW": "",
            "PRONUNCIATION_SCORE": 0
        })

        if correct:
            values["CORRECT_COUNT"] = int(values.get("CORRECT_COUNT") or 0) + 1
        else:
            values["WRONG_COUNT"] = int(values.get("WRONG_COUNT") or 0) + 1
        values["LAST_REVIEW"] = now

        if int(values["CORRECT_COUNT"]) >= 3:
            values["STATUS"] = "learned"

        self.db.upsert_by_keys(
            "USER_WORDS",
            {"USER_ID": user_id, "WORD_ID": word_id},
            values
        )

        return {"ok": True, "word": values}

    def _json(self, row):
        if row is None:
            return {}
        return {str(k): clean(v) for k, v in row.items()}
