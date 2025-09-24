from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from datetime import datetime
import pandas as pd

orders_bp = Blueprint("orders", __name__, template_folder="../../templates/orders")

# Customer: list own orders
@orders_bp.get("/")
def user_orders():
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    df_orders = current_app.read_sheet("Orders")
    df_products = current_app.read_sheet("Products")

    user_orders = df_orders[df_orders["C_ID"] == session["user_id"]]
    out = []
    for _, o in user_orders.iterrows():
        prow = df_products[df_products["Id"] == o["P_ID"]]
        name = prow.iloc[0]["Name"] if not prow.empty else f"Product #{int(o['P_ID'])}"
        price = prow.iloc[0]["Price"] if not prow.empty else None
        out.append({
            "OrderId": int(o["Id"]),
            "Product": name,
            "Price": price,
            "Timestamp": o["Timestamp"]
        })
    return render_template("orders/orders.html", orders=out, username=session.get("user_name"))

# Customer: buy product
@orders_bp.post("/buy/<int:product_id>")
def buy(product_id):
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    df_orders = current_app.read_sheet("Orders")
    df_products = current_app.read_sheet("Products")

    if df_products[df_products["Id"] == product_id].empty:
        flash(f"Product {product_id} not found.")
        return redirect(url_for("products.list_products"))

    new_id = int(df_orders["Id"].max() + 1) if not df_orders.empty else 1
    row = {
        "Id": new_id,
        "C_ID": int(session["user_id"]),
        "P_ID": int(product_id),
        "Quantity": 1,
        "Amount": None,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df_orders = pd.concat([df_orders, pd.DataFrame([row], columns=df_orders.columns)], ignore_index=True)
    current_app.write_sheet(df_orders, "Orders")
    flash("Order placed successfully!")
    return redirect(url_for("orders.user_orders"))

# Admin: list all orders
@orders_bp.get("/admin")
def admin_orders():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))

    df_orders = current_app.read_sheet("Orders")
    df_products = current_app.read_sheet("Products")
    df_customers = current_app.read_sheet("Customers")

    rows = []
    for _, o in df_orders.iterrows():
        prow = df_products[df_products["Id"] == o["P_ID"]]
        crow = df_customers[df_customers["Id"] == o["C_ID"]]
        product_name = prow.iloc[0]["Name"] if not prow.empty else f"Product #{int(o['P_ID'])}"
        price = prow.iloc[0]["Price"] if not prow.empty else None
        customer_name = crow.iloc[0]["Name"] if not crow.empty else f"Customer #{int(o['C_ID'])}"
        rows.append({
            "OrderId": int(o["Id"]),
            "Customer": customer_name,
            "Product": product_name,
            "Price": price,
            "Timestamp": o["Timestamp"]
        })
    return render_template("orders/admin_orders.html", orders=rows)

@orders_bp.post("/delete/<int:order_id>")
def delete_order(order_id):
    # Auth checks
    is_admin = bool(session.get("admin_logged_in"))
    user_id = session.get("user_id")

    if not is_admin and not user_id:
        flash("Please log in first.")
        return redirect(url_for("users.login"))

    df_orders = current_app.read_sheet("Orders")

    target = df_orders[df_orders["Id"] == order_id]
    if target.empty:
        flash(f"Order {order_id} not found.")
        return redirect(url_for("orders.admin_orders") if is_admin else url_for("orders.user_orders"))

    row = target.iloc[0]

    # Authorization: admin can delete any; customer can delete only own
    if not is_admin and int(row["C_ID"]) != int(user_id):
        flash("Not authorized to delete this order.")
        return redirect(url_for("orders.user_orders"))

    # Perform delete
    df_orders = df_orders[df_orders["Id"] != order_id].copy()
    try:
        df_orders["Id"] = df_orders["Id"].astype(int)
    except Exception:
        pass

    current_app.write_sheet(df_orders, "Orders")
    flash("Order deleted successfully.")
    # Redirect based on role or 'next' query/form param
    nxt = request.args.get("next") or request.form.get("next")
    if nxt:
        return redirect(nxt)
    return redirect(url_for("orders.admin_orders") if is_admin else url_for("orders.user_orders"))
