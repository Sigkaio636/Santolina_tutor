"""The board data contract: the files a board keeps under ~/santolina/.

Pure standard library, so it runs on the board (Python 3.13, no pip) and on the
teacher's laptop. The teacher app copies this package to ~/santolina/lib/classroom/
on every board, and the student interface imports it from there.
"""

CONTRACT_VERSION = 1
