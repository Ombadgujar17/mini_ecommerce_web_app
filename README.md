# Mini E-Commerce Web App

A simple e-commerce web application built with Flask, using Excel files for data storage. This app allows customers to register, log in, browse products, place orders, and view their order history. Admins can manage customers, products, and orders through a dedicated dashboard.

## Features

- Customer registration and login
- Product listing and purchase
- Order management for customers and admins
- Admin dashboard for managing customers, products, and orders
- Data stored in Excel files (`data.xlsx`)
- Modern, responsive UI with Bootstrap

## Project Structure

```
mini_ecommerce_web_app/
│
├── app.py
├── data.xlsx
├── requirements.txt
├── routes/
│   ├── users/
│   │   └── users.py
│   ├── products/
│   │   └── products.py
│   └── orders/
│       └── orders.py
├── static/
├── templates/
│   ├── users/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── admin_customers.html
│   │   ├── add_customer.html
│   │   ├── edit_customer.html
│   ├── products/
│   │   ├── products.html
│   │   ├── admin_products.html
│   │   ├── add_product.html
│   │   └── edit_product.html
│   └── orders/
│       ├── orders.html
│       └── admin_orders.html
```

## Setup Instructions

1. **Clone the repository**

   ```sh
   git clone <repo-url>
   cd mini_ecommerce_web_app
   ```

2. **Install dependencies**

   It is recommended to use a virtual environment:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```sh
   python app.py
   ```

4. **Access the app**

   Open your browser and go to `http://127.0.0.1:5000/`

## Notes

- The app uses `data.xlsx` for storing customers, products, and orders. Make sure this file exists and has the required sheets.
- Admin login is available at `/admin_login`.
- UI is styled with Bootstrap and custom CSS for a modern look.

## Requirements

- Python 3.8+
- See `requirements.txt` for Python package dependencies

## License

This project is for educational/demo purposes.
