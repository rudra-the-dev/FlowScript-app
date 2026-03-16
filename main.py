from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from lexer import Lexer
from interpreter import Interpreter

Window.clearcolor = get_color_from_hex('#0d0d0f')

class FlowScriptApp(App):

    def build(self):
        self.title = 'FlowScript'
        root = BoxLayout(orientation='vertical', spacing=dp(1))

        titlebar = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            padding=[dp(14), 0],
            spacing=dp(10)
        )
        titlebar.canvas.before.clear()
        with titlebar.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex('#131316'))
            self.title_rect = Rectangle(pos=titlebar.pos, size=titlebar.size)
        titlebar.bind(pos=self._update_rect, size=self._update_rect)

        title_label = Label(
            text='FlowScript',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex('#e8e8f0'),
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        run_btn = Button(
            text='▶  Run',
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(34),
            background_color=get_color_from_hex('#7c6af7'),
            color=get_color_from_hex('#ffffff'),
            bold=True,
            font_size=dp(13)
        )
        run_btn.bind(on_press=self.run_code)

        titlebar.add_widget(title_label)
        titlebar.add_widget(run_btn)

        self.editor = TextInput(
            hint_text='Write FlowScript here...\n\nsay "Hello World"',
            background_color=get_color_from_hex('#1e1e24'),
            foreground_color=get_color_from_hex('#e8e8f0'),
            cursor_color=get_color_from_hex('#7c6af7'),
            font_name='RobotoMono-Regular',
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
            text='Press Run to execute your FlowScript code',
            color=get_color_from_hex('#555570'),
            font_name='RobotoMono-Regular',
            font_size=dp(12),
            halign='left',
            valign='top',
            markup=True,
            size_hint_y=None,
            padding=[dp(14), dp(8)]
        )
        self.output.bind(texture_size=self.output.setter('size'))
        scroll.add_widget(self.output)

        root.add_widget(titlebar)
        root.add_widget(self.editor)
        root.add_widget(output_label)
        root.add_widget(scroll)

        return root

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
                result += f'[color=#f87171]✗  {text}[/color]\n'
            else:
                result += f'[color=#4ade80]›  {text}[/color]\n'

        self.output.text = result.strip()


if __name__ == '__main__':
    FlowScriptApp().run()
