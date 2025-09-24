from flask import Flask, redirect, url_for
from pathlib import Path
import pandas as pd
import sys, os

# Allow importing from routes/* without __init__.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from routes.users.users import users_bp # type: ignore
from routes.products.products import products_bp
from routes.orders.orders import orders_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key_here"

DATA_FILE = Path(__file__).parent / "data.xlsx"

def read_sheet(sheet):
    return pd.read_excel(DATA_FILE, sheet_name=sheet)

def write_sheet(df, sheet):
    # replace a single sheet while preserving others
    with pd.ExcelFile(DATA_FILE) as xls:
        all_sheets = {name: xls.parse(name) for name in xls.sheet_names}
    all_sheets[sheet] = df
    with pd.ExcelWriter(DATA_FILE, engine="openpyxl", mode="w") as writer:
        for name, sdf in all_sheets.items():
            sdf.to_excel(writer, sheet_name=name, index=False)

# expose helpers for blueprints
app.read_sheet = read_sheet
app.write_sheet = write_sheet

# register blueprints
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(orders_bp, url_prefix="/orders")

@app.route("/")
def home():
    return redirect(url_for("users.login"))

if __name__ == "__main__":
    app.run(debug=True)
