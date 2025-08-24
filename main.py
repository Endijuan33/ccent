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
from kivy.utils import platform

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path

from database import Database
from models import Product, CartItem
from barcode_scanner import BarcodeScanner
from utils import export_to_csv, adapt_window_size

import os
from datetime import datetime

# Load KV files
Builder.load_string('''
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
            text: "POS Toko HP"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            padding_y: dp(15)

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
            icon_left: "key"
            password: True
            size_hint_x: None
            width: dp(250)
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "LOGIN"
            pos_hint: {"center_x": 0.5}
            size_hint_x: None
            width: dp(250)
            on_release: root.try_login()

<MainScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "POS Toko HP"
            left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
            right_action_items: [["logout", lambda x: root.logout()]]
            elevation: 10

        MDNavigationLayout:
            ScreenManager:
                id: screen_manager

                Screen:
                    name: "home"
                    MDLabel:
                        text: "Selamat Datang di Aplikasi POS Toko HP"
                        halign: "center"

                Screen:
                    name: "products"
                    BoxLayout:
                        orientation: "vertical"
                        MDBoxLayout:
                            adaptive_height: True
                            padding: dp(10)
                            spacing: dp(10)
                            MDRaisedButton:
                                text: "Tambah Produk"
                                on_release: app.show_product_dialog()
                            MDRaisedButton:
                                text: "Refresh"
                                on_release: root.load_products()

                        ScrollView:
                            MDList:
                                id: product_list

                Screen:
                    name: "pos"
                    BoxLayout:
                        orientation: "vertical"
                        MDBoxLayout:
                            adaptive_height: True
                            padding: dp(10)
                            spacing: dp(10)
                            MDRaisedButton:
                                text: "Scan Barcode"
                                on_release: root.start_barcode_scan()
                            MDRaisedButton:
                                text: "Input Manual"
                                on_release: root.show_manual_input()

                        ScrollView:
                            MDList:
                                id: cart_list

                        MDBoxLayout:
                            adaptive_height: True
                            padding: dp(10)
                            MDLabel:
                                text: "Total: Rp 0"
                                id: total_label
                                bold: True
                            MDRaisedButton:
                                text: "Proses Transaksi"
                                on_release: root.process_transaction()

                Screen:
                    name: "reports"
                    BoxLayout:
                        orientation: "vertical"
                        MDBoxLayout:
                            adaptive_height: True
                            padding: dp(10)
                            spacing: dp(10)
                            MDRaisedButton:
                                text: "Harian"
                                on_release: root.load_reports('daily')
                            MDRaisedButton:
                                text: "Mingguan"
                                on_release: root.load_reports('weekly')
                            MDRaisedButton:
                                text: "Bulanan"
                                on_release: root.load_reports('monthly')
                            MDRaisedButton:
                                text: "Export CSV"
                                on_release: root.export_reports()

                        ScrollView:
                            MDList:
                                id: report_list

            MDNavigationDrawer:
                id: nav_drawer
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "8dp"
                    padding: "8dp"
                    Image:
                        size_hint_y: None
                        height: dp(150)
                        source: "assets/logo.png"
                    MDLabel:
                        text: "Menu Navigasi"
                        size_hint_y: None
                        height: self.texture_size[1]
                        font_style: "H6"
                    MDList:
                        OneLineListItem:
                            text: "Beranda"
                            on_release: root.switch_screen("home")
                        OneLineListItem:
                            text: "Produk"
                            on_release: root.switch_screen("products")
                        OneLineListItem:
                            text: "Point of Sale"
                            on_release: root.switch_screen("pos")
                        OneLineListItem:
                            text: "Laporan"
                            on_release: root.switch_screen("reports")

        MDBottomNavigation:
            panel_color: utils.get_color_from_hex("#1976d2")
            text_color_active: 1, 1, 1, 1

            MDBottomNavigationItem:
                name: "home"
                text: "Home"
                icon: "home"
                on_tab_press: root.switch_screen("home")

            MDBottomNavigationItem:
                name: "products"
                text: "Produk"
                icon: "package-variant"
                on_tab_press: root.switch_screen("products")

            MDBottomNavigationItem:
                name: "pos"
                text: "POS"
                icon: "point-of-sale"
                on_tab_press: root.switch_screen("pos")

            MDBottomNavigationItem:
                name: "reports"
                text: "Laporan"
                icon: "chart-bar"
                on_tab_press: root.switch_screen("reports")
''')

class LoginScreen(Screen):
    def try_login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        db = Database()
        user = db.get_user(username, password)

        if user:
            self.manager.current_user = user
            self.manager.current = 'main'
        else:
            self.show_error_dialog("Login gagal. Periksa username dan password.")

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.db = Database()
        self.scanner = BarcodeScanner()

    def on_enter(self):
        self.load_products()

    def switch_screen(self, screen_name):
        self.ids.screen_manager.current = screen_name
        if screen_name == "products":
            self.load_products()
        elif screen_name == "reports":
            self.load_reports('daily')

    def load_products(self):
        product_list = self.ids.product_list
        product_list.clear_widgets()

        products = self.db.get_products()
        for product in products:
            item = TwoLineListItem(
                text=f"{product[1]} - Rp {product[2]:,}",
                secondary_text=f"Stok: {product[3]} | IMEI: {product[4] if product[4] else 'N/A'}"
            )
            item.bind(on_release=lambda x, p=product: self.edit_product(p))
            product_list.add_widget(item)

    def show_product_dialog(self, product=None):
        title = "Edit Produk" if product else "Tambah Produk"
        self.dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=ProductDialogContent(product=product),
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SIMPAN", on_release=lambda x: self.save_product(product))
            ]
        )
        self.dialog.open()

    def save_product(self, existing_product=None):
        content = self.dialog.content_cls
        name = content.ids.name_field.text
        price = float(content.ids.price_field.text)
        stock = int(content.ids.stock_field.text)
        imei = content.ids.imei_field.text or None

        if existing_product:
            self.db.update_product(existing_product[0], name, price, stock, imei)
        else:
            self.db.add_product(name, price, stock, imei)

        self.dialog.dismiss()
        self.load_products()

    def edit_product(self, product):
        self.show_product_dialog(product)

    def start_barcode_scan(self):
        if not self.scanner.camera:
            camera_widget = self.scanner.init_camera()
            if camera_widget:
                # Add camera to layout temporarily
                pass

        self.scanner.start_scan(self.on_barcode_scanned)

    def on_barcode_scanned(self, barcode_data):
        product = self.db.get_product_by_imei(barcode_data)
        if product:
            self.add_to_cart(product)
        else:
            self.show_error_dialog("Produk tidak ditemukan untuk IMEI ini.")

    def show_manual_input(self):
        self.dialog = MDDialog(
            title="Input Manual IMEI",
            type="custom",
            content_cls=ManualInputDialogContent(),
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="CARI", on_release=lambda x: self.search_by_imei())
            ]
        )
        self.dialog.open()

    def search_by_imei(self):
        content = self.dialog.content_cls
        imei = content.ids.imei_field.text

        product = self.db.get_product_by_imei(imei)
        if product:
            self.add_to_cart(product)
        else:
            self.show_error_dialog("Produk tidak ditemukan untuk IMEI ini.")

        self.dialog.dismiss()

    def add_to_cart(self, product):
        # Check if product already in cart
        for item in self.cart:
            if item.product[0] == product[0]:
                item.quantity += 1
                item.subtotal = item.product[2] * item.quantity
                self.update_cart_display()
                return

        # Add new item to cart
        cart_item = CartItem(product)
        self.cart.append(cart_item)
        self.update_cart_display()

    def update_cart_display(self):
        cart_list = self.ids.cart_list
        total_label = self.ids.total_label

        cart_list.clear_widgets()
        total = 0

        for item in self.cart:
            list_item = TwoLineListItem(
                text=f"{item.product[1]} x {item.quantity}",
                secondary_text=f"Rp {item.subtotal:,}"
            )
            cart_list.add_widget(list_item)
            total += item.subtotal

        total_label.text = f"Total: Rp {total:,}"

    def process_transaction(self):
        if not self.cart:
            self.show_error_dialog("Keranjang kosong. Tambahkan produk terlebih dahulu.")
            return

        user_id = self.manager.current_user[0]
        items = [{
            'product_id': item.product[0],
            'quantity': item.quantity,
            'subtotal': item.subtotal
        } for item in self.cart]

        transaction_id = self.db.add_transaction(user_id, items)

        # Show success message
        self.show_success_dialog(f"Transaksi berhasil! ID: {transaction_id}")

        # Clear cart
        self.cart = []
        self.update_cart_display()

    def load_reports(self, period):
        report_list = self.ids.report_list
        report_list.clear_widgets()

        transactions = self.db.get_transactions(period)
        for transaction in transactions:
            item = TwoLineListItem(
                text=f"T#{transaction[0]} - {transaction[1]}",
                secondary_text=f"Rp {transaction[2]:,} - oleh {transaction[3]}"
            )
            item.bind(on_release=lambda x, t=transaction: self.show_transaction_details(t[0]))
            report_list.add_widget(item)

    def show_transaction_details(self, transaction_id):
        details = self.db.get_transaction_details(transaction_id)

        detail_text = "\n".join([f"{item[0]} x{item[1]} = Rp {item[2]:,}" for item in details])

        dialog = MDDialog(
            title=f"Detail Transaksi #{transaction_id}",
            text=detail_text,
            buttons=[MDFlatButton(text="TUTUP", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def export_reports(self):
        transactions = self.db.get_transactions('daily')
        data = [["ID", "Tanggal", "Total", "Kasir"]]

        for transaction in transactions:
            data.append([transaction[0], transaction[1], transaction[2], transaction[3]])

        filename = export_to_csv(data, "laporan_penjualan")
        self.show_success_dialog(f"Laporan berhasil diexport ke {filename}")

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def show_success_dialog(self, message):
        dialog = MDDialog(
            title="Sukses",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def logout(self):
        self.manager.current = 'login'
        self.manager.current_user = None

class ProductDialogContent(MDBoxLayout):
    def __init__(self, product=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = dp(200)

        self.ids.name_field = MDTextField(
            hint_text="Nama Produk",
            text=product[1] if product else ""
        )
        self.add_widget(self.ids.name_field)

        self.ids.price_field = MDTextField(
            hint_text="Harga",
            text=str(product[2]) if product else ""
        )
        self.add_widget(self.ids.price_field)

        self.ids.stock_field = MDTextField(
            hint_text="Stok",
            text=str(product[3]) if product else ""
        )
        self.add_widget(self.ids.stock_field)

        self.ids.imei_field = MDTextField(
            hint_text="IMEI (opsional)",
            text=product[4] if product and product[4] else ""
        )
        self.add_widget(self.ids.imei_field)

class ManualInputDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = dp(100)

        self.ids.imei_field = MDTextField(
            hint_text="Masukkan IMEI"
        )
        self.add_widget(self.ids.imei_field)

class POSApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Request Android permissions
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

        adapt_window_size()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.current_user = None

        return sm

if __name__ == '__main__':
    POSApp().run()
