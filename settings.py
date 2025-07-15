from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.core.window import Window


class SettingsCard(BoxLayout):
    def __init__(self, title, right_widget, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=8,
                         size_hint_y=None, height=100, **kwargs)

        with self.canvas.before:
            Color(1, 0.2, 0.6, 1)  # dark pink (outline)
            self.bg = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 15], width=1.5)
        self.bind(pos=self.update_bg, size=self.update_bg)

        label = Label(text=title, color=(1, 1, 1, 1),
                      size_hint_y=0.4, halign="left", valign="middle")
        label.bind(size=label.setter('text_size'))

        right_widget.size_hint_y = 0.6

        self.add_widget(label)
        self.add_widget(right_widget)

    def update_bg(self, *args):
        self.bg.rounded_rectangle = [self.x, self.y, self.width, self.height, 15]


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        title = Label(
            text="⚙️ Settings",
            font_size=28,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=50
        )
        layout.add_widget(title)

        # --- Dark Mode ---
        self.dark_mode_switch = Switch(active=False)
        self.dark_mode_switch.bind(active=self.toggle_dark_mode)
        layout.add_widget(SettingsCard("Dark Mode", self.dark_mode_switch))

        # --- Average Cycle Length ---
        self.cycle_input = TextInput(
            text="28",
            multiline=False,
            input_filter='int',
            size_hint=(1, None),
            height=40,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10]
        )
        layout.add_widget(SettingsCard("Average Cycle Length (days)", self.cycle_input))

        # --- Notifications Toggle ---
        self.notifications_switch = Switch(active=True)
        layout.add_widget(SettingsCard("Notifications", self.notifications_switch))

        # --- Save Button ---
        save_button = Button(
            text="Save Settings 💾",
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex("#ffffff"),
            color=(0, 0, 0, 1),
            bold=True
        )
        save_button.bind(on_press=self.save_settings)
        layout.add_widget(save_button)

        self.add_widget(layout)

    def toggle_dark_mode(self, instance, value):
        if value:
            Window.clearcolor = get_color_from_hex("#1C1C1C")
        else:
            Window.clearcolor = get_color_from_hex("#FFB6C1")

    def save_settings(self, instance):
        try:
            cycle_length = int(self.cycle_input.text)
        except ValueError:
            cycle_length = 28  # fallback
        print("🔧 Settings saved:")
        print(f" - Dark Mode: {self.dark_mode_switch.active}")
        print(f" - Avg Cycle Length: {cycle_length}")
        print(f" - Notifications: {self.notifications_switch.active}")
