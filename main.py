from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

from database import Database
from models import Product, CartItem
from barcode_scanner import BarcodeScanner
from utils import export_to_csv, adapt_window_size

import os
from datetime import datetime, timedelta

# Load KV string
KV = '''
#:import utils kivy.utils

<LoginScreen>:
    MDCard:
        size_hint: None, None
        size: dp(300), dp(400)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 10
        padding: dp(25)
        spacing: dp(15)
        orientation: "vertical"

        MDLabel:
            text: "Central Jati Cell"
            font_style: "H4"
            size_hint_y: None
            height: self.texture_size[1]
            halign: "center"

        MDTextField:
            id: username
            hint_text: "Username"
            icon_left: "account"
            size_hint_x: None
            width: dp(250)
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: password
            hint_text: "Password"
            icon_left: "lock"
            password: True
            size_hint_x: None
            width: dp(250)
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "LOGIN"
            size_hint_x: None
            width: dp(250)
            pos_hint: {"center_x": 0.5}
            on_release: root.try_login()

<MainScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "Central Jati Cell"
            left_action_items: [["logout", lambda x: app.logout()]]
            right_action_items: [["barcode-scan", lambda x: root.scan_barcode()], ["plus", lambda x: root.manual_input()]]

        ScrollView:
            MDList:
                id: cart_list

        MDBottomAppBar:
            MDToolbar:
                title: "Total: Rp 0"
                id: total_label
                icon: "cash"
                type: "bottom"
                left_action_items: [["checkbook", lambda x: root.checkout()]]
'''

Builder.load_string(KV)

class LoginScreen(Screen):
    def try_login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        # Untuk demo, kita gunakan login sederhana
        if username == 'admin' and password == 'admin':
            self.manager.current = 'main'
        else:
            # Tampilkan pesan error
            pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.db = Database()
        self.scanner = BarcodeScanner(self.on_barcode_scanned)

    def on_barcode_scanned(self, barcode):
        if barcode is None:
            # Jika scan gagal, atau di desktop, kita gunakan input manual
            self.manual_input()
        else:
            product = self.db.get_product_by_barcode(barcode)
            if product:
                self.show_product_dialog(product)
            else:
                # Produk tidak ditemukan, tampilkan dialog input manual dengan kode yang terisi
                self.show_manual_input_dialog(barcode)

    def scan_barcode(self):
        self.scanner.scan_barcode()

    def manual_input(self):
        self.show_manual_input_dialog()

    def show_manual_input_dialog(self, barcode=''):
        content = ManualInputDialogContent(barcode=barcode)
        self.dialog = MDDialog(
            title="Input Manual Kode Produk",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="CARI", on_release=lambda x: self.search_product(content.ids.code_input.text))
            ]
        )
        self.dialog.open()

    def search_product(self, code):
        self.dialog.dismiss()
        product = self.db.get_product_by_barcode(code)
        if product:
            self.show_product_dialog(product)
        else:
            # Tampilkan dialog error atau tambahkan produk baru
            pass

    def show_product_dialog(self, product):
        content = ProductDialogContent(product=product)
        self.dialog = MDDialog(
            title=product.name,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="TAMBAH", on_release=lambda x: self.add_to_cart(product, content.ids.quantity.text))
            ]
        )
        self.dialog.open()

    def add_to_cart(self, product, quantity_str):
        try:
            quantity = int(quantity_str)
        except:
            quantity = 1
        # Cek apakah product sudah ada di keranjang
        for item in self.cart:
            if item.product.id == product.id:
                item.quantity += quantity
                item.subtotal = item.product.price * item.quantity
                self.update_cart_display()
                self.dialog.dismiss()
                return
        # Jika belum ada, buat item baru
        cart_item = CartItem()
        cart_item.product = product
        cart_item.quantity = quantity
        cart_item.subtotal = product.price * quantity
        self.cart.append(cart_item)
        self.update_cart_display()
        self.dialog.dismiss()

    def update_cart_display(self):
        cart_list = self.ids.cart_list
        cart_list.clear_widgets()
        total = 0
        for item in self.cart:
            list_item = TwoLineListItem(
                text=item.product.name,
                secondary_text=f"Rp {item.product.price} x {item.quantity} = Rp {item.subtotal}"
            )
            cart_list.add_widget(list_item)
            total += item.subtotal
        self.ids.total_label.title = f"Total: Rp {total}"

    def checkout(self):
        if not self.cart:
            return
        total = sum(item.subtotal for item in self.cart)
        self.db.add_transaction(total, self.cart)
        # Ekspor ke CSV
        data = [['Produk', 'Harga', 'Jumlah', 'Subtotal']]
        for item in self.cart:
            data.append([item.product.name, item.product.price, item.quantity, item.subtotal])
        data.append(['Total', '', '', total])
        filename = export_to_csv(data, 'transaksi_')
        # Reset keranjang
        self.cart = []
        self.update_cart_display()
        # Tampilkan pesan sukses
        pass

class ProductDialogContent(MDBoxLayout):
    def __init__(self, product, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = dp(200)

        # Tambahkan widget untuk menampilkan detail produk dan input jumlah
        # ...

class ManualInputDialogContent(MDBoxLayout):
    def __init__(self, barcode='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = dp(100)

        self.ids.code_input.text = barcode

class POSApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        adapt_window_size()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

    def logout(self):
        self.root.current = 'login'

if __name__ == '__main__':
    POSApp().run()
