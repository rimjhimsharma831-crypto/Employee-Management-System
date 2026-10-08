from flask import Flask, render_template, request, redirect
import os
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("DB_HOST =", os.getenv("DB_HOST"))

if os.getenv("DB_SSL_CA"):
    CERT_PATH = "/tmp/tidb-ca.pem"

    with open(CERT_PATH, "w") as f:
        f.write(os.getenv("DB_SSL_CA"))
else:
    CERT_PATH = "certs/cert.pem"

app = Flask(__name__)



def get_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 4000)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=CERT_PATH
    )
    return conn



def create_table():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            department VARCHAR(100),
            position VARCHAR(100),
            salary VARCHAR(50),
            joining_date VARCHAR(50)
        )
    """)

    conn.commit()
    cursor.close()
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
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM employees"
    )
    total_employees = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT department) FROM employees "
        "WHERE department != ''"
    )
    departments = cursor.fetchone()[0]

    current_month = datetime.now().strftime("%Y-%m")

    cursor.execute(
        "SELECT COUNT(*) FROM employees "
        "WHERE joining_date LIKE %s",
        (current_month + "%",)
    )
    new_employees = cursor.fetchone()[0]

    cursor.close()
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
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO employees
            (full_name, email, phone, department, position, salary, joining_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        cursor.close()
        conn.close()

        return redirect("/view-employee")

    return render_template("add_employee.html")


@app.route("/view-employee")
def view_employee():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    )

    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "view_employee.html",
        employees=employees
    )


@app.route("/departments")
def departments_page():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT department, COUNT(*) AS total
        FROM employees
        WHERE department != ''
        GROUP BY department
        ORDER BY department
    """)

    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "departments.html",
        departments=departments
    )


@app.route("/new-employees")
def new_employees():
    current_month = datetime.now().strftime("%Y-%m")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM employees
        WHERE joining_date LIKE %s
        ORDER BY id DESC
    """, (current_month + "%",))

    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "new_employees.html",
        employees=employees
    )


@app.route("/attendance")
def attendance():
    return """
        <h1>Attendance</h1>
        <p>Attendance page is working.</p>
        <br>
        <a href="/dashboard">← Back to Dashboard</a>
    """


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM employees
        WHERE full_name LIKE %s
        OR email LIKE %s
        OR department LIKE %s
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    employees = cursor.fetchall()

    cursor.close()
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