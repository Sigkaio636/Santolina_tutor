"""The student interface, served by the board to the student's phone over its own Wi-Fi.

Standard library only (the board has no pip). The teacher app copies this package to
~/santolina/lib/student_app/, and `board/06_install_student_app.sh` starts it at boot:

    cd ~/santolina/lib && python3 -m student_app.server --port 80 --public-host 10.42.0.1

The copilot is behind `tutor.Tutor` (the fine-tuned tutor model, `llm.py`, with the
message router of `router.py`) and the learning path behind `planner.PathPlanner`.
"""

# Raise this by one with every change that boards must keep. A teacher app never replaces a
# board's code with a lower release (teacher_app/services/boards.py, push_lib), so a laptop
# with an old checkout can't put old code back on a board. Code from before this line is 0.
#   1: the real tutor (fine-tuned model, leak check, router)
#   2: prompts that reuse the model's cache, free mode from the index
RELEASE = 2
