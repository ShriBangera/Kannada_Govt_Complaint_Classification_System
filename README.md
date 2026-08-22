# Janadhwani Spandhana

## 📌 Overview

The **Janadhwani Spandhana** is a web-based application designed to simplify the process of submitting, classifying, assigning, and tracking citizen complaints.

The system uses **Natural Language Processing (NLP)** and **Machine Learning** to automatically classify Kannada complaints into the appropriate government department. The predicted department is then stored in a MySQL database and the complaint can be assigned to an employee for further action.

The system provides separate interfaces for **citizens** and **government employees**, making complaint management more organized, transparent, and efficient.

---

## 🎯 Objectives

* Allow citizens to submit complaints in Kannada.
* Automatically classify complaints into the appropriate department.
* Reduce manual complaint categorization.
* Store complaint information securely in a database.
* Automatically assign complaints to employees belonging to the predicted department.
* Allow employees to update complaint status and remarks.
* Allow citizens to track the status of their submitted complaints.
* Provide a simple and user-friendly complaint management interface.

---

## ✨ Key Features

### 👤 Citizen Module

* Citizen registration
* Citizen login
* Kannada complaint submission
* Automatic complaint classification
* Complaint ID generation
* View submitted complaints
* View predicted department
* Track complaint status
* View employee remarks
* Citizen logout

The citizen portal allows users to submit complaints and view their complaint history and status.

### 👨‍💼 Employee Module

* Employee registration
* Employee login
* Department-based complaint viewing
* View complaint details
* Update complaint status
* Add remarks
* Manage complaints assigned to the department

Employees can work with statuses such as **Pending, Accepted, In Progress, Resolved, and Rejected**.

### 🤖 Machine Learning Module

The classification engine uses:

* **TF-IDF Vectorization**
* **Character-level n-grams**
* **Logistic Regression**

The model uses character-level TF-IDF with an n-gram range of `(1, 2)`, which is useful for handling variations in Kannada text.

### 🗄️ Database Module

The application uses **MySQL** to store:

* Citizen information
* Employee information
* Department information
* Complaint information
* Complaint status
* Complaint remarks
* Employee assignments
* Complaint update history

The database automatically creates the required tables when the backend starts.

---

## 🏛️ Complaint Categories

The machine-learning classifier handles the following complaint categories:

| Category      | Department            |
| ------------- | --------------------- |
| 💧 Water      | Water Department      |
| ⚡ Electricity | Electricity Board     |
| 🛣️ Road      | Road Department       |
| 🏥 Health     | Health Department     |
| 👮 Police     | Police Department     |
| 🎓 Education  | Education Department  |
| 🧹 Sanitation | Sanitation Department |
| 🚌 Transport  | Transport Department  |

---

## 🔄 System Workflow

```text
Citizen
   │
   ▼
Register / Login
   │
   ▼
Submit Kannada Complaint
   │
   ▼
Flask Backend
   │
   ▼
TF-IDF Vectorization
   │
   ▼
Logistic Regression Model
   │
   ▼
Department Prediction
   │
   ▼
Complaint Stored in MySQL
   │
   ▼
Employee Assigned
   │
   ▼
Employee Reviews Complaint
   │
   ├── Accept
   ├── In Progress
   ├── Resolve
   └── Reject
   │
   ▼
Citizen Tracks Status
```

The backend transforms the submitted complaint using the saved vectorizer, predicts the category, calculates a confidence value, stores the complaint, and attempts to assign an employee from the predicted department.

---

## 🧠 Machine Learning Approach

### 1. Data Loading

The complaint dataset is loaded from `data.csv`.

### 2. Data Cleaning

Duplicate records and invalid rows are removed before training.

```python
data = data.drop_duplicates()
data = data[data['text'] != 'text']
```

Additional filtering is performed to remove confusing samples containing strong category-specific keywords.

### 3. TF-IDF Feature Extraction

The complaint text is converted into numerical features using **TF-IDF**.

Character-level analysis is used:

```python
TfidfVectorizer(
    ngram_range=(1,2),
    analyzer='char'
)
```

Character-level features help the model learn patterns within Kannada words and text variations.

### 4. Logistic Regression

The extracted TF-IDF features are provided to a **Logistic Regression** classifier.

```python
model = LogisticRegression(max_iter=2000)
model.fit(X_vec, y)
```

### 5. Model Saving

The trained model and vectorizer are saved using Python's `pickle` module.

```text
model.pkl
vectorizer.pkl
```

These saved files are loaded by the prediction system when the Flask application starts.

---

## 📊 Model Evaluation

The project includes a confusion matrix to evaluate classification performance.

The displayed confusion matrix contains **93 test samples**, with **91 correctly classified samples**, giving an accuracy of approximately:

### **97.85%**

```text
Correct predictions = 91
Total test samples  = 93

Accuracy = 91 / 93 × 100
         ≈ 97.85%
```

The confusion matrix shows that most predictions fall along the diagonal, indicating strong classification performance across the complaint categories.

The evaluation script uses an **80/20 train-test split**, `random_state=42`, and stratification by category.

---

## 🖥️ Application Architecture

```text
                    ┌──────────────────────┐
                    │      Citizen UI      │
                    │  Kannada Complaint   │
                    │      Portal          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Backend     │
                    │       REST API       │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Machine Learning│          │      MySQL      │
       │ TF-IDF +        │          │    Database     │
       │ Logistic Reg.   │          │                 │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └────────────┬───────────────┘
                             ▼
                  ┌──────────────────────┐
                  │ Employee Dashboard   │
                  │ Complaint Management  │
                  └──────────────────────┘
```

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Kannada Unicode interface

### Backend

* Python
* Flask
* Flask-CORS
* REST API

### Machine Learning

* Scikit-learn
* TF-IDF Vectorizer
* Logistic Regression
* Pickle

### Database

* MySQL
* MySQL Connector/Python

### Data Processing

* Pandas
* CSV dataset

---

## 📁 Project Structure

```text
Kannada-Government-Complaint-System/
│
├── app.py
├── database.py
├── model.py
├── predict.py
├── duplicate.py
├── confusion_matrix.py
├── install_deps.py
│
├── model.pkl
├── vectorizer.pkl
├── data.csv
│
├── index.html
├── login.html
├── register.html
├── employee_dashboard.html
│
├── dashboard.html
│
├── bg.png
├── bg2.png
├── confusion_matrix.png
│
└── README.md
```

---

## ⚙️ Requirements

Make sure the following are installed:

* Python 3.x
* MySQL Server
* MySQL Workbench (optional)
* Web browser

Required Python packages:

```bash
pip install flask flask-cors pandas scikit-learn mysql-connector-python
```

The project also contains an installation script for the MySQL connector.

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/kannada-government-complaint-system.git
cd kannada-government-complaint-system
```

### Step 2: Install Dependencies

```bash
pip install flask flask-cors pandas scikit-learn mysql-connector-python
```

### Step 3: Configure MySQL

Make sure MySQL Server is running.

The application uses the database:

```text
kannada_complaints
```

The database configuration is defined in `database.py`.

Update the following values according to your MySQL setup:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'kannada_complaints'
}
```

The application creates the database and required tables automatically through `create_tables()`.

> **Security Note:** Do not commit real database passwords to GitHub. Use environment variables for production deployments.

### Step 4: Start the Backend

```bash
python app.py
```

The Flask backend runs at:

```text
http://127.0.0.1:5000
```

### Step 5: Open the Frontend

Open:

```text
login.html
```

in a web browser.

From the login page, citizens can register/login, while employees can access the employee login interface.

---

## 🔌 Important API Endpoints

| Method | Endpoint                              | Purpose                         |
| ------ | ------------------------------------- | ------------------------------- |
| POST   | `/predict`                            | Classify and submit a complaint |
| POST   | `/citizen/register`                   | Register citizen                |
| POST   | `/citizen/login`                      | Citizen login                   |
| GET    | `/citizen/<id>/complaints`            | Get citizen complaints          |
| POST   | `/employee/register`                  | Register employee               |
| POST   | `/employee/login`                     | Employee login                  |
| GET    | `/employee/<id>/complaints`           | Get employee complaints         |
| GET    | `/department-complaints/<department>` | Get department complaints       |
| POST   | `/complaint/<id>/action`              | Perform complaint action        |
| POST   | `/update-status`                      | Update complaint status         |
| GET    | `/track/<id>`                         | Track complaint                 |

The Flask backend exposes separate citizen and employee routes along with complaint prediction, tracking, assignment, and status-management endpoints.

---

## 📝 Example Complaint

### Kannada Input

```text
ನಮ್ಮ ಪ್ರದೇಶದಲ್ಲಿ ನೀರು ಸರಿಯಾಗಿ ಬರುತ್ತಿಲ್ಲ.
```

### Processing

```text
Kannada Complaint
       ↓
TF-IDF Vectorization
       ↓
Logistic Regression
       ↓
Water
       ↓
Water Department
       ↓
Complaint Stored
       ↓
Employee Assignment
```

The standalone prediction script loads the saved model and vectorizer and transforms the input before making the prediction.

---

## 📋 Complaint Status Flow

```text
Pending
   ↓
Accepted
   ↓
In Progress
   ↓
Resolved
```

A complaint may also be marked as:

```text
Rejected
```

Employees can update the status and add remarks from the employee dashboard.

---

## 🔐 User Roles

### Citizen

Citizens can:

* Create an account
* Login
* Submit complaints
* View complaint history
* Track complaint status
* View remarks

### Employee

Employees can:

* Register
* Login
* View department complaints
* Update complaint status
* Add remarks
* Manage assigned complaints

---

## 📈 Advantages

* Supports complaints written in Kannada.
* Automates department classification.
* Reduces manual sorting of complaints.
* Provides centralized complaint storage.
* Enables department-wise complaint management.
* Allows citizens to track complaint progress.
* Provides confidence scores from the classification model.
* Maintains complaint update history.
* Provides separate citizen and employee interfaces.

---

## 🔮 Future Enhancements

* Improve the dataset with more real-world Kannada complaints.
* Add support for Kannada spelling variations and colloquial language.
* Improve model performance with additional NLP techniques.
* Add multilingual complaint support.
* Add administrator dashboard and analytics.
* Add email/SMS notifications.
* Implement secure password hashing.
* Add authentication tokens and role-based authorization.
* Deploy the application to a cloud server.
* Add complaint priority and urgency detection.
* Add graphical reports for department-wise complaints.
* Add mobile application support.

---

## 👩‍💻 Project Purpose

This project demonstrates the application of **Natural Language Processing, Machine Learning, Web Development, REST APIs, and Database Management** to solve a real-world public-service problem.

The main goal is to make the grievance-management process more **transparent, efficient, responsive, and citizen-friendly**, particularly for Kannada-speaking users.

---

## 📜 License

This project is developed for **academic and educational purposes**.

---

## ⭐ Acknowledgement

Developed as an academic project focusing on **Kannada NLP, Machine Learning, and Government Complaint Management**.
