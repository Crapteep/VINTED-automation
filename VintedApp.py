from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

class MainWindow(Screen):
    pass

class LogingWindow(Screen):
    pass

class AddAccountWindow(Screen):
    pass

class SettingsWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass


kv = Builder.load_file('properties.kv')


class AwesomeApp(App):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        return kv

if __name__ == '__main__':
    AwesomeApp().run()