"""
================================================================================
File: dialogs/project_setup/setup_span_controls.py
Purpose: Span controls, speed display, span recomputation.
         Formula: concentric = chained - coils_per_pole + 1
         coils_per_pole = all_slots / (3 * poles)
Version: 0.1.2
================================================================================
"""

from ui.theme import Theme


##
###### Update speed display based on selected poles ######
##
def update_speed_display(dialog, *args):
    try:
        poles_value = int(dialog.poles_spinner.text)
        speed = 6000 // poles_value if poles_value > 0 else 0
        dialog.speed_value_label.text = str(speed)
    except Exception:
        dialog.speed_value_label.text = '---'
# end update_speed_display


##
###### Update span input enabled/disabled state ######
##
def update_span_state(dialog):
    is_single = (dialog.layer_spinner.text == 'Single Layer')
    if is_single:
        dialog.chained_span_input.text = ''
        dialog.concentric_span_input.text = ''
        dialog.chained_span_input.disabled = True
        dialog.concentric_span_input.disabled = True
        dialog.chained_span_input.background_color = Theme.INPUT_DISABLED_BG
        dialog.concentric_span_input.background_color = Theme.INPUT_DISABLED_BG
        dialog.chained_span_btn.background_color = Theme.BUTTON_NEUTRAL_BG
        dialog.concentric_span_btn.background_color = Theme.BUTTON_NEUTRAL_BG
    else:
        if dialog.span_active_type == 'chained':
            dialog.chained_span_input.disabled = False
            dialog.chained_span_input.background_color = Theme.INPUT_BG
            dialog.concentric_span_input.disabled = True
            dialog.concentric_span_input.background_color = Theme.INPUT_DISABLED_BG
            dialog.chained_span_btn.background_color = [0.2, 0.7, 0.3, 1]
            dialog.concentric_span_btn.background_color = Theme.BUTTON_PRIMARY_BG
        else:
            dialog.chained_span_input.disabled = True
            dialog.chained_span_input.background_color = Theme.INPUT_DISABLED_BG
            dialog.concentric_span_input.disabled = False
            dialog.concentric_span_input.background_color = Theme.INPUT_BG
            dialog.chained_span_btn.background_color = Theme.BUTTON_PRIMARY_BG
            dialog.concentric_span_btn.background_color = [0.2, 0.7, 0.3, 1]
# end update_span_state


##
###### Handle span button click ######
##
def on_span_btn_click(dialog, span_type):
    dialog.span_active_type = span_type
    update_span_state(dialog)
# end on_span_btn_click


##
###### Get coils per pole value ######
##
def get_coils_in_pole(dialog):
    try:
        all_slots = int(dialog.all_slots_input.text.strip())
        poles = int(dialog.poles_spinner.text.strip())
    except Exception:
        return 0
    if poles <= 0:
        return 0
    return all_slots / (3 * poles)
# end get_coils_in_pole


##
###### Recompute other span using conversion formula ######
##
def recompute_other_span(dialog, source):
    if dialog.layer_spinner.text == 'Single Layer':
        return
    coils_per_pole = get_coils_in_pole(dialog)
    if coils_per_pole <= 0:
        return
    try:
        if source == 'chained':
            value_text = dialog.chained_span_input.text.strip()
            if not value_text:
                return
            chained_value = int(value_text)
            concentric_value = chained_value - coils_per_pole + 1
            dialog.concentric_span_input.text = str(int(round(concentric_value)))
        else:
            value_text = dialog.concentric_span_input.text.strip()
            if not value_text:
                return
            concentric_value = int(value_text)
            chained_value = concentric_value + coils_per_pole - 1
            dialog.chained_span_input.text = str(int(round(chained_value)))
    except Exception:
        pass
# end recompute_other_span


##
###### Handle chained span focus loss ######
##
def on_chained_span_focus(dialog, instance, focused):
    if not focused:
        recompute_other_span(dialog, 'chained')
# end on_chained_span_focus


##
###### Handle concentric span focus loss ######
##
def on_concentric_span_focus(dialog, instance, focused):
    if not focused:
        recompute_other_span(dialog, 'concentric')
# end on_concentric_span_focus