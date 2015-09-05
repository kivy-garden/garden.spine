# Spine Widget

`SpineAsset` is a Kivy widget that load and animate [Spine](http://esotericsoftware.com/) assets.

![Simple example](https://raw.githubusercontent.com/kivy-garden/garden.spine/master/screenshot.png)

Warning: this has been done during a sprint, many part are not functionnal such as:

- Only json export works
- Color per vertex
- Some models don't work (officials from the SpineTrial packages don't work, or the goblins example)

## Installation

    pip install spine-python
    garden install spine

## Usage

```python
from kivy.app import App
from kivy.garden.spine import SpineAsset

class SpineApp(App):
    def build(self):
        asset = SpineAsset(filename="data/dragon", valign="bottom")
        # print all possible animations
        print asset.animations
        asset.animate("flying")
        return asset

if __name__ == "__main__":
    SpineApp().run()
```

## Examples

See `examples` directory for an asset viewer (you can control the animation to apply, and load a different asset)

![Asset browser](https://raw.githubusercontent.com/kivy-garden/garden.spine/master/screenshot2.png)
