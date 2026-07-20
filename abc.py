from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "sunrayz_secret_key_2026"

# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="sunrayz_db"
    )

# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s AND password=%s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["role"] = user[4]

            # ---------------- ADMIN ---------------- #

            if user[4] == "admin":

                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role='employee'"
                )
                employee_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks"
                )
                task_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
                )
                pending_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM clients"
                )
                client_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
                )
                completed_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE priority='High'"
                )
                high_priority_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM tasks
                    WHERE DATE(due_date)=CURDATE()
                """)
                today_count = cursor.fetchone()[0]

                conn.close()

                return render_template(
                    "admin_dashboard.html",
                    employee_count=employee_count,
                    task_count=task_count,
                    pending_count=pending_count,
                    client_count=client_count,
                    completed_count=completed_count,
                    high_priority_count=high_priority_count,
                    today_count=today_count
                )

            # ---------------- EMPLOYEE ---------------- #

            else:

                cursor.execute(
                    """
                    SELECT id,
                           title,
                           description,
                           status,
                           priority,
                           due_date
                    FROM tasks
                    WHERE assigned_to=%s
                    """,
                    (user[0],)
                )

                tasks = cursor.fetchall()

                conn.close()

                return render_template(
                    "employee_dashboard.html",
                    employee_name=user[1],
                    tasks=tasks
                )

        conn.close()

        return "Invalid Email or Password"

    return render_template("login.html")


# ---------------- ADD EMPLOYEE ---------------- #

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(name,email,password,role)
            VALUES(%s,%s,%s,'employee')
            """,
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return "Employee Added Successfully!"

    return render_template("add_employee.html")


# ---------------- VIEW EMPLOYEES ---------------- #

@app.route("/employees")
def employees():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search")

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT id, name, email
            FROM users
            WHERE role='employee'
            AND (
                name LIKE %s
                OR email LIKE %s
            )
        """, (f"%{search}%", f"%{search}%"))

    else:

        cursor.execute("""
            SELECT id, name, email
            FROM users
            WHERE role='employee'
        """)

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "employees.html",
        employees=employees
    )


# ---------------- ASSIGN TASK ---------------- #

@app.route("/assign_task", methods=["GET", "POST"])
def assign_task():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]

        cursor.execute(
            """
            INSERT INTO tasks
            (title,description,assigned_to,status,priority,due_date)
            VALUES(%s,%s,%s,'Pending',%s,%s)
            """,
            (title, description, assigned_to, priority, due_date)
        )

        conn.commit()

        return redirect(url_for("assign_task"))

    cursor.execute(
        """
        SELECT id,name
        FROM users
        WHERE role='employee'
        """
    )

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "assign_task.html",
        employees=employees
    )


# ---------------- UPDATE TASK ---------------- #

@app.route("/update_task/<int:task_id>", methods=["GET", "POST"])
def update_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        status = request.form["status"]

        if status == "Completed":

            cursor.execute(
                """
                UPDATE tasks
                SET status=%s,
                    completed_on=NOW()
                WHERE id=%s
                """,
                (status, task_id)
            )

        else:

            cursor.execute(
                """
                UPDATE tasks
                SET status=%s
                WHERE id=%s
                """,
                (status, task_id)
            )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    conn.close()

    return render_template("update_task.html")

# ---------------- ADD CLIENT ---------------- #

@app.route("/add_client", methods=["GET", "POST"])
def add_client():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        client_name = request.form["client_name"]
        company_name = request.form["company_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        project_name = request.form["project_name"]
        status = request.form["status"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO clients
            (client_name, company_name, email, phone, project_name, status)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                client_name,
                company_name,
                email,
                phone,
                project_name,
                status
            )
        )

        conn.commit()
        conn.close()

        return "Client Added Successfully!"

    return render_template("add_client.html")

# ---------------- VIEW CLIENTS ---------------- #

@app.route("/clients")
def clients():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search")

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT *
            FROM clients
            WHERE client_name LIKE %s
               OR company_name LIKE %s
               OR email LIKE %s
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("SELECT * FROM clients")

    clients = cursor.fetchall()

    conn.close()

    return render_template(
        "clients.html",
        clients=clients
    )
# ---------------- EDIT CLIENT ---------------- #

@app.route("/edit_client/<int:id>", methods=["GET", "POST"])
def edit_client(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        client_name = request.form["client_name"]
        company_name = request.form["company_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        project_name = request.form["project_name"]
        status = request.form["status"]

        cursor.execute(
            """
            UPDATE clients
            SET client_name=%s,
                company_name=%s,
                email=%s,
                phone=%s,
                project_name=%s,
                status=%s
            WHERE id=%s
            """,
            (
                client_name,
                company_name,
                email,
                phone,
                project_name,
                status,
                id
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("clients"))

    cursor.execute(
        "SELECT * FROM clients WHERE id=%s",
        (id,)
    )

    client = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_client.html",
        client=client
    )

# ---------------- DELETE CLIENT ---------------- #

@app.route("/delete_client/<int:id>")
def delete_client(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM clients WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("clients"))

# ---------------- VIEW TASKS ---------------- #

@app.route("/tasks")
def tasks():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search")

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT
                tasks.id,
                tasks.title,
                users.name,
                tasks.status,
                tasks.priority,
                tasks.due_date
            FROM tasks
            JOIN users
            ON tasks.assigned_to = users.id
            WHERE
                tasks.title LIKE %s
                OR users.name LIKE %s
                OR tasks.status LIKE %s
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                tasks.id,
                tasks.title,
                users.name,
                tasks.status,
                tasks.priority,
                tasks.due_date
            FROM tasks
            JOIN users
            ON tasks.assigned_to = users.id
        """)

    tasks = cursor.fetchall()

    conn.close()

    return render_template(
        "tasks.html",
        tasks=tasks
    )
# ---------------- EDIT TASK ---------------- #

@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE tasks
            SET title=%s,
                description=%s,
                priority=%s,
                due_date=%s,
                status=%s
            WHERE id=%s
        """,
        (
            title,
            description,
            priority,
            due_date,
            status,
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("tasks"))

    cursor.execute(
        "SELECT * FROM tasks WHERE id=%s",
        (id,)
    )

    task = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_task.html",
        task=task
    )

# ---------------- DELETE TASK ---------------- #

@app.route("/delete_task/<int:id>")
def delete_task(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("tasks"))

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)