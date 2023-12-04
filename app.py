from flask import Flask, render_template, request, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
import sqlite3
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('my_database.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table (if it doesn't exist)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT
                )''')
conn.commit()

# Main route to display users and perform search
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Search functionality based on name or email
        search_term = request.form['search']
        cursor.execute('''SELECT * FROM users WHERE name LIKE ? OR email LIKE ?''',
                       ('%' + search_term + '%', '%' + search_term + '%'))
        rows = cursor.fetchall()
        return render_template('index.html', users=rows)
    else:
        # Display all users when no search term is provided
        cursor.execute('''SELECT * FROM users''')
        rows = cursor.fetchall()
        return render_template('index.html', users=rows)

# Route to add a new user
@app.route('/add', methods=['POST'])
def add_user():
    # Retrieve user data from form and insert into the database
    name = request.form['name']
    email = request.form['email']
    cursor.execute('''INSERT INTO users (name, email) VALUES (?, ?)''', (name, email))
    conn.commit()
    return redirect(url_for('index'))

# Route to update user information
@app.route('/update/<int:user_id>', methods=['POST'])
def update_user(user_id):
    # Update user information in the database
    new_name = request.form['name']
    new_email = request.form['email']
    cursor.execute('''UPDATE users SET name = ?, email = ? WHERE id = ?''', (new_name, new_email, user_id))
    conn.commit()
    return redirect(url_for('index'))

# Route to delete a user
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    # Delete a user from the database
    cursor.execute('''DELETE FROM users WHERE id = ?''', (user_id,))
    conn.commit()
    return redirect(url_for('index'))

# Route to download user data as Excel
@app.route('/download_excel')
def download_excel():
    # Retrieve user data and convert it to Excel format
    cursor.execute('''SELECT name, email FROM users''')
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['Name', 'Email'])
    
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    
    # Send the Excel file for download
    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='user_data.xlsx'
    )

# Route to download user data as PDF
@app.route('/download_pdf')
def download_pdf():
    # Retrieve user data and convert it to PDF format
    cursor.execute('''SELECT name, email FROM users''')
    rows = cursor.fetchall()

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    y = 700
    for row in rows:
        name, email = row
        c.drawString(100, y, f'Name: {name}, Email: {email}')
        y -= 20
    c.save()
    pdf_buffer.seek(0)
    
    # Send the PDF file for download
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='user_data.pdf'
    )
    
if __name__ == '__main__':
    app.run(debug=True)
