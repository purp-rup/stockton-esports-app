from EsportsManagementTool import app
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import MySQLdb.cursors
import re
import bcrypt
import secrets
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from EsportsManagementTool import mysql


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['id'],))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=user)