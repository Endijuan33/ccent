import csv
from datetime import datetime
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

def register_fonts():
    try:
        LabelBase.register(name='Roboto', 
                          fn_regular='assets/fonts/Roboto-Regular.ttf', 
                          fn_bold='assets/fonts/Roboto-Bold.ttf')
    except:
        # Fallback to default fonts if custom fonts aren't available
        pass

def export_to_csv(data, filename_prefix):
    filename = f"{filename_prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        return filename
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def adapt_window_size():
    if platform == 'android':
        # Fullscreen on Android
        Window.size = (360, 640)
    else:
        # Default size for desktop testing
        Window.size = (360, 640)
