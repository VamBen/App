from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
import threading
from kivy.uix.popup import Popup


# External modules (some possibly unused yet)
import geocoder
import requests
from plyer import gps  # Possibly unused
import webbrowser
import calendar
import datetime
from kivy.uix.spinner import Spinner


# Garden and local imports
from kivy_garden.mapview import MapView, MapMarkerPopup  # Possibly unused
from qa_screen import QAScreen
from settings import SettingsScreen
from cycle_chart import CycleChartScreen

# Set light pink background
Window.clearcolor = get_color_from_hex("#FFB6C1")


class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_image = Image(
            source="Welcome.jpg",
            size_hint=(None, None),
            size=(120, 120),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.add_widget(self.loading_image)


class WhiteDropdown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.container.spacing = 2
        self.container.padding = [5, 5]
        self.auto_width = False
        self.width = 200

    def add_widget(self, widget, index=0):
        widget.color = (0, 0, 0, 1)
        widget.background_normal = ''
        widget.background_color = (1, 1, 1, 1)
        return super().add_widget(widget, index)

# --- Calendar Screen ---

class CalendarWidget(BoxLayout):
    def __init__(self, on_date_change=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.today = datetime.date.today()
        self.year = self.today.year
        self.month = self.today.month
        self.selected_dates = {}
        self.on_date_change = on_date_change

        self.header = BoxLayout(size_hint_y=None, height=40, padding=[0, 5])
        self.calendar_grid = GridLayout(cols=7, spacing=3, padding=[10, 10, 10, 10])

        self.add_widget(self.header)
        self.add_widget(self.calendar_grid)

        self.build_header()
        self.build_calendar()

    def build_header(self):
        self.header.clear_widgets()
        prev_btn = Button(text="<<", size_hint_x=0.2, on_press=self.prev_month)
        next_btn = Button(text=">>", size_hint_x=0.2, on_press=self.next_month)
        month_label = Label(
            text=f"{calendar.month_name[self.month]} {self.year}",
            bold=True,
            font_size=20,
            color=(1, 1, 1, 1)
        )
        self.header.add_widget(prev_btn)
        self.header.add_widget(month_label)
        self.header.add_widget(next_btn)

    def build_calendar(self):
        self.calendar_grid.clear_widgets()
        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.calendar_grid.add_widget(Label(text=day, color=(1, 0, 0, 1), bold=True))

        cal = calendar.Calendar()
        for day in cal.itermonthdays(self.year, self.month):
            if day == 0:
                self.calendar_grid.add_widget(Label(text=""))
            else:
                date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                mood = self.selected_dates.get(date_str, "")

                btn = Button(
                    text=f"{day}\n{mood}" if mood else str(day),
                    background_normal='',
                    background_color=(1, 1, 1, 1),
                    color=(1, 0, 0, 1),
                    halign="center",
                    valign="middle"
                )

                if date_str == self.today.strftime("%Y-%m-%d"):
                    btn.background_color = get_color_from_hex("#E6CCFF")

                if mood:
                    btn.background_color = get_color_from_hex("#C71585")
                    btn.color = (1, 1, 1, 1)

                btn.bind(on_press=lambda instance, d=day: self.on_day_pressed(d))
                self.calendar_grid.add_widget(btn)

    def on_day_pressed(self, day):
        date_str = f"{self.year}-{self.month:02d}-{day:02d}"
        if date_str in self.selected_dates:
            del self.selected_dates[date_str]
            self.build_calendar()
            if self.on_date_change:
                self.on_date_change(self.get_latest_selected_date())
        else:
            self.show_mood_selector(day)

    def show_mood_selector(self, day):
        date_str = f"{self.year}-{self.month:02d}-{day:02d}"
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        spinner = Spinner(
            text="Select Mood",
            values=(":D", ":)", ":/", ":(", "T^T"),
            size_hint=(1, None),
            height=44,
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        spinner.dropdown_cls = WhiteDropdown

        def on_select(instance, value):
            self.selected_dates[date_str] = value
            self.build_calendar()
            popup.dismiss()
            if self.on_date_change:
                self.on_date_change(self.get_latest_selected_date())

        spinner.bind(text=on_select)

        layout.add_widget(Label(text=f"How did you feel on {day}?", color=(0, 0, 0, 1)))
        layout.add_widget(spinner)

        popup = Popup(
            title="Pick your mood 🎀",
            content=layout,
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()

    def get_latest_selected_date(self):
        if not self.selected_dates:
            return None
        return max(datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in self.selected_dates)

    def prev_month(self, instance):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.build_header()
        self.build_calendar()

    def next_month(self, instance):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.build_header()
        self.build_calendar()


# --- Screen: Tracker ---
class TrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=[20, 20, 20, 80], spacing=10)

        title_label = Label(
            text="˚˖𓍢🌷✧˚.🎀⋆period tracker",
            font_size=36,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15),
            halign="center",
            valign="middle",
        )
        title_label.bind(size=self._update_text_size)

        self.layout.add_widget(title_label)

        self.estimated_label = Label(
            text="",
            font_size=16,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1)
        )

        self.calendar = CalendarWidget(
            size_hint=(1, 0.75),
            on_date_change=self.update_estimated_date
        )

        self.layout.add_widget(self.calendar)
        self.layout.add_widget(self.estimated_label)

        self.add_widget(self.layout)

        self.update_estimated_date()

    def _update_text_size(self, instance, value):
        instance.text_size = value  # Ensures halign and valign work

    def update_estimated_date(self, last_date=None):
        if not last_date:
            last_date = self.calendar.get_latest_selected_date()

        if last_date:
            estimated = last_date + datetime.timedelta(days=28)
        else:
            estimated = datetime.date.today() + datetime.timedelta(days=28)

        self.estimated_label.text = f"🩸 Estimated next period on: {estimated.strftime('%d %B %Y')}"


# --- Screen: Doctors ---

class DoctorsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.map_view = None
        self.loading_image = None
        Clock.schedule_once(self.setup_map, 0.5)

    def setup_map(self, dt):
        # Show loading image
        self.loading_image = Image(source="Welcome.jpg", size_hint=(None, None), size=(100, 100),
                                   pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self.loading_image)

        # Center on Noida
        lat, lon = 28.5355, 77.3910  # Noida coordinates
        self.map_view = MapView(zoom=12, lat=lat, lon=lon, size_hint=(1, 1))

        # Add map to screen (behind loading image)
        self.add_widget(self.map_view)

        # Wait briefly and load cached data (if available)
        Clock.schedule_once(lambda dt: self.load_cached_clinics(lat, lon), 0.5)

    def load_cached_clinics(self, lat, lon):
        app = App.get_running_app()

        def check_and_load(dt):
            if getattr(app, "api_data_ready", False):
                print("[INFO] Cached API data is ready. Loading clinics.")
                self._load_clinics_from_data(app.api_data)
            else:
                print("[INFO] Waiting for cached API data...")
                Clock.schedule_once(check_and_load, 0.5)

        check_and_load(0)

    def _load_clinics_from_data(self, data):
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            name = props.get("name", "").lower()
            categories = props.get("categories", [])

            is_hospital = any("hospital" in cat for cat in categories) or "hospital" in name
            is_gyne = any(word in name for word in ["gyne", "gynae", "women", "obstetric"])

            if not (is_hospital or is_gyne):
                continue

            display_name = props.get("name", "")
            if not display_name or display_name.lower() in ["clinic", "women clinic", "hospital"]:
                display_name = props.get("address_line1") or props.get("formatted") or "Women's Clinic"

            lat = feature["geometry"]["coordinates"][1]
            lon = feature["geometry"]["coordinates"][0]

            self.add_marker(lat, lon, display_name)

        # Remove loading image
        if self.loading_image and self.loading_image.parent:
            self.remove_widget(self.loading_image)

    def add_marker(self, lat, lon, display_name):
        marker = MapMarkerPopup(lat=lat, lon=lon)

        label = Label(
            text=display_name,
            color=(0.86, 0.08, 0.24, 1),  # Dark pink
            bold=True,
            size_hint=(None, None)
        )
        label.texture_update()
        label.size = label.texture_size

        label_box = BoxLayout(size=label.size, size_hint=(None, None), padding=6)
        label_box.add_widget(label)

        with label_box.canvas.before:
            Color(1, 1, 1, 0.75)
            bg_rect = RoundedRectangle(radius=[8], size=label_box.size, pos=label_box.pos)

        def update_bg(*args):
            bg_rect.size = label_box.size
            bg_rect.pos = label_box.pos

        label_box.bind(size=update_bg, pos=update_bg)

        marker.add_widget(label_box)
        self.map_view.add_widget(marker)



class TipsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(
            text="📖 Wellness Tips & Period Articles coming soon 💡",
            font_size=20,
            color=(1, 1, 1, 1),
            halign="center"
        ))


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        img = Image(
            source="Welcome.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.add_widget(img)


class PeriodApp(App):
    def build(self):
        # Root layout will hold either splash or main app
        self.root_layout = BoxLayout(orientation='vertical')
        self.sm = ScreenManager(transition=FadeTransition())

        splash = SplashScreen(name="splash")
        self.sm.add_widget(splash)
        self.sm.current = "splash"

        self.root_layout.add_widget(self.sm)

        # After 7 seconds, load the actual app screens
        Clock.schedule_once(self.load_main_app, 5)

        return self.root_layout

    def build(self):
        self.api_data_ready = False  # Flag to check if API is ready
        self.api_data = None  # Store fetched data here

        # Start loading API data in background
        threading.Thread(target=self.load_api_data, daemon=True).start()

        # Set up splash screen
        self.root_layout = BoxLayout(orientation='vertical')
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(SplashScreen(name="splash"))
        self.sm.current = "splash"
        self.root_layout.add_widget(self.sm)

        # After 7 seconds, load main app regardless
        Clock.schedule_once(self.load_main_app, 4)

        return self.root_layout

    def load_api_data(self):
        try:
            lat, lon = 28.5355, 77.391
            radius = 50000
            api_key = "109d8f303029447b9c0dafb117708580"

            url = f"https://api.geoapify.com/v2/places?categories=healthcare&filter=circle:{lon},{lat},{radius}&bias=proximity:{lon},{lat}&limit=100&apiKey={api_key}"
            response = requests.get(url)

            if response.status_code == 200:
                self.api_data = response.json()
                self.api_data_ready = True
                print("[INFO] Map API data loaded in background.")
            else:
                print(f"[WARNING] API request failed with status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Failed to load API in background: {e}")


    def load_main_app(self, dt):
        # Add main screens
        self.sm.add_widget(TrackerScreen(name="tracker"))
        self.sm.add_widget(DoctorsScreen(name="doctors"))
        self.sm.add_widget(QAScreen(name="Q&A"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.current = "tracker"

        # Create footer nav
        footer = BoxLayout(size_hint_y=0.1, padding=5, spacing=10)
        buttons = [
            ("🗓 Tracker", "tracker"),
            ("🩺 Doctors", "doctors"),
            ("📖 Q&A", "Q&A"),
            ("⚙️ Settings", "settings")
        ]
        for label, screen_name in buttons:
            btn = Button(
                text=label,
                on_press=lambda btn, s=screen_name: self.sm.switch_to(self.sm.get_screen(s))
            )
            footer.add_widget(btn)

        # Add footer to root layout
        self.root_layout.add_widget(footer)


if __name__ == "__main__":
    PeriodApp().run()