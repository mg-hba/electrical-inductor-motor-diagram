"""
================================================================================
File: utils/constants/project_setup.py
Purpose: Project Setup dialog constants.
Version: 0.1.1
================================================================================
"""

PROJECT_SETUP_INPUT_HEIGHT = 18
PROJECT_SETUP_SPACING = 0
PROJECT_SETUP_SECTION_PADDING = 2
PROJECT_SETUP_HEADER_HEIGHT = 32
PROJECT_SETUP_BUTTON_HEIGHT = 34

PROJECT_SETUP_LABEL_HEIGHT = 9
PROJECT_SETUP_LABEL_FONT = '10sp'
PROJECT_SETUP_INPUT_FONT = '12sp'
PROJECT_SETUP_TITLE_FONT = '11sp'
PROJECT_SETUP_HEADER_FONT = '13sp'

COILS_PER_POLE_MAX_SLOTS = 6
COILS_PER_POLE_INPUT_HEIGHT = 40
COILS_PER_POLE_INPUT_FONT = '16sp'
COILS_PER_POLE_LABEL_FONT = '11sp'

# Focus order — indices of focusable elements in the dialog.
# Paper and Orientation are EXCLUDED.
FOCUS_ORDER = [
    'name', 'power', 'conn', 'all_slots', 'poles',
    'layer', 'span_chained', 'span_concentric',
    'slot_length', 'core_diameter', 'unit',
    'wire_items', 'turns_items',
    'open', 'save', 'cancel',
]