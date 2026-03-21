from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from lexer import Lexer
from interpreter import Interpreter

Window.clearcolor = get_color_from_hex('#0d0d0f')


def is_accessibility_enabled():
    try:
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        AccessibilityManager = autoclass('android.view.accessibility.AccessibilityManager')
        am = context.getSystemService(context.ACCESSIBILITY_SERVICE)
        enabled_services = android.provider.Settings.Secure.getString(
            context.getContentResolver(),
            android.provider.Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )
        return enabled_services and 'app.flowscript.FlowScriptService' in enabled_services
    except:
        return True


def open_accessibility_settings():
    try:
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    except Exception as e:
        print(f"Could not open accessibility settings: {e}")


class PermissionBanner(BoxLayout):
    def __init__(self, on_enable, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(52)
        self.padding = [dp(12), 0]
        self.spacing = dp(8)

        with self.canvas.before:
            Color(*get_color_from_hex('#2d1f0a'))
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        msg = Label(
            text='[color=#fbbf24]⚠ Enable Accessibility to use automations[/color]',
            markup=True,
            font_size=dp(12),
            halign='left',
            valign='middle',
            size_hint_x=0.72
        )
        msg.bind(size=msg.setter('text_size'))

        btn = Button(
            text='Enable',
            size_hint_x=0.28,
            size_hint_y=None,
            height=dp(34),
            background_color=get_color_from_hex('#f59e0b'),
            color=get_color_from_hex('#000000'),
            bold=True,
            font_size=dp(12)
        )
        btn.bind(on_press=lambda x: on_enable())

        self.add_widget(msg)
        self.add_widget(btn)

    def _upd(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size


class FlowScriptApp(App):

    def build(self):
        self.title = 'FlowScript'
        self.root_layout = BoxLayout(orientation='vertical', spacing=dp(1))

        titlebar = BoxLayout(
            size_hint_y=None,
            height=dp(52),
            padding=[dp(14), 0],
            spacing=dp(10)
        )
        with titlebar.canvas.before:
            Color(*get_color_from_hex('#131316'))
            self.title_rect = Rectangle(pos=titlebar.pos, size=titlebar.size)
        titlebar.bind(pos=self._update_rect, size=self._update_rect)

        title_label = Label(
            text='FlowScript',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex('#e8e8f0'),
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        run_btn = Button(
            text='RUN',
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(38),
            background_color=get_color_from_hex('#7c6af7'),
            color=get_color_from_hex('#ffffff'),
            bold=True,
            font_size=dp(14)
        )
        run_btn.bind(on_press=self.run_code)

        titlebar.add_widget(title_label)
        titlebar.add_widget(run_btn)

        self.editor = TextInput(
            hint_text='Write FlowScript here...\n\nsay "Hello World"',
            background_color=get_color_from_hex('#1e1e24'),
            foreground_color=get_color_from_hex('#e8e8f0'),
            cursor_color=get_color_from_hex('#7c6af7'),
            font_size=dp(13),
            padding=[dp(14), dp(14)],
            size_hint_y=0.55,
            multiline=True,
        )

        output_label = Label(
            text='OUTPUT',
            font_size=dp(10),
            bold=True,
            color=get_color_from_hex('#555570'),
            size_hint_y=None,
            height=dp(28),
            halign='left',
            valign='middle',
            padding_x=dp(14)
        )
        output_label.bind(size=output_label.setter('text_size'))

        scroll = ScrollView(size_hint_y=0.45)
        self.output = Label(
            text='Press RUN to execute your FlowScript code',
            color=get_color_from_hex('#555570'),
            font_size=dp(12),
            halign='left',
            valign='top',
            markup=True,
            size_hint_y=None,
            padding=[dp(14), dp(8)]
        )
        self.output.bind(texture_size=self.output.setter('size'))
        scroll.add_widget(self.output)

        self.root_layout.add_widget(titlebar)
        self.root_layout.add_widget(self.editor)
        self.root_layout.add_widget(output_label)
        self.root_layout.add_widget(scroll)

        Clock.schedule_once(self.check_accessibility, 1)

        return self.root_layout

    def check_accessibility(self, dt):
        if not is_accessibility_enabled():
            banner = PermissionBanner(on_enable=self.go_to_accessibility)
            self.root_layout.add_widget(banner, index=len(self.root_layout.children))
            self.accessibility_banner = banner

    def go_to_accessibility(self):
        open_accessibility_settings()
        self.show_instructions()

    def show_instructions(self):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        msg = Label(
            text='[b]How to enable FlowScript:[/b]\n\n1. Find [color=#7c6af7]FlowScript[/color] in the list\n2. Tap it\n3. Turn on the toggle\n4. Tap Allow\n5. Come back here',
            markup=True,
            font_size=dp(14),
            color=get_color_from_hex('#e8e8f0'),
            halign='left',
            valign='top'
        )
        msg.bind(size=msg.setter('text_size'))

        done_btn = Button(
            text='Done',
            size_hint_y=None,
            height=dp(44),
            background_color=get_color_from_hex('#7c6af7'),
            color=get_color_from_hex('#ffffff'),
            bold=True
        )

        content.add_widget(msg)
        content.add_widget(done_btn)

        popup = Popup(
            title='Enable Accessibility',
            content=content,
            size_hint=(0.88, 0.55),
            background_color=get_color_from_hex('#0d0d1f'),
            separator_color=get_color_from_hex('#7c6af7')
        )
        done_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _update_rect(self, instance, value):
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size

    def run_code(self, instance):
        code = self.editor.text.strip()
        if not code:
            return

        output_lines = []

        class OutputCapture:
            def write(self, text):
                output_lines.append(('out', str(text)))
            def flush(self):
                pass

        import sys
        old_stdout = sys.stdout
        sys.stdout = OutputCapture()

        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            interp = Interpreter(tokens)
            interp.run()
        except Exception as e:
            output_lines.append(('err', str(e)))

        sys.stdout = old_stdout

        if not output_lines:
            self.output.text = '[color=#555570]No output[/color]'
            return

        result = ''
        for kind, text in output_lines:
            if kind == 'err':
                result += f'[color=#f87171]ERROR: {text}[/color]\n'
            else:
                result += f'[color=#4ade80]> {text}[/color]\n'

        self.output.text = result.strip()


if __name__ == '__main__':
    FlowScriptApp().run()
