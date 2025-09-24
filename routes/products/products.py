from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
import pandas as pd

products_bp = Blueprint("products", __name__, template_folder="../../templates/products")

@products_bp.get("/")
def list_products():
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    df = current_app.read_sheet("Products")
    products = df.to_dict(orient="records")
    return render_template("products/products.html", products=products, username=session.get("user_name"))

# Admin product pages (templates/products/*.html)
@products_bp.get("/admin_products")
def admin_products():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Products")
    return render_template("products/admin_products.html", products=df.to_dict(orient="records"))

@products_bp.get("/add_product")
def add_product_form():
    if not session.get("admin_logged_in"):
        return redirect(url_for("users.admin_login"))
    return render_template("products/add_product.html")

@products_bp.post("/add_product")
def add_product():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Products")
    new_id = int(df["Id"].max() + 1) if not df.empty else 1
    new_product = {
        "Id": new_id,
        "Name": request.form["name"].strip(),
        "Price": float(request.form["price"])
    }
    df = pd.concat([df, pd.DataFrame([new_product], columns=df.columns)], ignore_index=True)
    current_app.write_sheet(df, "Products")
    flash("Product added successfully!")
    return redirect(url_for("products.admin_products"))

@products_bp.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Products")
    product = df[df["Id"] == product_id].iloc[0]
    if request.method == "POST":
        df.loc[df["Id"] == product_id, ["Name","Price"]] = [
            request.form["name"].strip(),
            float(request.form["price"])
        ]
        current_app.write_sheet(df, "Products")
        flash("Product updated successfully!")
        return redirect(url_for("products.admin_products"))
    return render_template("products/edit_product.html", product=product)

@products_bp.get("/delete_product/<int:product_id>")
def delete_product(product_id):
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Products")
    df = df[df["Id"] != product_id]
    current_app.write_sheet(df, "Products")
    flash(f"Product {product_id} deleted successfully!")
    return redirect(url_for("products.admin_products"))
