from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
import pandas as pd

users_bp = Blueprint("users", __name__, template_folder="../../templates/users")

# -------- Customer auth --------
@users_bp.get("/register")
def register():
    return render_template("users/register.html")

@users_bp.post("/register")
def register_post():
    df = current_app.read_sheet("Customers")
    email = request.form["email"].strip().lower()
    if not df[df["Email"].astype(str).str.strip().str.lower() == email].empty:
        flash("Email already registered")
        return redirect(url_for("users.register"))
    new_id = int(df["Id"].max() + 1) if not df.empty else 1
    new_row = {
        "Id": new_id,
        "Name": request.form["name"].strip(),
        "Email": email,
        "Password": request.form["password"].strip(),
        "Phone": request.form["phone"].strip(),
        "Address": request.form["address"].strip(),
        "Role": "customer"
    }
    df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
    current_app.write_sheet(df, "Customers")
    flash("Registration successful, please login")
    return redirect(url_for("users.login"))

@users_bp.get("/login")
def login():
    return render_template("users/login.html")

@users_bp.post("/login")
def login_post():
    df = current_app.read_sheet("Customers")
    email = request.form["email"].strip().lower()
    password = request.form["password"].strip()
    df["Email"] = df["Email"].astype(str).str.strip().str.lower()
    df["Password"] = df["Password"].astype(str).str.strip()
    df["Role"] = df["Role"].astype(str).str.strip().str.lower()
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    if user.empty:
        flash("Invalid email or password")
        return render_template("users/login.html")
    session["user_id"] = int(user.iloc[0]["Id"])
    session["user_name"] = user.iloc[0]["Name"]
    if user.iloc[0]["Role"] == "admin":
        flash("Welcome Admin!")
        return redirect(url_for("users.admin_dashboard"))
    flash("Welcome!")
    return redirect(url_for("products.list_products"))

@users_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("users.login"))

@users_bp.get("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    return render_template("users/dashboard.html", username=session.get("user_name"))

# -------- Admin auth --------
@users_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form["email"].strip().lower()
        password = request.form["password"].strip()
        df = current_app.read_sheet("Customers")
        df["Email"] = df["Email"].astype(str).str.strip().str.lower()
        df["Password"] = df["Password"].astype(str).str.strip()
        df["Role"] = df["Role"].astype(str).str.strip().str.lower()
        admin_user = df[(df["Email"] == username) & (df["Password"] == password) & (df["Role"] == "admin")]
        if not admin_user.empty:
            session["admin_logged_in"] = True
            session["admin_name"] = admin_user.iloc[0]["Name"]
            flash("Welcome Admin!")
            return redirect(url_for("users.admin_dashboard"))
        else:
            error = "Invalid admin credentials"
    return render_template("users/admin_login.html", error=error)

@users_bp.get("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    return render_template("users/admin_dashboard.html")

@users_bp.get("/admin_logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Admin logged out.")
    return redirect(url_for("users.admin_login"))

# -------- Admin: Customers --------
@users_bp.get("/admin/customers")
def admin_customers():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Customers")
    customers = df.to_dict(orient="records")
    return render_template("users/admin_customers.html", customers=customers)

@users_bp.get("/admin/delete_customer/<int:customer_id>")
def delete_customer(customer_id):
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Customers")
    df = df[df["Id"] != customer_id]
    current_app.write_sheet(df, "Customers")
    flash(f"Customer {customer_id} deleted successfully!")
    return redirect(url_for("users.admin_customers"))

@users_bp.route("/admin/add_customer", methods=["GET", "POST"])
def add_customer():
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    if request.method == "POST":
        df = current_app.read_sheet("Customers")
        new_id = int(df["Id"].max() + 1) if not df.empty else 1
        new_customer = {
            "Id": new_id,
            "Name": request.form["name"].strip(),
            "Email": request.form["email"].strip().lower(),
            "Password": request.form["password"].strip(),
            "Phone": request.form["phone"].strip(),
            "Address": request.form["address"].strip(),
            "Role": request.form["role"].strip().lower()
        }
        df = pd.concat([df, pd.DataFrame([new_customer], columns=df.columns)], ignore_index=True)
        current_app.write_sheet(df, "Customers")
        flash("Customer added successfully!")
        return redirect(url_for("users.admin_customers"))
    return render_template("users/add_customer.html")

@users_bp.route("/admin/edit_customer/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("users.admin_login"))
    df = current_app.read_sheet("Customers")
    customer = df[df["Id"] == customer_id].iloc[0]
    if request.method == "POST":
        df.loc[df["Id"] == customer_id, ["Name","Email","Password","Phone","Address","Role"]] = [
            request.form["name"].strip(),
            request.form["email"].strip().lower(),
            request.form["password"].strip(),
            request.form["phone"].strip(),
            request.form["address"].strip(),
            request.form["role"].strip().lower()
        ]
        current_app.write_sheet(df, "Customers")
        flash("Customer updated successfully!")
        return redirect(url_for("users.admin_customers"))
    return render_template("users/edit_customer.html", customer=customer)
