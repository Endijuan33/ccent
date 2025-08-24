from kivy import platform
from kivy.clock import Clock
from jnius import autoclass, cast
from android import activity
from android.runnable import run_on_ui_thread

if platform == 'android':
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    Toast = autoclass('android.widget.Toast')
else:
    # Untuk desktop, kita tidak menggunakan intent
    pass

class BarcodeScanner:
    def __init__(self, on_barcode_scanned):
        self.on_barcode_scanned = on_barcode_scanned
        self.scan_result = None

    def scan_barcode(self):
        if platform == 'android':
            self._scan_android()
        else:
            # Di desktop, kita tidak memindai, tetapi memunculkan input manual
            # Kita akan kembalikan None dan handle di main.py untuk input manual
            self.on_barcode_scanned(None)

    def _scan_android(self):
        # Menggunakan intent untuk memindai barcode
        intent = Intent('com.google.zxing.client.android.SCAN')
        intent.putExtra('PROMPT_MESSAGE', 'Arahkan kamera ke barcode')
        intent.putExtra('SCAN_MODE', 'PRODUCT_MODE')
        activity = PythonActivity.mActivity
        activity.startActivityForResult(intent, 0)
        activity.bind(on_activity_result=self._on_activity_result)

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code == 0:
            if result_code == -1:  # RESULT_OK
                contents = intent.getStringExtra('SCAN_RESULT')
                self.on_barcode_scanned(contents)
            else:
                self.on_barcode_scanned(None)
