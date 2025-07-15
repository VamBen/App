from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import mainthread
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
import threading
import requests

OPENROUTER_API_KEY = "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"
common_qa = {
    "What is a normal period length?": "Usually 3–7 days.",
    "Can I swim on my period?": "Yes! Just use a tampon or menstrual cup.",
    "Is brown blood normal?": "Yes. Brown blood is just older blood that's been exposed to air.",
    "Can I get pregnant during my period?": "It's rare, but possible especially with irregular cycles.",
    "What's PMS?": "PMS stands for premenstrual syndrome. It includes mood swings, cramps, and more."
}
print("Q&A Screen loaded with the following:")
for q, a in common_qa.items():
    print(q)
    print(a)

class CustomQAItem(BoxLayout):
    def __init__(self, question, answer, **kwargs):
        super().__init__(orientation='vertical', spacing=5, size_hint_y=None, **kwargs)
        self.padding = 10

        with self.canvas.before:
            Color(1, 0.4, 0.6, 1)
            self.bg = RoundedRectangle(radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.question_button = Button(text=question, size_hint_y=None, height=40, background_normal='', background_color=(1, 0.4, 0.6, 1))
        self.answer_label = Label(text=answer, size_hint_y=None, height=0, opacity=0, halign="left", valign="top", color=(1, 1, 1, 1))
        self.answer_label.bind(texture_size=self.update_answer_height)
        self.question_button.bind(on_release=self.toggle_answer)

        self.add_widget(self.question_button)
        self.add_widget(self.answer_label)

    def update_rect(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def toggle_answer(self, instance):
        if self.answer_label.opacity == 0:
            self.answer_label.opacity = 1
            self.answer_label.height = self.answer_label.texture_size[1]
        else:
            self.answer_label.opacity = 0
            self.answer_label.height = 0

    def update_answer_height(self, instance, value):
        if self.answer_label.opacity == 1:
            self.answer_label.height = value[1]

class WhiteChatBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(padding=[15, 10, 15, 10], size_hint_y=None, **kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[12])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RoundedInputBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=50, padding=[15, 10, 15, 10], **kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[12])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class QAScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None,  padding=[10,10,10,60], spacing=10)
        self.content.bind(minimum_height=self.content.setter('height'))

        for question, answer in common_qa.items():
            item = CustomQAItem(question, answer)
            self.content.add_widget(item)

        prompt_label = Label(
            text="Have more questions? Ask away!",
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle"
        )
        prompt_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        self.content.add_widget(prompt_label)

        self.question_input = TextInput(
            hint_text="Ask anything about periods...",
            multiline=True,
            background_color=(0, 0, 0, 0),
            foreground_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30,
            padding=(4, 4),
            cursor_color=(0, 0, 0, 1)
        )


        input_box = RoundedInputBox()
        input_box.add_widget(self.question_input)
        self.content.add_widget(input_box)

        ask_btn = Button(
            text="Ask AI",
            size_hint=(None, None),
            height=40,
            width=100,
            pos_hint={"center_x": 0.5}
        )
        ask_btn.bind(on_press=self.ask_ai)
        self.content.add_widget(ask_btn)

        self.answer_label = Label(
            text="",
            size_hint_y=None,
            text_size=(self.width, None),
            halign="left",
            valign="top",
            color=(0, 0, 0, 1)
        )
        self.answer_label.bind(texture_size=self._update_answer_height, width=self._update_text_wrap)

        self.answer_box = WhiteChatBox(orientation="vertical")
        self.answer_box.add_widget(self.answer_label)
        self.answer_wrapper = BoxLayout(size_hint_y=None, padding=(10, 5))
        self.answer_wrapper.add_widget(self.answer_box)
        self.content.add_widget(self.answer_wrapper)

        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def ask_ai(self, instance):
        question = self.question_input.text.strip()
        if not question:
            self.update_answer("Please type a question.")
            return

        self.update_answer("Thinking...")
        threading.Thread(target=self._query_ai, args=(question,), daemon=True).start()

    def _query_ai(self, question):
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a friendly assistant that answers questions about menstruation in a helpful and respectful way."},
                    {"role": "user", "content": question}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            ai_reply = result["choices"][0]["message"]["content"]
            self.update_answer(ai_reply)

        except Exception as e:
            self.update_answer(f"\u274c Error: {str(e)}")

    @mainthread
    def update_answer(self, text):
        self.answer_label.text = str(text)

    def _update_answer_height(self, instance, size):
        self.answer_label.height = size[1]
        self.answer_box.height = self.answer_label.height + 20
        self.answer_wrapper.height = self.answer_box.height + 10

    def _update_text_wrap(self, instance, value):
        self.answer_label.text_size = (value - 30, None)
