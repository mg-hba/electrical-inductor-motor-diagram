"""
================================================================================
File: dialogs/docs_viewer.py
Purpose: Show a markdown document with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


_INSTANCE_OPEN = False


class DocsViewer(Popup):

    def __init__(self, title, markdown_text, docs_manager, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.94, 0.88)
        self.background_color = [0, 0, 0, 0.3]
        self.auto_dismiss = True

        self.markdown_text = markdown_text or ''
        self.docs_manager = docs_manager
        self.raw_mode = False

        self._built = False
        self._bg = None
        self.scroll = None
        self.content = None
        self.raw_btn = None

        self.bind(on_dismiss=self._on_close)
        self._safe_build_ui(title)
        self._safe_refresh_content()

    def _on_close(self, *args):
        global _INSTANCE_OPEN
        _INSTANCE_OPEN = False

    def _safe_build_ui(self, title):
        if self._built:
            return
        try:
            self._build_ui_inner(title)
            self._built = True
        except Exception as e:
            print("DocsViewer._build_ui error:", e)

    def _safe_refresh_content(self):
        try:
            self._refresh_content_inner()
        except Exception as e:
            print("DocsViewer._refresh error:", e)

    def _build_ui_inner(self, title):
        # Clean previous state
        if hasattr(self, 'content') and self.content is not None:
            if self.content.parent is not None:
                try:
                    self.content.parent.remove_widget(self.content)
                except Exception:
                    pass

        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            self._bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(
            pos=lambda i, v: setattr(self._bg, 'pos', i.pos),
            size=lambda i, v: setattr(self._bg, 'size', i.size)
        )

        header = BoxLayout(
            size_hint_y=None, height=dp(44),
            spacing=dp(6),
            padding=[dp(8), dp(6), dp(8), dp(6)]
        )
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(
            pos=lambda i, v: setattr(hbg, 'pos', i.pos),
            size=lambda i, v: setattr(hbg, 'size', i.size)
        )

        header.add_widget(make_icon_button(
            text='<', icon_name='back',
            on_press=lambda x: self.dismiss(),
            size=(dp(32), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))

        title_lbl = Label(
            text=str(title) + get_version_suffix(),
            font_size='13sp', bold=True,
            color=Theme.HEADER_TEXT,
            size_hint_x=1,
            halign='center', valign='middle'
        )
        header.add_widget(title_lbl)

        self.raw_btn = make_icon_button(
            text='Raw', icon_name='view_raw',
            on_press=self.toggle_raw,
            size=(dp(44), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        header.add_widget(self.raw_btn)

        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(30), dp(30)),
            bg_color=[0.8, 0.2, 0.2, 1],
        ))

        main.add_widget(header)

        self.scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(2),
            size_hint_y=None,
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        main.add_widget(self.scroll)

        self.add_widget(main)

    def toggle_raw(self, instance=None):
        self.raw_mode = not self.raw_mode
        self._safe_refresh_content()

    def _refresh_content_inner(self):
        if self.content is None:
            return
        if self.content.parent is None:
            # Content got detached — try to re-add
            try:
                if hasattr(self, 'scroll') and self.scroll is not None:
                    self.scroll.add_widget(self.content)
            except Exception:
                return
        self.content.clear_widgets()

        if self.raw_mode:
            lbl = Label(
                text=self.markdown_text,
                font_size='12sp',
                color=[0.1, 0.1, 0.1, 1],
                size_hint_y=None,
                halign='left',
                valign='top',
                text_size=(Window.width * 0.85, None)
            )
            lbl.bind(texture_size=lambda i, ts: setattr(i, 'height', ts[1]))
            self.content.add_widget(lbl)
            return

        try:
            items = self.docs_manager.markdown_to_items(self.markdown_text)
        except Exception as e:
            print("markdown_to_items error:", e)
            items = [{'text': self.markdown_text, 'font_size': '12sp'}]

        tw = max(200, Window.width * 0.85)
        for item in items:
            lbl = Label(
                text=item.get('text', ''),
                font_size=item.get('font_size', '13sp'),
                bold=item.get('bold', False),
                italic=item.get('italic', False),
                color=item.get('color', [0, 0, 0, 1]),
                size_hint_y=None,
                halign='left',
                valign='top',
                text_size=(tw, None)
            )
            lbl.bind(
                texture_size=lambda i, ts: setattr(
                    i, 'height', max(ts[1] + dp(2), dp(16))
                )
            )
            self.content.add_widget(lbl)


def show_docs_viewer(title, markdown_text, docs_manager):
    global _INSTANCE_OPEN
    if _INSTANCE_OPEN:
        print("DocsViewer: already open, skipping")
        return
    _INSTANCE_OPEN = True
    try:
        viewer = DocsViewer(title, markdown_text, docs_manager)
        viewer.open()
    except Exception as e:
        print("show_docs_viewer error:", e)
        _INSTANCE_OPEN = False