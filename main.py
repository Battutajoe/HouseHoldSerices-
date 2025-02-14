from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout 
from requests import post, get
import jwt
from jwt import decode
import json
from kivy.uix.popup import Popup
from functools import partial
from kivy.network.urlrequest import UrlRequest  # For non-blocking HTTP requests
from kivy.clock import Clock
import requests
from functools import partial
# Define screens for different services

class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.token = None  # Attribute to hold the JWT token
        self.role = None  # Attribute to hold the user role

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super(RegistrationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.username_input = TextInput(hint_text="Username", size_hint=(1, None), height=40)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint=(1, None), height=40)
        self.role_input = TextInput(hint_text="Role (optional, default user)", size_hint=(1, None), height=40)

        self.register_button = Button(text="Register", size_hint=(1, None), height=40)
        self.register_button.bind(on_press=self.register_user)

        self.message_label = Label(text="Enter details to register", size_hint=(1, None), height=40)

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.role_input)
        layout.add_widget(self.register_button)
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def register_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        role = self.role_input.text or 'user'

        if not username or not password:
            self.message_label.text = "Username and Password are required."
            return

        data = {
            'username': username,
            'password': password,
            'role': role
        }

        self.message_label.text = "Registering..."
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post('http://127.0.0.1:5000/register', json=data, headers=headers)
            if response.status_code == 201:
                result = response.json()
                self.manager.token = result.get('token')
                self.message_label.text = "Registration successful!"
                self.manager.current = 'home'
            else:
                self.message_label.text = f"Registration failed: {response.status_code} {response.text}"
        except Exception as e:
            self.message_label.text = f"An error occurred: {str(e)}"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.username_input = TextInput(hint_text="Username", size_hint=(1, None), height=40)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint=(1, None), height=40)

        self.login_button = Button(text="Login", size_hint=(1, None), height=40)
        self.login_button.bind(on_press=self.login_user)

        self.register_button = Button(text="Register", size_hint=(1, None), height=40)
        self.register_button.bind(on_press=self.go_to_register)

        self.message_label = Label(text="Enter your credentials to login", size_hint=(1, None), height=40)

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.login_button)
        layout.add_widget(self.register_button)
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def login_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if not username or not password:
            self.message_label.text = "Username and Password are required."
            return

        data = {
            'username': username,
            'password': password
        }

        self.message_label.text = "Logging in..."
        try:
            response = requests.post('http://127.0.0.1:5000/login', json=data)
            if response.status_code == 200:
                result = response.json()
                self.manager.token = result.get('token')
                if self.manager.token:
                    decoded = jwt.decode(self.manager.token, options={"verify_signature": False})
                    self.manager.role = decoded.get('role')
                    self.message_label.text = "Login successful!"
                    if self.manager.role == 'admin':
                        self.manager.current = 'admin_dashboard'
                    else:
                        self.manager.current = 'user_dashboard'
                else:
                    self.message_label.text = "No token received from server."
            else:
                self.message_label.text = f"Login failed: {response.status_code} {response.text}"
        except Exception as e:
            self.message_label.text = f"An error occurred: {str(e)}"

    def go_to_register(self, instance):
        self.manager.current = 'register'



class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.message_label = Label(text="Welcome to the dashboard", size_hint=(1, None), height=40)
        self.logout_button = Button(text="Logout", size_hint=(1, None), height=40)
        self.logout_button.bind(on_press=self.logout_user)

        layout.add_widget(self.message_label)
        layout.add_widget(self.logout_button)

        # Fetch services button
        fetch_services_button = Button(text="Fetch Services", size_hint=(1, 0.1))
        fetch_services_button.bind(on_press=self.fetch_services)
        layout.add_widget(fetch_services_button)

        # Scrollable services list
        self.services_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.services_list.bind(minimum_height=self.services_list.setter('height'))
        scrollview_services = ScrollView()
        scrollview_services.add_widget(self.services_list)
        layout.add_widget(scrollview_services)

        # Fetch orders button
        fetch_orders_button = Button(text="Fetch Your Orders", size_hint=(1, 0.1))
        fetch_orders_button.bind(on_press=self.fetch_orders)
        layout.add_widget(fetch_orders_button)

        # Scrollable orders list
        self.orders_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.orders_list.bind(minimum_height=self.orders_list.setter('height'))
        scrollview_orders = ScrollView()
        scrollview_orders.add_widget(self.orders_list)
        layout.add_widget(scrollview_orders)

        self.add_widget(layout)

    def on_enter(self):
        # Fetch protected data when entering the dashboard screen
        self.fetch_services(None)
        self.fetch_orders(None)

    def fetch_services(self, instance):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        print(f"Token being sent: {self.manager.token}")  # Debugging line
        try:
            response = requests.get("http://127.0.0.1:5000/api/services", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                try:
                    services = response.json()
                    self.services_list.clear_widgets()
                    if not services:
                        self.display_message(self.services_list, "No services available.")
                        return
                    for category, service_list in services.items():
                        for service in service_list:
                            self.add_service_to_list(service['name'], service['price'])
                except ValueError as e:
                    self.display_message(self.services_list, f"Failed to parse JSON: {str(e)}")
            else:
                self.display_message(self.services_list, f"Failed to fetch services: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(self.services_list, f"Error fetching services: {e}")

    def add_service_to_list(self, service_name, price):
        service_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        service_box.add_widget(Label(text=f"Service: {service_name}"))
        service_box.add_widget(Label(text=f"Price: {price}"))
        order_button = Button(text="Order")
        order_button.bind(on_press=lambda x: self.place_order(service_name))
        service_box.add_widget(order_button)
        self.services_list.add_widget(service_box)

    def place_order(self, service_name):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        data = {"service_id": service_name}  # Assuming service_name is the ID, adjust if necessary
        try:
            response = requests.post("http://127.0.0.1:5000/api/orders", json=data, headers=headers)
            if response.status_code == 201:
                print(f"Order placed for service {service_name}")
                self.fetch_orders(None)  # Refresh orders list
            else:
                print(f"Failed to place order: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error placing order: {e}")

    def fetch_orders(self, instance):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        try:
            response = requests.get("http://127.0.0.1:5000/api/orders/my", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                try:
                    orders = response.json()
                    self.orders_list.clear_widgets()
                    if not orders:
                        self.display_message(self.orders_list, "You have no orders placed yet.")
                        return
                    for order in orders:
                        self.add_order_to_list(order)
                except ValueError as e:
                    self.display_message(self.orders_list, f"Failed to parse JSON: {str(e)}")
            else:
                self.display_message(self.orders_list, f"Failed to fetch orders: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(self.orders_list, f"Error fetching orders: {e}")

    def add_order_to_list(self, order):
        order_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        order_box.add_widget(Label(text=f"Order ID: {order['order_id']}"))
        order_box.add_widget(Label(text=f"Service ID: {order['service_id']}"))
        order_box.add_widget(Label(text=f"Quantity: {order['quantity']}"))
        order_box.add_widget(Label(text=f"Total Price: {order['total_price']}"))
        order_box.add_widget(Label(text=f"Status: {order['status']}"))
        self.orders_list.add_widget(order_box)

    def logout_user(self, instance):
        self.manager.token = None
        self.manager.current = 'login'  # Navigate back to the login screen

    def display_message(self, widget, message):
        widget.clear_widgets()
        widget.add_widget(Label(text=message))

class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        super(AdminDashboard, self).__init__(**kwargs)
        self.token = None  # Will be set after login

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Fetch orders button
        fetch_button = Button(text="Fetch Orders", size_hint=(1, 0.1))
        fetch_button.bind(on_press=self.fetch_orders)
        layout.add_widget(fetch_button)

        # Scrollable order list
        self.orders_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.orders_list.bind(minimum_height=self.orders_list.setter('height'))
        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.add_widget(self.orders_list)
        layout.add_widget(scrollview)

        self.add_widget(layout)

    def fetch_orders(self, instance):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get("http://127.0.0.1:5000/api/orders", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                try:
                    orders = response.json()
                    self.display_orders(orders)
                except ValueError as e:
                    self.display_message(f"Failed to parse JSON: {str(e)}")
            else:
                self.display_message(f"Failed to fetch orders: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(f"An error occurred: {str(e)}")

    def display_orders(self, orders):
        self.orders_list.clear_widgets()
        for order in orders:
            order_info = f"Order ID: {order['order_id']}, User ID: {order['user_id']}, Service ID: {order['service_id']}, Quantity: {order['quantity']}, Location: {order['location']}, Total Price: {order['total_price']}, Status: {order['status']}, Created At: {order['created_at']}"
            order_label = Label(text=order_info, size_hint=(1, None), height=40)
            confirm_button = Button(text="Confirm Order", size_hint=(1, None), height=40)
            confirm_button.bind(on_press=lambda instance, order_id=order['order_id']: self.confirm_order(order_id))
            self.orders_list.add_widget(order_label)
            self.orders_list.add_widget(confirm_button)

    def confirm_order(self, order_id):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.post(f"http://127.0.0.1:5000/api/orders/{order_id}/confirm", headers=headers)
            if response.status_code == 200:
                self.display_message(f"Order {order_id} confirmed successfully.")
                self.fetch_orders(None)  # Refresh the orders list
            else:
                self.display_message(f"Failed to confirm order {order_id}: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(f"An error occurred: {str(e)}")

    def display_message(self, message):
        self.orders_list.clear_widgets()
        self.orders_list.add_widget(Label(text=message, size_hint=(1, None), height=40))



class UserDashboard(Screen):
    def __init__(self, **kwargs):
        super(UserDashboard, self).__init__(**kwargs)
        self.token = None  # Will be set after login

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Fetch services button
        fetch_services_button = Button(text="Fetch Services", size_hint=(1, 0.1))
        fetch_services_button.bind(on_press=self.fetch_services)
        layout.add_widget(fetch_services_button)

        # Scrollable services list
        self.services_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.services_list.bind(minimum_height=self.services_list.setter('height'))
        scrollview_services = ScrollView()
        scrollview_services.add_widget(self.services_list)
        layout.add_widget(scrollview_services)

        # Fetch orders button
        fetch_orders_button = Button(text="Fetch Your Orders", size_hint=(1, 0.1))
        fetch_orders_button.bind(on_press=self.fetch_orders)
        layout.add_widget(fetch_orders_button)

        # Scrollable orders list
        self.orders_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.orders_list.bind(minimum_height=self.orders_list.setter('height'))
        scrollview_orders = ScrollView()
        scrollview_orders.add_widget(self.orders_list)
        layout.add_widget(scrollview_orders)

        self.add_widget(layout)

    def fetch_services(self, instance):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        try:
            response = requests.get("http://127.0.0.1:5000/api/services", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                try:
                    services = response.json()
                    self.services_list.clear_widgets()
                    if not services:
                        self.display_message(self.services_list, "No services available.")
                        return
                    for category, service_list in services.items():
                        for service in service_list:
                            self.add_service_to_list(service['name'], service['price'])
                except ValueError as e:
                    self.display_message(self.services_list, f"Failed to parse JSON: {str(e)}")
            else:
                self.display_message(self.services_list, f"Failed to fetch services: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(self.services_list, f"Error fetching services: {e}")

    def add_service_to_list(self, service_name, price):
        service_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        service_box.add_widget(Label(text=f"Service: {service_name}"))
        service_box.add_widget(Label(text=f"Price: {price}"))
        order_button = Button(text="Order")
        order_button.bind(on_press=lambda x: self.place_order(service_name))
        service_box.add_widget(order_button)
        self.services_list.add_widget(service_box)

    def place_order(self, service_id):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        try:
            response = requests.post("http://127.0.0.1:5000/api/orders", json={"service_id": service_id}, headers=headers)
            if response.status_code == 201:
                print(f"Order placed for service {service_id}")
                self.fetch_orders(None)  # Refresh orders list
            else:
                print(f"Failed to place order: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error placing order: {e}")

    def fetch_orders(self, instance):
        headers = {"Authorization": f"Bearer {self.manager.token}"}
        try:
            response = requests.get("http://127.0.0.1:5000/api/orders/my", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                try:
                    orders = response.json()
                    self.orders_list.clear_widgets()
                    if not orders:
                        self.display_message(self.orders_list, "You have no orders placed yet.")
                        return
                    for order in orders:
                        self.add_order_to_list(order)
                except ValueError as e:
                    self.display_message(self.orders_list, f"Failed to parse JSON: {str(e)}")
            else:
                self.display_message(self.orders_list, f"Failed to fetch orders: {response.status_code} {response.text}")
        except Exception as e:
            self.display_message(self.orders_list, f"Error fetching orders: {e}")

    def add_order_to_list(self, order):
        order_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        order_box.add_widget(Label(text=f"Order ID: {order.get('order_id', 'N/A')}"))
        order_box.add_widget(Label(text=f"Service: {order.get('service_id', 'N/A')}"))
        order_box.add_widget(Label(text=f"Status: {order.get('status', 'N/A')}"))
        self.orders_list.add_widget(order_box)

    @staticmethod
    def display_message(target_list, message):
        target_list.clear_widgets()
        target_list.add_widget(Label(text=message))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Buttons for each service category
        layout.add_widget(Button(text="Cleaning Services", on_press=self.go_to_cleaning))
        layout.add_widget(Button(text="Food Delivery", on_press=self.go_to_food))
        layout.add_widget(Button(text="Groceries Delivery", on_press=self.go_to_groceries))
        layout.add_widget(Button(text="Fruit Delivery", on_press=self.go_to_fruit))
        layout.add_widget(Button(text="Gardening Services", on_press=self.go_to_gardening))

        self.add_widget(layout)

    def go_to_cleaning(self, instance):
        self.manager.current = 'cleaning'

    def go_to_food(self, instance):
        self.manager.current = 'food'

    def go_to_groceries(self, instance):
        self.manager.current = 'groceries'

    def go_to_fruit(self, instance):
        self.manager.current = 'fruit'

    def go_to_gardening(self, instance):
        self.manager.current = 'gardening'


class CleaningScreen(Screen):
    def __init__(self, **kwargs):
        super(CleaningScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Prices in Kenyan Shillings for cleaning services
        self.prices = {
            'House Cleaning': 3500,
            'Couch Cleaning': 2500,
            'Toilet Cleaning': 3000,
            'Car Cleaning': 1200,
            'Laundry': 2000,
            'Dry Cleaning': 1500
        }

        # Feedback label for order submission status
        self.feedback_label = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.feedback_label)

        # Cleaning service selection dropdown (Spinner)
        layout.add_widget(Label(text="Choose cleaning service:"))
        self.service_spinner = Spinner(
            text='Select Cleaning Service',
            values=tuple(self.prices.keys()),
            size_hint=(None, None),
            size=(200, 44),
            on_text=self.update_price
        )
        layout.add_widget(self.service_spinner)

        # Display price label
        self.price_label = Label(text="Price: KES 0")
        layout.add_widget(self.price_label)

        # Delivery location input
        layout.add_widget(Label(text="Enter delivery location:"))
        self.location_input = TextInput(hint_text="Delivery Location", multiline=False)
        layout.add_widget(self.location_input)

        # Quantity input (optional for this service, but you can add based on needs)
        layout.add_widget(Label(text="Enter quantity (if applicable):"))
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')
        layout.add_widget(self.quantity_input)

        # Submit order button
        submit_button = Button(
            text="Place Order",
            background_color=(0.2, 0.6, 0.2, 1),  # Green button
            color=(1, 1, 1, 1),  # White text
            font_size=18,
            on_press=self.submit_order
        )
        layout.add_widget(submit_button)

        # Back button to return to home screen
        back_button = Button(
            text="Back to Home",
            background_color=(0.6, 0.2, 0.2, 1),  # Red button
            color=(1, 1, 1, 1),  # White text
            font_size=18,
            on_press=self.go_back_home
        )
        layout.add_widget(back_button)

        # Feedback label for status updates
        self.feedback_label = Label(text="")
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def on_enter(self):
        self.fetch_services()

    def update_price(self, spinner, text):
        """Update price label based on selected service."""
        if text in self.prices:
            price = self.prices[text]
            self.price_label.text = f"Price: KES {price}"

    def fetch_services(self):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get('http://127.0.0.1:5000/api/services/cleaning', headers=headers)
            if response.status_code == 200:
                self.prices = response.json()
                self.service_spinner.values = list(self.prices.keys())
            else:
                self.feedback_label.text = "Failed to fetch services."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def submit_order(self, instance):
        cleaning_service = self.service_spinner.text
        location = self.location_input.text
        quantity = int(self.quantity_input.text) if self.quantity_input.text.isdigit() else 1

        if cleaning_service == "Select Cleaning Service":
            self.feedback_label.text = "Please select a cleaning service."
        elif not location:
            self.feedback_label.text = "Please enter the delivery location."
        else:
            price = self.prices[cleaning_service]
            total_price = price * quantity
            order_data = {
                'service': cleaning_service,
                'price': price,
                'location': location,
                'total_price': total_price,
                'quantity': quantity
            }

            headers = {'Authorization': f'Bearer {self.manager.token}'}
            try:
                response = requests.post('http://127.0.0.1:5000/api/orders', json=order_data, headers=headers)
                if response.status_code == 201:
                    self.feedback_label.color = (0, 1, 0, 1)  # Green for success
                    self.feedback_label.text = "Order placed successfully!"
                else:
                    self.feedback_label.text = "Failed to place order."
            except Exception as e:
                self.feedback_label.text = f"Error: {str(e)}"

    def go_back_home(self, instance):
        self.manager.current = 'home'


class FoodScreen(Screen):
    def __init__(self, **kwargs):
        super(FoodScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Prices for food items
        self.prices = {
            'Fries': 170,
            'KFC': 230,
            'Smokies': 50,
            'Hotdog': 300,
            'Sausages': 50,
            'Bread': 65,
            'Cakes': 1500,
            'Meat': 600,
            'Fish': 750,
            'Chicken': 700,
            'Blended Juice': 250
        }

        # Service selection dropdown
        layout.add_widget(Label(text="Choose food item:"))
        self.service_spinner = Spinner(
            text='Select Food Item',
            values=tuple(self.prices.keys()),
            size_hint=(None, None),
            size=(200, 44),
            on_text=self.update_price
        )
        layout.add_widget(self.service_spinner)

        # Display price label
        self.price_label = Label(text="Price: KES 0")
        layout.add_widget(self.price_label)

        # Quantity input
        layout.add_widget(Label(text="Enter quantity:"))
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')
        layout.add_widget(self.quantity_input)

        # Delivery location input
        layout.add_widget(Label(text="Enter delivery location:"))
        self.location_input = TextInput(hint_text="Delivery Location", multiline=False)
        layout.add_widget(self.location_input)

        # Submit order button
        submit_button = Button(text="Place Order", on_press=self.submit_order)
        layout.add_widget(submit_button)

        # Back button to home screen
        back_button = Button(text="Back to Home", on_press=self.go_back_home)
        layout.add_widget(back_button)

        # Feedback label for status updates
        self.feedback_label = Label(text="")
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def on_enter(self):
        self.fetch_services()

    def update_price(self, spinner, text):
        """Update price label based on selected service."""
        if text in self.prices:
            price = self.prices[text]
            self.price_label.text = f"Price: KES {price}"

    def fetch_services(self):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get('http://127.0.0.1:5000/api/services/food', headers=headers)
            if response.status_code == 200:
                self.prices = response.json()
                self.service_spinner.values = list(self.prices.keys())
            else:
                self.feedback_label.text = "Failed to fetch services."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def submit_order(self, instance):
        food_service = self.service_spinner.text
        location = self.location_input.text
        quantity = int(self.quantity_input.text) if self.quantity_input.text.isdigit() else 1

        if food_service == "Select Food Item" or not location:
            self.feedback_label.text = "Please complete all fields."
            return

        price = self.prices[food_service]
        total_price = price * quantity
        order_data = {
            'service': food_service,
            'price': price,
            'total_price': total_price,
            'location': location,
            'quantity': quantity
        }

        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.post('http://127.0.0.1:5000/api/orders', json=order_data, headers=headers)
            if response.status_code == 201:
                self.feedback_label.text = "Order placed successfully!"
            else:
                self.feedback_label.text = "Failed to place order."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def go_back_home(self, instance):
        self.manager.current = 'home'


class GroceriesScreen(Screen):
    def __init__(self, **kwargs):
        super(GroceriesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Prices for groceries items
        self.prices = {
            'Onions': 50,
            'Tomato': 50,
            'Pepper': 50,
            'Kales': 50,
            'Cabbages': 50,
            'Green Pepper': 50,
            'Coriander': 50
        }

        # Service selection dropdown
        layout.add_widget(Label(text="Choose grocery item:"))
        self.service_spinner = Spinner(
            text='Select Grocery Item',
            values=tuple(self.prices.keys()),
            size_hint=(None, None),
            size=(200, 44),
            on_text=self.update_price
        )
        layout.add_widget(self.service_spinner)

        # Display price label
        self.price_label = Label(text="Price: KES 0")
        layout.add_widget(self.price_label)

        # Quantity input
        layout.add_widget(Label(text="Enter quantity:"))
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')
        layout.add_widget(self.quantity_input)

        # Delivery location input
        layout.add_widget(Label(text="Enter delivery location:"))
        self.location_input = TextInput(hint_text="Delivery Location", multiline=False)
        layout.add_widget(self.location_input)

        # Submit order button
        submit_button = Button(text="Place Order", on_press=self.submit_order)
        layout.add_widget(submit_button)

        # Back button to home screen
        back_button = Button(text="Back to Home", on_press=self.go_back_home)
        layout.add_widget(back_button)

        # Feedback label for status updates
        self.feedback_label = Label(text="")
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def on_enter(self):
        self.fetch_services()

    def update_price(self, spinner, text):
        """Update price label based on selected service."""
        if text in self.prices:
            price = self.prices[text]
            self.price_label.text = f"Price: KES {price}"

    def fetch_services(self):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get('http://127.0.0.1:5000/api/services/groceries', headers=headers)
            if response.status_code == 200:
                self.prices = response.json()
                self.service_spinner.values = list(self.prices.keys())
            else:
                self.feedback_label.text = "Failed to fetch services."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def submit_order(self, instance):
        grocery_service = self.service_spinner.text
        location = self.location_input.text
        quantity = int(self.quantity_input.text) if self.quantity_input.text.isdigit() else 1

        if grocery_service == "Select Grocery Item" or not location:
            self.feedback_label.text = "Please complete all fields."
            return

        price = self.prices[grocery_service]
        total_price = price * quantity

        order_data = {
            'service': grocery_service,
            'price': price,
            'location': location,
            'quantity': quantity,
            'total_price': total_price
        }

        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.post('http://127.0.0.1:5000/api/orders', json=order_data, headers=headers)
            if response.status_code == 201:
                self.feedback_label.text = "Order placed successfully!"
            else:
                self.feedback_label.text = "Failed to place order."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def go_back_home(self, instance):
        self.manager.current = 'home'


class FruitScreen(Screen):
    def __init__(self, **kwargs):
        super(FruitScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Prices for fruit items
        self.prices = {
            'Mango': 100,
            'Banana': 100,
            'Watermelon': 350,
            'Grapes': 300,
            'Strawberry': 300
        }

        # Service selection dropdown
        layout.add_widget(Label(text="Choose fruit:"))
        self.service_spinner = Spinner(
            text='Select Fruit',
            values=tuple(self.prices.keys()),
            size_hint=(None, None),
            size=(200, 44),
            on_text=self.update_price
        )
        layout.add_widget(self.service_spinner)

        # Display price label
        self.price_label = Label(text="Price: KES 0")
        layout.add_widget(self.price_label)

        # Quantity input
        layout.add_widget(Label(text="Enter quantity:"))
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')
        layout.add_widget(self.quantity_input)

        # Delivery location input
        layout.add_widget(Label(text="Enter delivery location:"))
        self.location_input = TextInput(hint_text="Delivery Location", multiline=False)
        layout.add_widget(self.location_input)

        # Submit order button
        submit_button = Button(text="Place Order", on_press=self.submit_order)
        layout.add_widget(submit_button)

        # Back button to home screen
        back_button = Button(text="Back to Home", on_press=self.go_back_home)
        layout.add_widget(back_button)

        # Feedback label for status updates
        self.feedback_label = Label(text="")
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def on_enter(self):
        self.fetch_services()

    def update_price(self, spinner, text):
        """Update price label based on selected service."""
        if text in self.prices:
            price = self.prices[text]
            self.price_label.text = f"Price: KES {price}"

    def fetch_services(self):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get('http://127.0.0.1:5000/api/services/fruit', headers=headers)
            if response.status_code == 200:
                self.prices = response.json()
                self.service_spinner.values = list(self.prices.keys())
            else:
                self.feedback_label.text = "Failed to fetch services."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def submit_order(self, instance):
        fruit_service = self.service_spinner.text
        location = self.location_input.text
        quantity = int(self.quantity_input.text) if self.quantity_input.text.isdigit() else 1

        if fruit_service == "Select Fruit" or not location:
            self.feedback_label.text = "Please complete all fields."
            return

        price = self.prices[fruit_service]
        total_price = price * quantity

        order_data = {
            'service': fruit_service,
            'price': price,
            'quantity': quantity,
            'total_price': total_price,
            'location': location
        }

        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.post('http://127.0.0.1:5000/api/orders', json=order_data, headers=headers)
            if response.status_code == 201:
                self.feedback_label.text = "Order placed successfully!"
            else:
                self.feedback_label.text = "Failed to place order."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def go_back_home(self, instance):
        self.manager.current = 'home'

class GardeningScreen(Screen):
    def __init__(self, **kwargs):
        super(GardeningScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Prices for gardening services
        self.prices = {
            'Garbage Collection': 200,
            'Landscaping': 1000
        }

        # Service selection dropdown
        layout.add_widget(Label(text="Choose gardening service:"))
        self.service_spinner = Spinner(
            text='Select Gardening Service',
            values=tuple(self.prices.keys()),
            size_hint=(None, None),
            size=(200, 44),
            on_text=self.update_price
        )
        layout.add_widget(self.service_spinner)

        # Display price label
        self.price_label = Label(text="Price: KES 0")
        layout.add_widget(self.price_label)

        # Quantity input
        layout.add_widget(Label(text="Enter quantity:"))
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')
        layout.add_widget(self.quantity_input)

        # Delivery location input
        layout.add_widget(Label(text="Enter delivery location:"))
        self.location_input = TextInput(hint_text="Delivery Location", multiline=False)
        layout.add_widget(self.location_input)

        # Submit order button
        submit_button = Button(text="Place Order", on_press=self.submit_order)
        layout.add_widget(submit_button)

        # Back button to home screen
        back_button = Button(text="Back to Home", on_press=self.go_back_home)
        layout.add_widget(back_button)

        # Feedback label for status updates
        self.feedback_label = Label(text="")
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def on_enter(self):
        self.fetch_services()

    def update_price(self, spinner, text):
        """Update price label based on selected service."""
        if text in self.prices:
            price = self.prices[text]
            self.price_label.text = f"Price: KES {price}"

    def fetch_services(self):
        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.get('http://127.0.0.1:5000/api/services/gardening', headers=headers)
            if response.status_code == 200:
                self.prices = response.json()
                self.service_spinner.values = list(self.prices.keys())
            else:
                self.feedback_label.text = "Failed to fetch services."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def submit_order(self, instance):
        gardening_service = self.service_spinner.text
        location = self.location_input.text
        quantity = int(self.quantity_input.text) if self.quantity_input.text.isdigit() else 1

        if gardening_service == "Select Gardening Service" or not location:
            self.feedback_label.text = "Please complete all fields."
            return

        price = self.prices[gardening_service]
        total_price = price * quantity

        order_data = {
            'service': gardening_service,
            'price': price,
            'quantity': quantity,
            'total_price': total_price,
            'location': location
        }

        headers = {'Authorization': f'Bearer {self.manager.token}'}
        try:
            response = requests.post('http://127.0.0.1:5000/api/orders', json=order_data, headers=headers)
            if response.status_code == 201:
                self.feedback_label.text = "Order placed successfully!"
            else:
                self.feedback_label.text = "Failed to place order."
        except Exception as e:
            self.feedback_label.text = f"Error: {str(e)}"

    def go_back_home(self, instance):
        self.manager.current = 'home'

# ScreenManager to navigate between different services
class ServiceApp(App):
    def build(self):
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(AdminDashboard(name='admin_dashboard'))
        sm.add_widget(UserDashboard(name='user_dashboard'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CleaningScreen(name='cleaning'))
        sm.add_widget(FoodScreen(name='food'))
        sm.add_widget(GroceriesScreen(name='groceries'))
        sm.add_widget(FruitScreen(name='fruit'))
        sm.add_widget(GardeningScreen(name='gardening'))
        sm.current = 'login'
        return sm

if __name__ == '__main__':
    ServiceApp().run()