from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = "student27"

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="sms",
        user="postgres",
        password="root",
        port="5432"
    )

con = get_connection()
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
)
""")

con.commit()
cur.close()
con.close()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute(
                "INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            con.commit()

            return redirect('/login')

        except psycopg2.errors.UniqueViolation:
            con.rollback()
            return "Email Already Registered!"

        finally:
            cur.close()
            con.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        con = get_connection()
        cur = con.cursor()

        cur.execute("SELECT * FROM students WHERE email=%s AND password=%s",
                    (request.form['email'], request.form['password']))

        data = cur.fetchone()
        cur.close()
        con.close()

        if data:
            session['student_id'] = data[0]
            return redirect('/dashboard')
        return "Invalid Email or Password!"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect('/login')

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT id,name,email FROM students WHERE id=%s",
                (session['student_id'],))
    student = cur.fetchone()

    cur.close()
    con.close()

    return render_template('dashboard.html', student=student)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'student_id' not in session:
        return redirect('/login')

    con = get_connection()
    cur = con.cursor()

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        cur.execute(
                "UPDATE students SET name=%s, email=%s WHERE id=%s",
                (name, email, session['student_id'])
            )

        con.commit()
        cur.close()
        con.close()

        return redirect('/dashboard')

    cur.execute(
               "SELECT name,email FROM students WHERE id=%s",
                (session['student_id'],)
            )

    student = cur.fetchone()
    cur.close()
    con.close()
    return render_template('update.html', student=student)

@app.route('/delete', methods=['POST'])
def delete():
    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM students WHERE id=%s",
        (session['student_id'],)
    )

    con.commit()
    cur.close()
    con.close()

    session.clear()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
