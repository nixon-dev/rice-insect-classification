# 🦗 Rice Insect Classification System

A Flask web application for insect image classification using a YOLOv11-trained model. Displays insect name, description, and treatment recommendations.

> 🚀 This was a college learning project to understand Image Classification A.I and deepen my knowledge of web development using Flask Framework, Python, YoloV11 and MySQL.

---

## 📌 Features

- 💡 YoloV11 for Image Classification Model
- 📊 Interactive data tables using DataTables
- 📈 Visual reports using Chart.js
- 🔐 Admin and User authentication system
- 🛠 Admin dashboard for managing information of insects
- 🧑🏼‍🦰Users dashboard for identifying insect image and see their insect identification history.

---

## 🧰 Tech Stack

- **Backend:** Python (Flask Framework)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Machine Learning & Computer Vision**
  - [YoloV11](https://docs.ultralytics.com/models/yolo11/) – for model training
  - torch, torchvision - for deep learning model execution
  - opencv-python - for image handling and  processing
- **Libraries & APIs:**
  - [DataTables](https://datatables.net/) – for enhanced table functionality
  - [Chart.js](https://www.chartjs.org/) – for graphical data representation


## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/water-billing-automation.git
2. **Install requirements.txt**
3. **After importing MySQL DB, change credentials in database/__init__.py**
  ```python
        # Define MySQL configuration
        app.secret_key = 'nickson'
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'riceinsect_db'
  ```
 4. **Run flask server**
