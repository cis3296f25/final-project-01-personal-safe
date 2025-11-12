from kivy.graphics.texture import Texture


class Theme:
    def __init__(self):
        # top -> bottom RGBA colors
        self.color_top = (58 / 255, 9 / 255, 85 / 255, 1)  # deep navy
        self.color_bottom = (185 / 255, 58 / 255, 255 / 255, 0.8)  # lighter blue
        self.gradient_texture = self._build_vertical_gradient(
            self.color_top, self.color_bottom, steps=128
        )
        # Backwards-compatible alias for KV usage
        self.background_texture = self.gradient_texture

    def _build_vertical_gradient(self, top, bottom, steps=64):
        """
        Create a 1 x steps texture and let Kivy stretch it.
        """
        tex = Texture.create(size=(1, steps), colorfmt="rgba")
        tex.mag_filter = "linear"
        tex.min_filter = "linear"
        buf = bytearray()
        for i in range(steps):
            t = i / float(steps - 1)
            r = top[0] + (bottom[0] - top[0]) * t
            g = top[1] + (bottom[1] - top[1]) * t
            b = top[2] + (bottom[2] - top[2]) * t
            a = top[3] + (bottom[3] - top[3]) * t
            buf += bytes([int(r * 255), int(g * 255), int(b * 255), int(a * 255)])
        tex.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
        return tex
