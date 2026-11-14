"""The student interface, served by the board to the student's phone over its own Wi-Fi.

Standard library only (the board has no pip). The teacher app copies this package to
~/santolina/lib/student_app/, and `board/06_install_student_app.sh` starts it at boot:

    cd ~/santolina/lib && python3 -m student_app.server --port 80 --public-host 10.42.0.1

The copilot is behind `tutor.Tutor` and the learning path behind `planner.PathPlanner`.
Both are stubs for now: replace them without touching the interface.
"""
