import os
from flask import Flask, render_template, request
from sheets import get_kot_sheets, get_summary, get_store_employees

app = Flask(__name__)


@app.route("/")
def index():
    sheets = get_kot_sheets()
    selected = request.args.get("sheet", sheets[0] if sheets else None)
    summary, total = get_summary(selected) if selected else ([], 0)
    return render_template("index.html", sheets=sheets, selected=selected, summary=summary, total=total)


@app.route("/store/<sheet_name>/<path:store_name>")
def store(sheet_name, store_name):
    employees = get_store_employees(sheet_name, store_name)
    return render_template("store.html", sheet_name=sheet_name, store_name=store_name, employees=employees)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
