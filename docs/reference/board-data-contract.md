# Board data contract

The files a board keeps under `~/santolina/`, shared by the teacher app (laptop) and the student interface (board). The `classroom/` package implements them with the Python standard library only. The teacher app copies it to `~/santolina/lib/classroom/` at setup and at every connection, so the board always has the same version as the laptop.

The student interface imports it from there:

```python
import sys
sys.path.insert(0, "/home/arduino/santolina/lib")
from classroom.events import EventWriter
```

## Layout

| Path | Written by | Contents |
| --- | --- | --- |
| `identity.json` | teacher app | `board_id` (adb serial), `name`, `group_id`, `setup_at`, `contract_version`, `rag_index_path` |
| `mode.json` | teacher app | `mode`: `student` or `professor`, `changed_at` |
| `roster.json` | teacher app | `group_id`, `codes` (student codes, never names), `updated_at` |
| `exercises/<pack_id>/` | teacher app | an exercise pack (below) |
| `outbox/<session_id>.jsonl` | student interface | one session, one event per line |
| `archive/` | teacher app | sessions already unloaded |
| `lib/classroom/` | teacher app | this package |

Every JSON object carries `schema_version` (now `1`). Readers ignore fields they don't know. Times are ISO 8601.

## Rules for the student interface

- **Read** `mode.json`, `roster.json` and `exercises/`. Never write them.
- **Respect the mode.** In `student` mode, don't show answers or settings, and don't delete data.
- **Ask for the student code** at the start, and check it against `roster.json`. Store only the code.
- **Send the phone's time** as `client_ts` when a session starts. The board's clock can be wrong, because it syncs only with internet. The teacher app corrects times with it.
- **Write events only through `EventWriter`.** It appends and syncs every line to disk, so a power cut loses at most one line.
- **End sessions** with `session.end()`. A session that stays untouched for 2 hours counts as abandoned and is unloaded as it is.
- **Never delete** files in `outbox/` or `archive/`.

```python
writer = EventWriter.from_root()
session = writer.start_session("K7M2", client_ts="2026-11-14T09:30:00+01:00")
session.log("exercise_shown", pack_id="demo-arithmetic", exercise_id="e01", level=0)
session.log("hint_requested", pack_id="demo-arithmetic", exercise_id="e01", hint_level=1)
session.log("answer_submitted", pack_id="demo-arithmetic", exercise_id="e01",
            level=0, answer="B", correct=True)
session.end(reason="student_finished")
```

## Events

Each line of a session file is one event:

| Field | Meaning |
| --- | --- |
| `event_id` | unique ID (UUID). The teacher app skips IDs it already has. |
| `board_id`, `session_id`, `seq` | where it comes from, and its order in the session |
| `student_code` | the code the student typed, or `null` |
| `ts` | the board's clock |
| `type` | what happened |
| `payload` | free-form details |

These types are known today. New types need no change to the contract.

| Type | Payload the statistics use |
| --- | --- |
| `session_start` | `client_ts` |
| `exercise_shown` | `pack_id`, `exercise_id`, `level` |
| `hint_requested` | `pack_id`, `exercise_id`, `hint_level` |
| `answer_submitted` | `pack_id`, `exercise_id`, `level`, `answer`, `correct` |
| `session_end` | `reason` |

## Exercise packs

```
exercises/<pack_id>/manifest.json    pack_id, title, version, language, created_at, count, description
exercises/<pack_id>/exercises.json   {"schema_version": 1, "exercises": [...]}
exercises/<pack_id>/media/           images listed by the exercises
```

An exercise has `exercise_id`, `kind` (such as `multiple_choice`), `language`, `level`, `prompt`, and optionally `options` (`{"A": ...}`), `answer`, `media` (paths inside the pack) and `meta`. Which pack is active, and in what order exercises appear, is up to the student interface.

## The retrieval index

The copilot's retrieval index, `~/Santolina_tutor/data/index.db` (path in `identity.json` as `rag_index_path`), is not part of this contract. It is built on the board with `build_index.py` (Step 12 of [the board setup guide](../BOARD_SETUP.md)). The teacher app only reads it, to show its size and languages, and requires it at setup. It never changes it. Retrieval may find an exercise from a pack, with its answer; deciding whether a hint leaks the answer is the job of the copilot's own check, not of this contract.

## Board status

`python3 -m classroom.status --root ~/santolina`, run from `~/santolina/lib`, prints the whole state as JSON: identity, mode, roster, packs, outbox (with which sessions are closed), archive, free disk, the retrieval index and the model services. The teacher app reads the board through it.
