from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            department TEXT,
            position TEXT,
            salary TEXT,
            joining_date TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "1234":
        return redirect("/dashboard")

    return "Invalid Username or Password"

@app.route("/dashboard")
def dashboard():
    conn = get_db()

    total_employees = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    departments = conn.execute(
        "SELECT COUNT(DISTINCT department) FROM employees WHERE department != ''"
    ).fetchone()[0]

    current_month = datetime.now().strftime("%Y-%m")

    new_employees = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE joining_date LIKE ?",
        (current_month + "%",)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        departments=departments,
        new_employees=new_employees
    )

@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":

        conn = get_db()

        conn.execute("""
            INSERT INTO employees
            (full_name, email, phone, department, position, salary, joining_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["full_name"],
            request.form["email"],
            request.form["phone"],
            request.form["department"],
            request.form["position"],
            request.form["salary"],
            request.form["joining_date"]
        ))

        conn.commit()
        conn.close()

        return redirect("/view-employee")

    return render_template("add_employee.html")

@app.route("/view-employee")
def view_employee():
    conn = get_db()

    employees = conn.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "view_employee.html",
        employees=employees
    )
@app.route("/departments")
def departments_page():
    conn = get_db()

    departments = conn.execute("""
        SELECT department, COUNT(*) as total
        FROM employees
        WHERE department != ''
        GROUP BY department
        ORDER BY department
    """).fetchall()

    conn.close()

    return render_template(
        "departments.html",
        departments=departments
    )

@app.route("/new-employees")
def new_employees():
    current_month = datetime.now().strftime("%Y-%m")

    conn = get_db()

    employees = conn.execute("""
        SELECT * FROM employees
        WHERE joining_date LIKE ?
        ORDER BY id DESC
    """, (current_month + "%",)).fetchall()

    conn.close()

    return render_template(
        "new_employees.html",
        employees=employees
    )

@app.route("/attendance")
def attendance():
    return "<h1>Attendance</h1><p>Attendance page is working.</p><br><a href='/dashboard'>← Back to Dashboard</a>"
   
     
          

           
@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")

    conn = get_db()

    employees = conn.execute("""
        SELECT * FROM employees
        WHERE full_name LIKE ?
        OR email LIKE ?
        OR department LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    )).fetchall()

    conn.close()

    return render_template(
        "search.html",
        employees=employees,
        keyword=keyword
    )

@app.route("/logout")
def logout():
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)