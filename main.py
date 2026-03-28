from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class FlowScriptApp(App):
    def build(self):
        # We return a Layout instead of None to keep the Window alive
        layout = BoxLayout(orientation='vertical')
        
        layout.add_widget(Label(text="FlowScript Engine Active", font_size='20sp'))
        
        btn = Button(text="Run Automation Test", size_hint=(1, 0.2))
        # btn.bind(on_press=self.start_logic) # You can link your android_bridge here later
        layout.add_widget(btn)
        
        return layout

if __name__ == "__main__":
    FlowScriptApp().run()
