"""
test_buttons_final.py
Comprehensive button test.
"""
import sys
sys.path.insert(0, "/storage/emulated/0/python/3phase_motor/kivy/0.1.3.2")

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from ui.button_manager import button_manager


class TestApp(App):
    def build(self):
        root = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
        )

        root.add_widget(Label(
            text='Final Button Test',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))

        # Row 1: Icon-only with different styles
        row1 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44),
        )
        row1.add_widget(button_manager.create_icon_button(
            'menu', style='primary', size=(44, 44),
        ))
        row1.add_widget(button_manager.create_icon_button(
            'close', style='danger', size=(44, 44),
        ))
        row1.add_widget(button_manager.create_icon_button(
            'save', style='success', size=(44, 44),
        ))
        row1.add_widget(button_manager.create_icon_button(
            'reset', style='warning', size=(44, 44),
        ))
        row1.add_widget(button_manager.create_icon_button(
            'back', style='neutral', size=(44, 44),
        ))
        root.add_widget(row1)

        # Row 2: Text buttons
        row2 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44),
        )
        row2.add_widget(button_manager.create_text_button(
            'Open', style='primary', width=100, height=44,
        ))
        row2.add_widget(button_manager.create_text_button(
            'Save', style='success', width=100, height=44,
        ))
        row2.add_widget(button_manager.create_text_button(
            'Cancel', style='danger', width=100, height=44,
        ))
        root.add_widget(row2)

        # Row 3: Icon+Text buttons
        row3 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44),
        )
        row3.add_widget(button_manager.create_icon_text_button(
            text='Open', icon_name='open_file',
            style='primary', width=130, height=44,
        ))
        row3.add_widget(button_manager.create_icon_text_button(
            text='Save', icon_name='save',
            style='success', width=130, height=44,
        ))
        root.add_widget(row3)

        # Row 4: Toggles
        row4 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44),
        )
        row4.add_widget(button_manager.create_toggle_button(
            text='Grid 10x', is_active=True, width=140, height=44,
        ))
        row4.add_widget(button_manager.create_toggle_button(
            text='Grid 5x', is_active=False, width=140, height=44,
        ))
        root.add_widget(row4)

        # Status
        self.status = Label(
            text='Click any button',
            font_size='12sp',
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(self.status)

        # Info
        root.add_widget(Label(
            text='Check: border color, icon centered, text horizontal',
            font_size='11sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20),
        ))

        return root


if __name__ == "__main__":
    TestApp().run()