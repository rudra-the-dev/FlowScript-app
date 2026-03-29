import traceback
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

# Ensure lexer.py and interpreter.py are in the same folder!
try:
    from lexer import Lexer
    from interpreter import Interpreter
except ImportError:
    # Fallback for initial testing if files aren't moved yet
    class Lexer: pass
    class Interpreter: pass

Window.clearcolor = get_color_from_hex('#0d0d0f')

# --- ANDROID HELPER FUNCTIONS ---

def request_screen_capture():
    try:
        from jnius import autoclass
        # Ensure 'app.flowscript' matches the package in your Java files
        ScreenCapture = autoclass('app.flowscript.FlowScriptScreenCapture')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        ScreenCapture.requestPermission(activity)
        return True
    except Exception as e:
        print(f"Screen capture request error: {e}")
        return False

def is_accessibility_enabled():
    try:
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        # FIXED: Properly bridge the Android Settings class
        Settings = autoclass('android.provider.Settings')

        # Access Secure settings via the Java bridge
        enabled_services = Settings.Secure.getString(
            context.getContentResolver(),
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )

        if enabled_services:
            return 'app.flowscript.FlowScriptService' in enabled_services
        return False
    except Exception as e:
        print(f"Accessibility check error: {e}")
        # Return True for desktop/testing environments to avoid the banner
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

# --- UI COMPONENTS ---

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
            markup=True, font_size=dp(12), halign='left', valign='middle', size_hint_x=0.72
        )
        msg.bind(size=msg.setter('text_size'))

        btn = Button(
            text='Enable', size_hint_x=0.28, size_hint_y=None, height=dp(34),
            background_color=get_color_from_hex('#f59e0b'),
            color=get_color_from_hex('#000000'), bold=True, font_size=dp(12)
        )
        btn.bind(on_press=lambda x: on_enable())
        self.add_widget(msg); self.add_widget(btn)

    def _upd(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

class FlowScriptApp(App):
    def build(self):
        # WRAP EVERYTHING IN A TRY-EXCEPT TO PREVENT SILENT CRASHES
        try:
            self.title = 'FlowScript'
            self.root_layout = BoxLayout(orientation='vertical', spacing=dp(1))

            # Header
            titlebar = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(14), 0], spacing=dp(10))
            with titlebar.canvas.before:
                Color(*get_color_from_hex('#131316'))
                self.title_rect = Rectangle(pos=titlebar.pos, size=titlebar.size)
            titlebar.bind(pos=self._update_rect, size=self._update_rect)

            title_label = Label(text='FlowScript', font_size=dp(18), bold=True, color=get_color_from_hex('#e8e8f0'),
                               size_hint_x=0.7, halign='left', valign='middle')
            title_label.bind(size=title_label.setter('text_size'))

            run_btn = Button(text='RUN', size_hint_x=0.3, size_hint_y=None, height=dp(38),
                            background_color=get_color_from_hex('#7c6af7'), color=(1,1,1,1),
                            bold=True, font_size=dp(14))
            run_btn.bind(on_press=self.run_code)
            titlebar.add_widget(title_label); titlebar.add_widget(run_btn)

            # Editor
            self.editor = TextInput(
                hint_text='Write FlowScript here...\n\nsay "Hello World"',
                background_color=get_color_from_hex('#1e1e24'), foreground_color=get_color_from_hex('#e8e8f0'),
                cursor_color=get_color_from_hex('#7c6af7'), font_size=dp(13), padding=[dp(14), dp(14)],
                size_hint_y=0.55, multiline=True
            )

            # Output
            output_label = Label(text='OUTPUT', font_size=dp(10), bold=True, color=get_color_from_hex('#555570'),
                                size_hint_y=None, height=dp(28), halign='left', valign='middle', padding_x=dp(14))
            output_label.bind(size=output_label.setter('text_size'))

            scroll = ScrollView(size_hint_y=0.45, do_scroll_x=True, do_scroll_y=True)
            self.output=Label(


    text='Press RUN to execute your FlowScript code',
    color=get_color_from_hex('#555570'),
    font_size=dp(12),
    halign='left',
    valign='top',
    markup=True,
    size_hint_y=None,
    padding=[dp(14), dp(8)]
)

            self.output.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

            self.output.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            scroll.add_widget(self.output)

            self.root_layout.add_widget(titlebar)
            self.root_layout.add_widget(self.editor)
            self.root_layout.add_widget(output_label)
            self.root_layout.add_widget(scroll)

            Clock.schedule_once(self.check_accessibility, 6)
            return self.root_layout

        except Exception:
            # If the app crashes on boot, show the error in a Label
            return Label(text=f"CRASH ON START:\n\n{traceback.format_exc()}", color=(1,0,0,1))

    def _update_rect(self, instance, value):
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size

    def check_accessibility(self, dt):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.POST_NOTIFICATIONS,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])
        except: pass

        if not is_accessibility_enabled():
            banner = PermissionBanner(on_enable=self.go_to_accessibility)
            self.root_layout.add_widget(banner)

        self.check_screen_capture()

    def check_screen_capture(self):
        try:
            from jnius import autoclass
            ScreenCapture = autoclass('app.flowscript.FlowScriptScreenCapture')
            if not ScreenCapture.hasPermission():
                self.show_screen_capture_dialog()
        except: pass

    def show_screen_capture_dialog(self):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        msg = Label(text='[b]Screen capture needed[/b]\n\nFlowScript needs permission to automate apps.',
                    markup=True, font_size=dp(13), color=get_color_from_hex('#e8e8f0'))
        allow_btn = Button(text='Allow Screen Capture', size_hint_y=None, height=dp(44),
                          background_color=get_color_from_hex('#7c6af7'), color=(1,1,1,1), bold=True)
        content.add_widget(msg); content.add_widget(allow_btn)

        popup = Popup(title='Permission Required', content=content, size_hint=(0.88, 0.45))
        allow_btn.bind(on_press=lambda x: [popup.dismiss(), request_screen_capture()])
        popup.open()

    def go_to_accessibility(self):
        open_accessibility_settings()

    def run_code(self, instance):
        code = self.editor.text.strip()
        if not code: return

        output_lines = []
        class OutputCapture:
            def write(self, text):
                if text.strip(): output_lines.append(('out', str(text)))
            def flush(self): pass

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
        result = ""
        for kind, text in output_lines:
            color = "#f87171" if kind == 'err' else "#4ade80"
            result += f'[color={color}]{text}[/color]\n'
        self.output.text = result if result else "Success (No Output)"

if __name__ == '__main__':
    FlowScriptApp().run()