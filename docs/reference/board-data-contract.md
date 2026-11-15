# Board data contract

This page is for developers who change the teacher app or the student app. It lists the files that a board keeps under `~/santolina/`, who writes each file and what it holds. The board user is `arduino`, so on a board this folder is `/home/arduino/santolina/`. The teacher app (laptop) and the [student app](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) (board, `student_app/`) share these files. The `classroom/` package implements the contract with the Python standard library only.

## Layout

| Path | Written by | Contents |
| --- | --- | --- |
| `identity.json` | teacher app | `board_id` (the serial number that `adb`, the teacher app's USB link to the board, reports), `name` (the board's label), `group_id`, `setup_at`, `contract_version`, `rag_index_path` |
| `mode.json` | teacher app | `mode`: `student` or `professor`, `changed_at` |
| `roster.json` | teacher app | `group_id`, `codes` (student codes, never names), `updated_at` |
| `exercises/<pack_id>/` | teacher app | an exercise pack (below) |
| `outbox/<session_id>.jsonl` | student app | one session, one event per line |
| `archive/` | teacher app | sessions that the teacher app copied to the laptop and then moved here from `outbox/` |
| `assignments.json` | teacher app | the group's homework: `{"schema_version": 1, "assignments": [...]}`. Each assignment has `assignment_id`, `title`, `pack_id`, `exercise_ids` (`null` = whole pack), `due` and `created_at`. |
| `hotspot.json` | teacher app | the board's Wi-Fi: `ssid`, `password` |
| `progress/<code>.json` | student app | per student code: `code`, `updated_at`, `exercises` and `last`. `exercises` maps `<pack_id>/<exercise_id>` to `status` (`done`, `with_help`, `tried`), `attempts` and `first_try_correct`. `last` is the exercise the student opened last (`mode`, `pack_id`, `exercise_id`, `assignment_id`), or `null`. |
| `lib/classroom/`, `lib/student_app/`, `lib/VERSION` | teacher app | the board code and its version (below) |

The dataclasses in `classroom/schemas.py` define each record. A dataclass field without a default is required. The `check()` methods add the formats, for example the pattern of a student code.

Every JSON file and every event carries `schema_version` (now `1`): the version of that record's format. Readers ignore fields they don't know. But `from_dict` in `classroom/schemas.py` rejects a record whose `schema_version` is higher than its own. Depending on the file, the student app then skips the record, uses a default, or refuses every login (`identity.json`). So raise `schema_version` only together with new code in `lib/`. `identity.json` also carries `contract_version` (now `1`). No code reads its value today, but the field is required. Times are ISO 8601.

The apps also read two files that are not part of the contract:

- `topics.jsonl` in `~/santolina/`: one topic per [M3Kang](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) problem ID. Someone copies it to the board by hand. It is M3Kang data, so it never goes into Git. `santolina_tutor/topics.py` makes it. That script comes with the branch `exp/program-solver`, which is not merged yet.
- The retrieval index `index.db`, built on the board ([below](#the-retrieval-index)).

## Board code in `lib/`

The teacher app compares a fingerprint of its `classroom/` and `student_app/` code with `lib/VERSION` on the board. It does this at setup, and each time it opens the board's page. When they are different, it copies the two packages to `~/santolina/lib/` and rewrites `lib/VERSION`. A running student app then restarts with the new code.

One exception: when the board has a newer student app release (`RELEASE` in `student_app/__init__.py`) than the laptop, the board keeps its code. Raise `RELEASE` with each change that boards must keep. Then a laptop with an older checkout cannot put old code back.

Before the first setup, `board/06_install_student_app.sh` can put this repository's copy in `lib/`, without `lib/VERSION`. The first comparison then finds a difference.

Board code imports the package from there. `classroom.paths.board_root` uses `$SANTOLINA_ROOT` if it exists, else `~/santolina`.

```python
import sys
sys.path.insert(0, "/home/arduino/santolina/lib")
from classroom.events import EventWriter
```

## How the student app uses the files

- It **reads** `identity.json`, `mode.json`, `roster.json`, `assignments.json`, `exercises/` and `lib/VERSION`, and never writes them. It writes only `outbox/` and `progress/`.
- It **asks for the student code** at login and checks it against `roster.json`. Events store only the code.
- It **gives the answer only with the solution.** A student gets an exercise's answer only with the solution, after at least one try. In `professor` mode, a teacher can also log in without a code. The teacher sees the answers, and the student app logs nothing for that teacher visit.
- It **sends the phone's time** as `client_ts` when a session starts. The board's clock can be wrong, because it syncs only with internet. The teacher app corrects times with it.
- It **writes events only through `EventWriter`**, which appends each line and syncs it to disk. A power cut loses at most one line.
- It **ends sessions** with `session.end(reason=...)`. It ends a session after 30 minutes without activity (`idle`, `IDLE_SECONDS` in `student_app/state.py`).
- It **never deletes** files in `outbox/` or `archive/`.

`classroom.status` on the board marks a session file closed when it ends with `session_end`, or when it has not changed for 2 hours (`SESSION_IDLE_SECONDS` in `classroom/paths.py`). The teacher app unloads only closed files, as they are.

```python
writer = EventWriter.from_root()  # reads identity.json
session = writer.start_session("K7M2", client_ts="2026-11-14T09:30:00+01:00")
session.log("exercise_shown", pack_id="demo-arithmetic", exercise_id="e01", level=0)
session.log("hint_requested", pack_id="demo-arithmetic", exercise_id="e01", hint_number=1)
session.log("answer_submitted", pack_id="demo-arithmetic", exercise_id="e01",
            level=0, answer="B", correct=True)
session.end(reason="logout")
```

## Events

Each line of a session file is one event:

| Field | Meaning |
| --- | --- |
| `schema_version` | the event format (now `1`) |
| `event_id` | unique ID (UUID). The teacher app skips IDs it already has. |
| `board_id`, `session_id`, `seq` | where it comes from, and its order in the session |
| `student_code` | the code the student typed, or `null` |
| `ts` | the board's clock |
| `type` | what happened |
| `payload` | free-form details |

The table gives the types that the apps use today. A new type needs no change to the contract. When an exercise is open, an event (except `view_opened` and `session_end`) also carries the exercise context in `payload`: `mode`, `assignment_id`, `pack_id`, `exercise_id`, `level` and `topic`. This `mode` is the student app's view (`homework`, `practice` or `free`), not the board mode of `mode.json`.

| Type | Payload |
| --- | --- |
| `session_start` | `client_ts` (the phone's clock), `language` |
| `session_end` | `reason`: `logout`, `idle`, `new_login` (a new login, of a student or of the teacher), `restart` (new code in `lib/`) |
| `view_opened` | `view`: `home`, `homework`, `practice`, `free`, `exercise` |
| `exercise_shown` | `path_reason`. In free mode, it is the [learning path](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) rule that picked the exercise: `start`, `harder_after_solve`, `new_topic_after_mastery`, `same_level_after_help`, `easier_after_fail` or `other_topic_after_skip` (see `student_app/planner.py`). In any mode, it is `suggested` when the student opened an exercise from a chat suggestion. Otherwise it is `null`. |
| `answer_submitted` | `answer`, `correct`, `attempt`, `seconds_since_shown`, `with_help` (after the solution) |
| `hint_requested` | `hint_number` |
| `solution_requested` | `attempts_before` |
| `question_asked` | `text`, `has_photo`, `photo_bytes`, `photo_type` (the photo itself is not stored) |
| `copilot_reply` | `text`, `seconds`, `kind` (`chat`, `clue`, `solution`), `suggestions`. The tutor model's code (`student_app/tutor.py`) can add more fields. `route` tells which part wrote the reply: `tutor_model`, `fallback`, or the name of a prewritten reply. Optional: `label` (the kind of chat message: `STUCK`, `CONCEPT`, `ATTEMPT`, `SOLUTION` or `OTHER`, from `student_app/router.py`), `clue_number`, `tokens`, `prompt_tokens`, `model_seconds`, `first_token_seconds`, `leak_blocked`, `error`. See [tutor model](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md). |
| `exercise_left` | `seconds`, `attempts` (left without solving) |
| `page_hidden` | no field of its own (the student switched to another app) |
| `page_visible` | `seconds_hidden` (how long the student was in another app) |
| `language_changed` | `language` |

## Exercise packs

```text
exercises/<pack_id>/manifest.json    pack_id, title, version, language, created_at, count, description
exercises/<pack_id>/exercises.json   {"schema_version": 1, "exercises": [...]}
exercises/<pack_id>/media/           images listed by the exercises
```

An exercise has `exercise_id`, `kind` (such as `multiple_choice`), `language`, `level`, `prompt`, and optionally `options` (`{"A": ...}`), `answer`, `media` and `meta`. `media` is a list of `media/<file>` paths. The student app does not serve subfolders of `media/`. The student app loads every valid pack and chooses the order of the exercises.

## The retrieval index

The retrieval index is not part of this contract. Its path is in `identity.json` as `rag_index_path`: the first index that setup finds in `RAG_INDEX_CANDIDATES` (`classroom/paths.py`), usually `~/Santolina_tutor/data/index.db`. You build it on the board with `build_index.py` (Step 12 of [the board setup guide](../BOARD_SETUP.md)).

The student app reads it. Its solved problems are the problems of free mode: `kangaroo-index`, a pack that the student app makes from the index, with no folder in `exercises/`. Free mode leaves out every index problem whose `meta.m3kang_id` a loaded pack holds (`free_items` in `student_app/catalog.py`). With no index, free mode uses the packs. The index vectors find related problems for the learning path and for clues.

The teacher app requires the index at setup, shows its size and languages, and copies it for its Kangaroo library. Neither app changes it.

## Board status

Run `python3 -m classroom.status --root ~/santolina` from `~/santolina/lib`. It prints, as JSON, the state that the teacher app needs:

- `board_time`, the board's clock in Unix seconds, for the time correction
- identity, mode, roster and packs
- outbox (each session file with a `closed` flag) and archive
- free disk and the retrieval index
- the model services on ports 8081, 8082 and 8084 (language, embedding and tutor model)

The teacher app reads the board through it.
