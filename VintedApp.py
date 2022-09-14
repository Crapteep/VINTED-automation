from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('properties.kv')

class MyLayout(Widget):
    pass 
    # name = ObjectProperty(None)
    # pizza = ObjectProperty(None)
    # color = ObjectProperty(None)

    
    # def press(self):
    #     name = self.name.text
    #     pizza = self.pizza.text
    #     color = self.color.text
    #     #print( f'Hello {name}, you like {pizza} pizza, and your favourite color is {color}.')
    #     # print it to the screen
    #     self.add_widget(Label(text= f'Hello {name}, you like {pizza} pizza, and your favourite color is {color}.' ))

    #     #clear the input boxes
    #     self.name.text = ""
    #     self.pizza.text = ""
    #     self.color.text = ""

class VintedApp(App):
    def build(self):
        return MyLayout()


if __name__ == '__main__':
    VintedApp().run()