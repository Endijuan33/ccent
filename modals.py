from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, ListProperty

class Product(EventDispatcher):
    id = NumericProperty(0)
    name = StringProperty('')
    price = NumericProperty(0)
    stock = NumericProperty(0)
    imei = StringProperty('')

    def __init__(self, id, name, price, stock, imei='', **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.imei = imei

class CartItem(EventDispatcher):
    product = None
    quantity = NumericProperty(0)
    subtotal = NumericProperty(0)

    def __init__(self, product, quantity=1, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.quantity = quantity
        self.subtotal = product.price * quantity

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.subtotal = self.product.price * quantity
