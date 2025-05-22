import os
import io
import MySQLdb
import uuid
import torch
import base64
from flask import Flask, Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from PIL import Image
from database import MySQL
from ultralytics import YOLO
from datetime import datetime
import pytz

app = Flask(__name__)
mysql = MySQL(app)

ai = Blueprint("ai", __name__)


best_model_path = "website/models/best.pt"
fallback_model_path = "website/models/v3.pt"

if os.path.exists(best_model_path):
    model = YOLO(best_model_path)
else:
    model = YOLO(fallback_model_path)

torch.set_num_threads(1)


def render_picture(data):
    return base64.b64encode(data).decode("ascii")


def add_history(user, name, image):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "INSERT INTO history (users_id, insect_name, insect_image, date) VALUES (%s, %s, %s, %s)"

    philippine_timezone = pytz.timezone("Asia/Manila")
    today = datetime.now(philippine_timezone)
    formatted_datetime = today.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(query, (user, name, image, formatted_datetime))
    mysql.connection.commit()


def fetch_pictures(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM insect_picture WHERE insect_id = %s LIMIT 5"
    cursor.execute(query, (id,))
    insects_pictures = cursor.fetchall()
    return insects_pictures


def generate_thumbnail(image_path, size=(100, 100)):
    with Image.open(image_path) as img:
        img.thumbnail(size)
        orig_format = img.format
        buffer = io.BytesIO()
        img.save(buffer, format=orig_format)
        return base64.b64encode(buffer.getvalue()).decode()


def load_class_names(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]


# Route to handle image upload and classification
@ai.route("/upload", methods=["POST"])
def upload():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    try:

        # Get the uploaded image file
        image_file = request.files.get("file")
        users_id = request.form.get("userId")

        if not image_file:
            return jsonify({"error": "No image file uploaded"}), 400

        # Save the image file
        unique_filename = str(uuid.uuid4()) + \
            os.path.splitext(image_file.filename)[1]
        file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], unique_filename)
        image_file.save(file_path)

        relative_path = file_path.replace("website/", "", 1)

        insect_names = [class_name.title()
                        for idx, class_name in model.names.items()]

        device = torch.device('cpu')
        results = model(file_path, verbose=False, device=device)

        probs = results[0].probs.data.tolist()
        confidence_threshold = 0.90
        filtered_results = [
            (insect_names[name], prob)
            for name, prob in zip(results[0].names, probs)
            if prob > confidence_threshold
        ]

        # Get the predicted insect name
        predicted_insect_name = (
            filtered_results[0][0] if filtered_results else "No insect detected"
        )

        thumbnail_image = generate_thumbnail(file_path)
        if not thumbnail_image:
            return jsonify({"error": "Failed to generate thumbnail"}), 500

        add_history(users_id, predicted_insect_name, thumbnail_image)

        # return jsonify({"image": relative_path, "insect_name": predicted_insect_name})
        return redirect(url_for("ai.result", image=relative_path, insect_name=predicted_insect_name))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to render the result.html page
@ai.route("/result")
def result():
    if 'logged_in' not in session:
        return redirect(url_for('views.login'))

    insect_pic = request.args.get("image")
    insect_name = request.args.get("insect_name")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM insects WHERE insect_name = %s", (insect_name,))
    insect = cursor.fetchone()

    if insect:
        i_name = insect["insect_name"]
        i_title1 = insect["insect_title1"]
        i_desc = insect["insect_description"]
        i_title2 = insect["insect_title2"]
        i_treatment = insect["insect_treatment"]
        i_image = insect["insect_image"]
        i_id = insect["insect_id"]

        pictures = fetch_pictures(i_id)

    else:
        i_name = "Insect not found on the database"
        i_title1 = "Description"
        i_desc = "No details available. Please contact the administrator if this insect affects rice."
        i_title2 = "Treatment"
        i_treatment = "..."
        i_image = None
        pictures = None

    return render_template(
        "result.html",
        image=insect_pic,
        ins_name=insect_name,
        ins_t1=i_title1,
        ins_desc=i_desc,
        ins_t2=i_title2,
        ins_treat=i_treatment,
        ins_image=i_image,
        pictures=pictures,
    )
