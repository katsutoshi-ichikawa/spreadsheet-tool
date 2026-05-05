import os
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for
from sheets import get_kot_sheets, get_summary, get_store_employees

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "パスワードが違います"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    sheets = get_kot_sheets()
    selected = request.args.get("sheet", sheets[0] if sheets else None)
    summary, total = get_summary(selected) if selected else ([], 0)
    return render_template("index.html", sheets=sheets, selected=selected, summary=summary, total=total)


@app.route("/store/<sheet_name>/<path:store_name>")
@login_required
def store(sheet_name, store_name):
    employees = get_store_employees(sheet_name, store_name)
    return render_template("store.html", sheet_name=sheet_name, store_name=store_name, employees=employees)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
