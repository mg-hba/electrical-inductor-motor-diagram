"""
================================================================================
File: dialogs/project_setup/base_page.py
Purpose: Base class for all wizard pages.
         Compact layout: header 36dp, footer 48dp.
Version: 0.1.4.1
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button


class BasePage(BoxLayout):

    title = "PAGE"

    def __init__(self, mode="wizard", is_first_page=False,
                 is_last_page=False, **kwargs):
        super().__init__(orientation="vertical", spacing=0, **kwargs)

        self.mode = mode
        self.is_first_page = is_first_page
        self.is_last_page = is_last_page

        # Callbacks
        self.on_next = None
        self.on_back = None
        self.on_cancel = None
        self.on_save = None
        self.on_open = None
        self.on_physical = None

        # Background
        with self.canvas.before:
            Color(*Theme.DIALOG_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.add_widget(self._build_header())
        self.add_widget(self._build_content_scroll())
        self.add_widget(self._build_footer())

    # ============================================================
    # ================== BACKGROUND ==============================
    # ============================================================

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    # ============================================================
    # ================== HEADER (compact 36dp) ===================
    # ============================================================

    def _build_header(self):
        header = BoxLayout(size_hint_y=None, height=dp(36),
                           spacing=dp(4),
                           padding=[dp(8), dp(4), dp(8), dp(4)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self._header_bg = Rectangle(pos=header.pos,
                                        size=header.size)
        header.bind(pos=self._update_header_bg,
                    size=self._update_header_bg)

        self.header_title = Label(
            text=self.title,
            font_size='13sp', bold=True,
            color=Theme.HEADER_TEXT,
            size_hint_x=1,
            halign='center', valign='middle'
        )
        header.add_widget(self.header_title)

        close_btn = make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self._do_cancel(),
            size=(dp(28), dp(26)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        header.add_widget(close_btn)

        return header

    def _update_header_bg(self, *args):
        self._header_bg.pos = self.children[-1].pos
        self._header_bg.size = self.children[-1].size

    # ============================================================
    # ================== CONTENT =================================
    # ============================================================

    def _build_content_scroll(self):
        scroll = ScrollView(size_hint=(1, 1))
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            padding=[dp(8), dp(6), dp(8), dp(6)],
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.build_content()
        scroll.add_widget(self.content)
        return scroll

    def build_content(self):
        pass

    # ============================================================
    # ================== FOOTER (compact 48dp) ===================
    # ============================================================

    def _build_footer(self):
        footer = BoxLayout(size_hint_y=None, height=dp(48),
                           spacing=dp(6),
                           padding=[dp(8), dp(4), dp(8), dp(4)])
        with footer.canvas.before:
            Color(*Theme.SECTION_BG)
            self._footer_bg = Rectangle(pos=footer.pos, size=footer.size)
        footer.bind(pos=self._update_footer_bg,
                    size=self._update_footer_bg)

        # Extra buttons (e.g. Physical)
        extra = self.build_extra_footer_buttons()
        for btn in extra:
            footer.add_widget(btn)

        # Spacer
        footer.add_widget(Label(size_hint_x=1))

        if self.mode == "wizard":
            self._build_wizard_buttons(footer)
        else:
            self._build_standalone_buttons(footer)

        return footer

    def _update_footer_bg(self, *args):
        footer = self.children[0]
        self._footer_bg.pos = footer.pos
        self._footer_bg.size = footer.size

    def _build_wizard_buttons(self, footer):
        # Open (first page only)
        if self.is_first_page:
            open_btn = make_icon_text_button(
                text='Open', icon_name='open',
                on_press=lambda x: self._do_open(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_SUCCESS_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(open_btn)

        # Back (not on first page)
        if not self.is_first_page:
            back_btn = make_icon_text_button(
                text='Back', icon_name='back',
                on_press=lambda x: self._do_back(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_NEUTRAL_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(back_btn)

        # Save (last page) OR Next
        if self.is_last_page:
            save_btn = make_icon_text_button(
                text='Save', icon_name='save',
                on_press=lambda x: self._do_save(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_PRIMARY_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(save_btn)
        else:
            next_btn = make_icon_text_button(
                text='Next', icon_name='go',
                on_press=lambda x: self._do_next(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_PRIMARY_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(next_btn)

        # Cancel
        cancel_btn = make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self._do_cancel(),
            height=dp(38), icon_size=dp(20), font_size='12sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        )
        footer.add_widget(cancel_btn)

    def _build_standalone_buttons(self, footer):
        save_btn = make_icon_text_button(
            text='Save', icon_name='save',
            on_press=lambda x: self._do_save(),
            height=dp(38), icon_size=dp(20), font_size='12sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        footer.add_widget(save_btn)

        cancel_btn = make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self._do_cancel(),
            height=dp(38), icon_size=dp(20), font_size='12sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        )
        footer.add_widget(cancel_btn)

    def build_extra_footer_buttons(self):
        return []

    # ============================================================
    # ================== ACTIONS =================================
    # ============================================================

    def _do_next(self):
        if self.on_next:
            self.on_next(self)

    def _do_back(self):
        if self.on_back:
            self.on_back(self)

    def _do_cancel(self):
        if self.on_cancel:
            self.on_cancel(self)

    def _do_save(self):
        if self.on_save:
            self.on_save(self)

    def _do_open(self):
        if self.on_open:
            self.on_open(self)

    # ============================================================
    # ================== SUBCLASS API ============================
    # ============================================================

    def validate(self):
        return True

    def get_data(self):
        return {}

    def load_data(self, data):
        pass

    def get_focus_order(self):
        return []
