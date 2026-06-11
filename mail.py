from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

# Чёрно-жёлтая тема
Window.clearcolor = (0, 0, 0, 1)  # Чёрный фон


class RealmeBrowser(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.current_url = "https://www.google.com"
        self.history = []
        self.bookmarks = []

        # Верхняя панель
        nav = BoxLayout(size_hint=(1, 0.08), spacing=2, padding=[5, 2, 5, 2])

        # Установка цвета фона панели через canvas
        with nav.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Тёмно-серый
            self.nav_rect = Rectangle(size=nav.size, pos=nav.pos)
        nav.bind(size=self._update_nav_rect, pos=self._update_nav_rect)

        # Кнопка "Назад"
        btn_back = Button(text="◀", background_color=(1, 0.8, 0, 1), background_normal='', size_hint=(0.1, 1))
        btn_back.bind(on_press=lambda x: self.go_back())

        # Кнопка "Вперёд"
        btn_forward = Button(text="▶", background_color=(1, 0.8, 0, 1), background_normal='', size_hint=(0.1, 1))
        btn_forward.bind(on_press=lambda x: self.go_forward())

        # Кнопка "Обновить"
        btn_refresh = Button(text="⟳", background_color=(1, 0.8, 0, 1), background_normal='', size_hint=(0.1, 1))
        btn_refresh.bind(on_press=lambda x: self.refresh())

        # Адресная строка
        self.url_input = TextInput(
            text=self.current_url,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 0.8, 0, 1),
            cursor_color=(1, 0.8, 0, 1),
            size_hint=(0.5, 1),
            font_size='14sp'
        )
        self.url_input.bind(on_text_validate=self.load_url)

        # Кнопка "Домой"
        btn_home = Button(text="🏠", background_color=(1, 0.8, 0, 1), background_normal='', size_hint=(0.1, 1))
        btn_home.bind(on_press=lambda x: self.go_home())

        # Кнопка "Закладки"
        btn_bookmark = Button(text="★", background_color=(1, 0.8, 0, 1), background_normal='', size_hint=(0.1, 1))
        btn_bookmark.bind(on_press=lambda x: self.add_bookmark())

        nav.add_widget(btn_back)
        nav.add_widget(btn_forward)
        nav.add_widget(btn_refresh)
        nav.add_widget(self.url_input)
        nav.add_widget(btn_home)
        nav.add_widget(btn_bookmark)

        # WebView (только на Android, на Windows показывает заглушку)
        try:
            from kivy.uix.webview import WebView
            self.webview = WebView(url=self.current_url)
            self.webview.bind(on_load=self.on_page_load)
            self.add_widget(nav)
            self.add_widget(self.webview)
        except ImportError:
            self.add_widget(nav)
            self.add_widget(Label(text="WebView доступен только на Android", color=(1, 0.8, 0, 1), size_hint=(1, 0.9)))

        # Нижняя панель
        bottom = BoxLayout(size_hint=(1, 0.06), spacing=2)
        btn_history = Button(text="📜 История", background_color=(0.2, 0.2, 0.2, 1), color=(1, 0.8, 0, 1))
        btn_history.bind(on_press=self.show_history)

        btn_bookmarks_list = Button(text="🔖 Закладки", background_color=(0.2, 0.2, 0.2, 1), color=(1, 0.8, 0, 1))
        btn_bookmarks_list.bind(on_press=self.show_bookmarks)

        bottom.add_widget(btn_history)
        bottom.add_widget(btn_bookmarks_list)
        self.add_widget(bottom)

    def _update_nav_rect(self, instance, value):
        """Обновление прямоугольника фона"""
        self.nav_rect.size = instance.size
        self.nav_rect.pos = instance.pos

    def load_bookmarks(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('bookmarks.json')
            return store.get('bookmarks')['list']
        except:
            return []

    def save_bookmarks(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('bookmarks.json')
            store.put('bookmarks', list=self.bookmarks)
        except:
            pass

    def load_url(self, instance):
        url = self.url_input.text
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            self.webview.url = url
            self.current_url = url
            self.history.append(url)
        except:
            pass

    def on_page_load(self, instance, value):
        try:
            self.url_input.text = self.webview.url
            self.current_url = self.webview.url
        except:
            pass

    def go_back(self):
        try:
            if self.webview.can_go_back:
                self.webview.go_back()
        except:
            pass

    def go_forward(self):
        try:
            if self.webview.can_go_forward:
                self.webview.go_forward()
        except:
            pass

    def refresh(self):
        try:
            self.webview.reload()
        except:
            pass

    def go_home(self):
        try:
            self.webview.url = "https://www.google.com"
        except:
            pass

    def add_bookmark(self):
        if self.current_url not in self.bookmarks:
            self.bookmarks.append(self.current_url)
            self.save_bookmarks()
            self.show_message("✓ Добавлено в закладки")

    def show_message(self, text):
        popup = Popup(title="Realme Browser", content=Label(text=text), size_hint=(0.6, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def show_history(self, instance):
        if not self.history:
            self.show_message("История пуста")
            return
        text = "\n".join([f"• {u[:50]}" for u in self.history[-10:]])
        popup = Popup(title="История", content=Label(text=text), size_hint=(0.9, 0.7))
        popup.open()

    def show_bookmarks(self, instance):
        if not self.bookmarks:
            self.show_message("Нет закладок")
            return
        text = "\n".join([f"★ {u[:50]}" for u in self.bookmarks])
        popup = Popup(title="Закладки", content=Label(text=text), size_hint=(0.9, 0.7))
        popup.open()


class RealmeBrowserApp(App):
    def build(self):
        self.title = "Realme Browser"
        return RealmeBrowser()


if __name__ == '__main__':
    RealmeBrowserApp().run()