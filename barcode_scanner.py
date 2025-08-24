try:
    from kivy.graphics.texture import Texture
    from kivy.uix.camera import Camera
    from kivy.uix.image import Image
    from pyzbar.pyzbar import decode
    from PIL import Image as PILImage
    import numpy as np
except ImportError:
    # Fallback for environments without camera support
    pass

class BarcodeScanner:
    def __init__(self):
        self.camera = None
        self.is_scanning = False
        self.callback = None

    def init_camera(self):
        try:
            self.camera = Camera(resolution=(640, 480), play=True)
            self.camera.bind(texture=self.on_camera_texture)
            return self.camera
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return None

    def on_camera_texture(self, instance, value):
        if self.is_scanning and value and self.callback:
            self.scan_barcode(value)

    def scan_barcode(self, texture):
        try:
            # Convert texture to numpy array
            buffer = texture.pixels
            size = texture.size
            fmt = texture.colorfmt

            # Convert to PIL Image
            pil_image = PILImage.frombytes(fmt, size, buffer, 'raw', fmt, 0, 1)

            # Convert to grayscale
            gray_image = pil_image.convert('L')

            # Decode barcodes
            barcodes = decode(gray_image)

            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                self.is_scanning = False
                if self.callback:
                    self.callback(barcode_data)
        except Exception as e:
            print(f"Barcode scanning error: {e}")

    def start_scan(self, callback):
        self.callback = callback
        self.is_scanning = True

    def stop_scan(self):
        self.is_scanning = False
        if self.camera:
            self.camera.play = False
