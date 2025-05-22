from flask import (
    Flask,
    Blueprint,
    request,
    session,
    render_template,
    flash,
    redirect,
    url_for,
)
import MySQLdb
import base64
from database import MySQL
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

GMAIL_USER = "itriagri@gmail.com"
GMAIL_PASSWORD = "bqhx kmok ddma uvyc"

mysql = MySQL(app)
auth = Blueprint("auth", __name__)


@auth.route("/get-started")
def getstarted():
    if session.get("logged_in"):
        return redirect(url_for("views.dashboard"))
    else:
        return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():

    if (request.method == "POST"):
        email = request.form["emailText"]
        password = request.form["passwordText"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s", (email, password,),)
        user = cursor.fetchone()

        if user:

            verified = user["email_verified"]

            if verified == 0:
                send_verification_email(email)
                error = "Please verify your email. A verification email has been sent."
                return redirect(url_for("auth.login", error=error))
            else:
                session["logged_in"] = True
                session["id"] = user["id"]
                session["email"] = user["email"]
                session["fname"] = user["first_name"]
                session["mname"] = user["middle_name"]
                session["lname"] = user["last_name"]
                session["fullname"] = (f"{user['first_name']} {user['middle_name'] + ' ' if user['middle_name'] else ''}{user['last_name']}"
                                       )
                session["role"] = user["roles"]
                return redirect(url_for("views.dashboard"))

        else:
            error = "Incorrect Email or Password"
            return render_template("login.html", error=error)

    return render_template("login.html")


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(
        app.config['SECRET_KEY'], "email-verification")
    return serializer.dumps(email, salt="email-verification")


def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(
        app.config['SECRET_KEY'], "email-verification")
    try:
        email = serializer.loads(
            token, salt="email-verification", max_age=expiration)
    except Exception as e:
        return False
    return email


def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    verification_url = url_for(
        'auth.verify_email', token=token, _external=True)

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = user_email
    msg['Subject'] = "Please verify your email address"

    body = f"Click the link to verify your email: {verification_url}"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(GMAIL_USER, GMAIL_PASSWORD)

    try:
        server.sendmail(GMAIL_USER, user_email, msg.as_string())
        server.quit()
        message = "Password reset email sent."
    except Exception as e:
        error = f"Failed to send email: {str(e)}"


@auth.route("/verify/<token>", methods=["GET", "POST"])
def verify_email(token):
    error = None
    success = None
    try:
        email = confirm_verification_token(token)
    except:
        error = "The email verification link is invalid or has expired."

    if email:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        verified_true = 1
        cursor.execute(
            "UPDATE users SET email_verified = %s WHERE email = %s", (verified_true, email,))
        mysql.connection.commit()
        success = "Your email has been verified!"
        return redirect(url_for('auth.login', success=success))
    else:
        error = "The verification link is invalid or has expired."
        return redirect(url_for('auth.signup', error=error))


@auth.route("/signup", methods=["POST", "GET"])
def signup():
    if (
        request.method == "POST"
        and "emailText" in request.form
        and "passwordText" in request.form
    ):
        fname = request.form["fnameText"]
        mname = request.form["mnameText"]
        lname = request.form["lnameText"]
        email = request.form["emailText"]
        password = request.form["passwordText"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        checkEmail = cursor.fetchone()

        if checkEmail:
            error = "Email already exists!"
            return render_template("signup.html", error=error)
        else:
            insertcursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            insertcursor.execute(
                "INSERT INTO users (first_name, middle_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)",
                (
                    fname,
                    mname,
                    lname,
                    email,
                    password,
                ),
            )
            mysql.connection.commit()
            send_verification_email(email)
            success = "Account created successfully, A verification email has been sent to your inbox!"
            return redirect(url_for("auth.login", success=success))

    return render_template("signup.html")


@auth.route("/logout")
def logout():
    session.clear()
    response = redirect("/")
    response.set_cookie("session", "", expires=0)  # Expire the session cookie
    return response


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], "password-reset")
    return serializer.dumps(email, salt="password-reset")


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], "password-reset")
    try:
        email = serializer.loads(
            token, salt="password-reset", max_age=expiration)
    except:
        return False
    return email


@auth.route("/forgot-password", methods=["POST", "GET"])
def forgotpassword():
    message = None
    error = None
    if request.method == "POST":
        email = request.form["email"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        checkEmail = cursor.fetchone()

        if checkEmail:
            token = generate_confirmation_token(email)
            confirm_url = url_for("auth.reset_password",
                                  token=token, _external=True)

            msg = MIMEMultipart()
            msg["From"] = GMAIL_USER
            msg["To"] = email
            msg["Subject"] = "Password Reset Request"

            body = (
                f"You are receiving this email because you requested a password reset for your account.\n\n"
                f"Please click on the following link to reset your password:\n\n"
                f"{confirm_url}\n\n"
                f"If you did not request a password reset, please ignore this email."
            )
            msg.attach(MIMEText(body, "plain"))


            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(GMAIL_USER, GMAIL_PASSWORD)

            try:
                server.sendmail(GMAIL_USER, email, msg.as_string())
                server.quit()
                message = "Password reset email sent."
            except Exception as e:
                error = f"Failed to send email: {str(e)}"
        else:
            error = "Email address not found."
        return render_template("forgot.html", error=error, success=message)

    return render_template("forgot.html", error=error, success=message)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    message = None
    error = None
    try:
        email = confirm_token(token)
    except:
        error = "The password reset link is invalid or has expired."

    if request.method == "POST":
        new_password = request.form["passwordText"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        checkEmail = cursor.fetchone()
        if checkEmail:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s", (new_password, email,))
            mysql.connection.commit()  # Commit the changes to the database
            message = "Password updated successfully!"
            return redirect(url_for("auth.login", success=message, error=error))
        else:
            error = "Invalid user."

    return render_template("resetpassword.html", success=message, error=error, token=token)
