"""Every piece of text the teacher sees. Translate the app by copying this module.

Templates read these as `S.key`. Text with {placeholders} is filled with .format().
"""

from types import SimpleNamespace

S = SimpleNamespace(
    app_name="Santolina · Teacher",
    # Navigation
    nav_dashboard="Dashboard",
    nav_students="Students",
    nav_groups="Groups",
    nav_boards="Boards",
    nav_packs="Exercise packs",
    nav_unassigned="Unassigned",
    # Connected boards strip
    connected_title="Connected boards",
    connected_none="No board connected. Plug a board into this computer with its USB-C cable.",
    connected_new="New board",
    connected_setup="Set up this board",
    connected_open="Open",
    connected_state_unauthorized="Allow USB debugging on the board, or wait a minute.",
    connected_state_other="The board is not ready ({state}). Wait a minute, or plug it in again.",
    simulated="simulated",
    # Dashboard
    dashboard_title="Dashboard",
    # Students
    students_title="Students",
    students_add="Add a student",
    students_name="Name",
    students_group="Group",
    students_notes="Notes",
    students_code="Code",
    students_code_help=(
        "The student types this code on the board. Boards only ever see the code, never the name."
    ),
    students_none="No students yet. Add the first one below.",
    students_sessions="Sessions",
    students_move="Move to group",
    students_delete="Delete student",
    students_delete_confirm="Delete this student? Their sessions stay, but become unassigned.",
    no_group="No group",
    # Groups
    groups_title="Groups",
    groups_add="Add a group",
    groups_name="Group name (e.g. 3r ESO B)",
    groups_none="No groups yet.",
    groups_students="Students",
    groups_boards="Boards",
    # Boards
    boards_title="Boards",
    boards_none="No boards yet. Plug in a new board to set it up.",
    board_not_connected="This board is not connected. Plug it in to change it or unload its data.",
    board_status="Status",
    board_mode="Mode",
    board_mode_student="Student",
    board_mode_professor="Professor",
    board_mode_to_student="Lock (student mode)",
    board_mode_to_professor="Unlock (professor mode)",
    board_group="Group",
    board_group_save="Change group",
    board_unload="Unload student data",
    board_unload_help="Copies finished sessions to this computer. The board keeps a copy in its archive.",
    board_waiting="Sessions waiting to unload",
    board_open_sessions="Sessions still open",
    board_archive="Sessions already unloaded (kept on the board)",
    board_clear="Delete unloaded data from the board",
    board_clear_confirm=(
        "Delete the unloaded sessions from the board? They are already on this computer."
    ),
    board_disk="Free disk",
    board_clock="Board clock vs this computer",
    board_services="Model services",
    board_rag="Retrieval index (copilot)",
    board_rag_help="Built on the board with build_index.py. The teacher app only reads it.",
    board_packs="Exercise packs on the board",
    board_packs_load="Load pack",
    board_packs_remove="Remove",
    board_syncs="Unload history",
    board_roster="Student codes on the board",
    # Setup
    setup_title="Set up a new board",
    setup_intro=(
        "This prepares the board for your students. The board must already have the copilot "
        "installed (see the board setup guide)."
    ),
    setup_name="Board name",
    setup_name_help="Write the same name on a sticker on the board.",
    setup_group="Group",
    setup_start="Set up the board",
    setup_done="Done. Write “{name}” on a sticker on the board.",
    setup_failed="The setup stopped. Fix the problem below and try again.",
    # Packs
    packs_title="Exercise packs",
    packs_none="No packs yet.",
    packs_import="Import a pack from a folder",
    packs_folder="Folder with manifest.json and exercises.json",
    packs_demo="Create a demo pack (synthetic)",
    # Unassigned
    unassigned_title="Unassigned sessions",
    unassigned_help=(
        "These sessions used a code that doesn't belong to any student, or no code. "
        "Pick the student they belong to."
    ),
    unassigned_none="Nothing to assign.",
    unassigned_assign="Assign",
    unassigned_no_code="(no code)",
    # Common
    save="Save",
    add="Add",
    yes="yes",
    no="no",
    never="never",
    up="up",
    down="down",
    error="Error",
)
