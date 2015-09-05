# coding=utf-8

from kivy.garden.spine import SpineAsset
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

kv = """
BoxLayout:
    orientation: "vertical"
    BoxLayout:
        size_hint_y: None
        height: "48dp"
        CheckBox:
            id: debug
        Spinner:
            id: assets
            size_hint_y: None
            height: "48dp"
            text: "data/dragon"
            values: ("data/dragon", "data/spineboy", "data/goblins", "data/alien/alien", "data/spinosaurus", "data/powerup")
            on_text: dragon.filename = self.text
        Spinner:
            id: valign
            size_hint_y: None
            height: "48dp"
            text: "middle"
            values: ("middle", "bottom")
            on_text: dragon.valign = self.text

    SpineAsset:
        id: dragon
        filename: "data/dragon"
        debug: debug.active

    Spinner:
        size_hint_y: None
        height: "48dp"
        text: (dragon.animations or ["-"])[0]
        values: dragon.animations
        on_text: dragon.animate(self.text)

"""

class SpineApp(App):
    def build(self):
        from kivy.lang import Builder
        return Builder.load_string(kv)


if __name__ == "__main__":
    SpineApp().run()
