from flask import (
    Blueprint,
    session,
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Flask,
    jsonify,
    send_file,
)
from PIL import Image
import os
import json
from database import MySQL
import MySQLdb
import base64
from datetime import datetime

app = Flask(__name__)
mysql = MySQL(app)

views = Blueprint("views", __name__)

app.config["UPLOAD_FOLDER"] = "website/models/"
app.config["UPLOAD_FOLDER_IMAGE"] = "website/static/img/"
app.config["FETCH_FOLDER_IMAGE"] = "static/img/"

# Routes that don't require authentication
EXCLUDED_ROUTES = ['login', 'static']  # Add route names here


@app.before_request
def check_session():
    # Skip authentication check for excluded routes
    if request.endpoint not in EXCLUDED_ROUTES and 'user' not in session:
        return redirect(url_for('login'))


def render_picture(data):
    return base64.b64encode(data).decode("ascii")


def update_setting(q, w, e, r, t, y):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        UPDATE settings SET
        website_title = %s,
        welcome_title = %s,
        welcome_subtitle = %s,
        about_us = %s,
        phone = %s,
        email = %s
        WHERE id = 1
    """
    cursor.execute(query, (q, w, e, r, t, y))
    mysql.connection.commit()
    cursor.close()


def update_insect(id, name, t1, c1, t2, c2):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        UPDATE insects SET
        insect_name = %s,
        insect_title1 = %s,
        insect_description = %s,
        insect_title2 = %s,
        insect_treatment = %s
        WHERE insect_id = %s
    """
    cursor.execute(query, (name, t1, c1, t2, c2, id))
    mysql.connection.commit()
    cursor.close()


def update_user(z, x, c, v, b):
    id = session.get("id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        UPDATE users
        SET
            first_name = %s,
            middle_name = %s,
            last_name = %s,
            email = %s,
            password = %s
        WHERE id = %s
    """
    cursor.execute(query, (z, x, c, v, b, id))
    mysql.connection.commit()
    cursor.close()


def db_insert_insect(name, title1, description, title2, treatment, image):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "INSERT INTO insects (insect_name, insect_title1, insect_description, insect_title2, insect_treatment, insect_image) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (name, title1, description,
                   title2, treatment, image))
    mysql.connection.commit()
    cursor.close()


def db_request_insect(user_id, insect_name, description, render_file):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "INSERT INTO requests (id, insect_name, description, insect_image) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, insect_name, description, render_file))
    mysql.connection.commit()
    cursor.close()


def fetch_insects():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM insects"
    cursor.execute(query)
    insects_data = cursor.fetchall()

    return insects_data


def fetch_pictures(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM insect_picture WHERE insect_id = %s"
    cursor.execute(query, (id,))
    insects_pictures = cursor.fetchall()
    return insects_pictures


@views.route('/images/<filename>')
def serve_image(filename):
    filepath = os.path.join(app.config["FETCH_FOLDER_IMAGE"], filename)
    return send_file(filepath)


@views.route("/")
def index():

    insects_data = fetch_insects()

    id = "1"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM settings WHERE id = %s", (id,))
    s = cursor.fetchone()

    if s:
        title = s["website_title"]
        w_title = s["welcome_title"]
        w_subtitle = s["welcome_subtitle"]
        about_us = s["about_us"]
        phone = s["phone"]
        email = s["email"]

        if email == "":
            email = "PAKAENAM NI RHOVIN"
        if phone == "":
            phone = "PAKAENAM NI RHOVIN"

    else:
        title = "Rice Insect Identification"
        w_title = ""
        w_subtitle = ""
        about_us = ""
        phone = "PAKAENAM NI RHOVIN"
        email = "PAKAENAM NI RHOVIN"
    return render_template(
        "index.html",
        title=title,
        w_title=w_title,
        w_subtitle=w_subtitle,
        about_us=about_us,
        phone=phone,
        email=email,
        insects=insects_data,
    )


@views.route("/dashboard")
def dashboard():
    

    return render_template("dashboard.html")


@views.route("/login")
def login():
    return render_template("login.html")


@views.route("/settings", methods=["POST", "GET"])
def settings():

    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    message = None
    error = None

    if request.method == "POST":
        f_name = request.form["f_name"]
        m_name = request.form["m_name"]
        l_name = request.form["l_name"]
        email = request.form["email"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            error = "Password is not the same"
        else:
            update_user(f_name, m_name, l_name, email, password1)
            message = "Updated successfully!"

    id = session.get("id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if user:
        f_name = user["first_name"]
        m_name = user["middle_name"]
        l_name = user["last_name"]
        email = user["email"]
        password = user["password"]
    else:
        f_name = None
        m_name = None
        l_name = None
        email = None
        password = None

    return render_template(
        "settings.html",
        f_name=f_name,
        m_name=m_name,
        l_name=l_name,
        email=email,
        password=password,
        error=error,
        success=message
    )


@views.route("/insectdetailed", methods=["GET"])
def insectdetailed():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    if request.method == "GET" and request.args.get("id"):
        id = request.args.get("id")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT * FROM insects WHERE insect_id = %s"
        cursor.execute(query, (id,))
        insect = cursor.fetchone()
        cursor.close()

        pictures = fetch_pictures(id)

        if not insect:
            error = "Insect not found."
            return redirect(url_for("views.insects", error=error))
        return render_template("insectdetailed.html", insect=insect, pictures=pictures)

    return redirect(url_for("views.insects"))


@views.route("/insectdetail", methods=["GET"])
def insectdetail():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    if request.method == "GET" and request.args.get("id"):
        id = request.args.get("id")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT * FROM insects WHERE insect_id = %s"
        cursor.execute(query, (id,))
        insect = cursor.fetchone()
        cursor.close()

        pictures = fetch_pictures(id)

        if not insect:
            error = "Insect not found."
            return redirect(url_for("views.insects", error=error))
        return render_template("insectdetail.html", insect=insect, pictures=pictures)

    return redirect(url_for("views.insects"))


@views.route("/updateinsect", methods=["POST", "GET"])
def updateinsect():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    message = None
    error = None
    if session.get("role") != "Administrator":
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        id = request.form["insect_id"]
        name = request.form["insect_name"]
        t1 = request.form["title_1"]
        c1 = request.form["context_1"]
        t2 = request.form["title_2"]
        c2 = request.form["context_2"]

        try:
            update_insect(id, name, t1, c1, t2, c2)
            message = "Insect updated successfully"
        except Exception as e:
            error = "Error: Insect did not update!"

        return redirect(url_for("views.insects", id=id, error=error, success=message))


@views.route("/addpictures", methods=["POST", "GET"])
def addpictures():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    if session.get("role") != "Administrator":
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        insect_image = request.files["insectImage"]
        id = request.form["insect_id"]
        try:
            data = insect_image.read()
            render_file = render_picture(data)
            db_insert_picture(id, render_file)
            message = "Insect picture successfully"
            id = request.form["insect_id"]
            return render_template("addpictures.html", success=message, id=id)

        except Exception as e:
            message = "Error adding picture"
            id = request.form["insect_id"]

            return render_template("addpictures.html", error=message, id=id)
    else:
        id = request.args.get("id")

        return render_template("addpictures.html", id=id)


def db_insert_picture(id, render_file):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "INSERT INTO insect_picture (insect_id, picture) VALUES (%s, %s)"
    cursor.execute(query, (id, render_file))
    mysql.connection.commit()
    cursor.close()


@views.route("/insects")
def insects():

    insects_data = fetch_insects()

    return render_template("insects.html", insects=insects_data)


@views.route("/addinsect", methods=["POST", "GET"])
def addinsect():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    if session.get("role") != "Administrator":
        return redirect(url_for("views.dashboard"))
    if request.method == "POST" and "insectnameText" in request.form:
        insect_name = request.form["insectnameText"]
        insect_title1 = request.form["insecttitle1Text"]
        insect_description = request.form["descriptionText"]
        insect_title2 = request.form["insecttitle2Text"]
        insect_treatment = request.form["treatmentText"]
        insect_image = request.files["insectImage"]

        try:
            data = insect_image.read()
            render_file = render_picture(data)
            db_insert_insect(
                insect_name, insect_title1, insect_description, insect_title2, insect_treatment, render_file
            )
            message = "Insect added successfully"
            return render_template("addinsect.html", success=message)

        except Exception as e:
            message = "Error adding insect"
            return render_template("addinsect.html", error=message)

    return render_template("addinsect.html")

@views.route("/deletepic", methods=["GET"])
def deletepic():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    message = None
    error = None
    if session.get("role") == "Administrator":
        picid = request.args.get("picid")
        insectid = request.args.get("id")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "DELETE FROM insect_picture WHERE pic_id = %s"

        try:
            cursor.execute(query, (picid,))
            mysql.connection.commit()
            message = "Picture deleted successfully."

        except Exception as e:
            mysql.connection.rollback()
            error = "Error deleting insect"
        finally:
            cursor.close()

        return redirect(url_for("views.insectdetailed", id=insectid, success=message, error=error))
    else:
        return redirect(url_for("views.dashboard"))

@views.route("/deleteinsect", methods=["GET"])
def deleteinsect():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    message = None
    error = None
    if session.get("role") == "Administrator":
        id = request.args.get("id")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "DELETE FROM insects WHERE insect_id = %s"

        try:
            cursor.execute(query, (id,))
            mysql.connection.commit()
            message = "Insect deleted successfully."

        except Exception as e:
            mysql.connection.rollback()
            error = "Error deleting insect"
        finally:
            cursor.close()

        return redirect(url_for("views.insects", success=message, error=error))
    else:
        return redirect(url_for("views.dashboard"))


@views.route("/insectrequest", methods=["POST", "GET"])
def insectrequest():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    if request.method == "POST" and "insectnameText" in request.form:
        user_id = request.form["useridText"]
        insect_name = request.form["insectnameText"]
        description = request.form["descriptionText"]
        insect_image = request.files["insectImage"]

        try:
            data = insect_image.read()
            render_file = render_picture(data)
            db_request_insect(user_id, insect_name, description, render_file)
            message = "Insect added succesfully"
            return render_template("insectrequest.html", success=message)

        except Exception as e:
            message = "Error adding insect"
            return render_template("insectrequest.html", error=message)

    return render_template("insectrequest.html")


@views.route("/requests")
def requests():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        return redirect(url_for("views.dashboard"))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = """
    SELECT r.request_id,
           CONCAT(u.first_name, ' ', u.last_name) AS fullname,
           r.insect_name,
           r.description,
           r.insect_image
    FROM requests r
    INNER JOIN users u ON r.id = u.id
    """

    cursor.execute(query)
    requests_data = cursor.fetchall()

    return render_template("requests.html", requests=requests_data)


@views.route("/history", methods=["POST", "GET"])
def history():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        id = int(session["id"])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query = """
            SELECT *,
                   CONCAT(u.first_name, ' ', u.last_name) AS fullname
            FROM history h
            INNER JOIN users u ON h.users_id = u.id
            WHERE h.users_id = %s
            ORDER BY h.date DESC
        """
        cursor.execute(query, (id,))
        history_data = cursor.fetchall()

        countquery = """
            SELECT insect_name, COUNT(*) AS search_count
                FROM history
                WHERE users_id = %s
                GROUP BY insect_name;
        """
        cursor.execute(countquery, (id,))
        history_count = cursor.fetchall()

        chart_data = {
            "labels": [item["insect_name"] for item in history_count],
            "data": [item["search_count"] for item in history_count],
        }

        return render_template(
            "history.html", history=history_data, chart_data=chart_data
        )
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query = """
            SELECT h.*,
                   CONCAT(u.first_name, ' ', u.last_name) AS fullname
            FROM history h
            INNER JOIN users u ON h.users_id = u.id
            ORDER BY h.date DESC
        """
        cursor.execute(query)
        history_data = cursor.fetchall()

        countquery = """
            SELECT insect_name, COUNT(*) AS search_count
                FROM history
                GROUP BY insect_name
                ORDER BY search_count DESC;
        """
        cursor.execute(countquery)
        history_count = cursor.fetchall()

        chart_data = {
            "labels": [item["insect_name"] for item in history_count],
            "data": [item["search_count"] for item in history_count],
        }

        return render_template(
            "history.html", history=history_data, chart_data=chart_data
        )

    return render_template("history.html")


@views.route("/model")
def model():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        return redirect(url_for('views.dashboard'))

    return render_template("model.html")


@views.route("/save_model", methods=["POST"])
def save_model():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        return redirect(url_for('views.dashboard'))
    message = None
    error = None
    if "model" not in request.files:
        return "No file part", 400

    file = request.files["model"]

    new_name = "best.pt"

    if file.filename == "":
        return "No selected file", 400

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], new_name)
        file.save(filepath)
        message = "File uploaded successfully"
        return redirect(url_for("views.model", success=message, error=error))

    else:
        error = "Invalid file type"
        return redirect(url_for("views.model", success=message, error=error))


@views.route("/update_bg", methods=["POST"])
def update_bg():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        return redirect(url_for('views.dashboard'))
    message = None
    error = None

    bg1 = request.files.get("bg1")
    bg2 = request.files.get("bg2")

    bg1_name = "bg1.webp"
    bg2_name = "bg2.webp"

    def optimize_and_save(image, save_path):
        try:
            with Image.open(image) as img:
                img = img.convert("RGB")
                img.save(save_path, format="WEBP", quality=80, optimize=True)
            return True
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return False

    if bg1 and bg1.filename != "":
        filepath = os.path.join(app.config["UPLOAD_FOLDER_IMAGE"], bg1_name)
        if optimize_and_save(bg1, filepath):
            message = "Background 1 updated successfully!"
        else:
            error = "Error updating Background 1."

    if bg2 and bg2.filename != "":
        filepath = os.path.join(app.config["UPLOAD_FOLDER_IMAGE"], bg2_name)
        if optimize_and_save(bg2, filepath):
            if message:
                message += " Background 2 updated successfully!"
            else:
                message = "Background 2 updated successfully!"
        else:
            error = "Error updating Background 2."

    if not (bg1 and bg1.filename) and not (bg2 and bg2.filename):
        error = "No valid file uploaded."

    return redirect(url_for("views.websettings", success=message, error=error))


@views.route("/websettings", methods=["POST", "GET"])
def websettings():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))
    if session.get("role") != "Administrator":
        return redirect(url_for('views.dashboard'))
    message = None
    error = None

    if request.method == "POST":
        q = request.form["title"]
        w = request.form["w_title"]
        e = request.form["w_subtitle"]
        r = request.form["about_us"]
        t = request.form["phone"]
        y = request.form["email"]

        try:
            update_setting(q, w, e, r, t, y)
            message = "Web settings updated succesfully"
        except Exception as e:
            error = "Error: Web Settings did not update!"

    id = "1"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM settings WHERE id = %s", (id,))
    s = cursor.fetchone()

    if s:
        title = s["website_title"]
        w_title = s["welcome_title"]
        w_subtitle = s["welcome_subtitle"]
        about_us = s["about_us"]
        phone = s["phone"]
        email = s["email"]
    else:
        title = "Rice Insect Identification"
        w_title = ""
        w_subtitle = ""
        about_us = ""
        phone = ""
        email = ""

    return render_template(
        "websettings.html",
        title=title,
        w_title=w_title,
        w_subtitle=w_subtitle,
        about_us=about_us,
        phone=phone,
        email=email,
        success=message,
        error=error,
    )


@views.route("/tutorial")
def tutorial():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    return render_template("tutorial.html")


@views.route("/user")
def users():
    if 'logged_in' not in session:
        return redirect(url_for('views.index'))
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query = """
        SELECT
            id,
            CONCAT(first_name, ' ', last_name) AS fullname,
            email,
            roles
        FROM users;
        """
        cursor.execute(query)
        users_data = cursor.fetchall()

        return render_template("users.html", usersdata=users_data)
    except Exception as e:
        return redirect(url_for("views.index"))


@views.route("/addusers", methods=["POST", "GET"])
def addusers():
    error = None
    success = None
    if request.method == "POST" and "email" in request.form:
        fname = request.form["fname"]
        mname = request.form["mname"]
        lname = request.form["lname"]
        email = request.form["email"]
        password = request.form["password"]
        role = 'Administrator'
        verified = 1

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        checkEmail = cursor.fetchone()

        if checkEmail:
            error = "Email already exists!"
        else:
            insertcursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            insertcursor.execute(
                "INSERT INTO users (first_name, middle_name, last_name, email, password, roles, email_verified) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    fname,
                    mname,
                    lname,
                    email,
                    password,
                    role,
                    verified
                ),
            )
            mysql.connection.commit()
            success = "Account created successfully!"

    return render_template("addusers.html", error=error, success=success)


@views.route("/deleteuser", methods=['GET'])
def deleteuser():
    message = None
    error = None
    if session.get("role") == "Administrator":
        id = request.args.get("id")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "DELETE FROM users WHERE id = %s"

        try:
            cursor.execute(query, (id,))
            mysql.connection.commit()
            message = "User deleted successfully."

        except Exception as e:
            mysql.connection.rollback()
            error = "Error deleting User"
        finally:
            cursor.close()
        return redirect(url_for("views.users", success=message, error=error))
    else:
        return redirect(url_for("views.dashboard"))