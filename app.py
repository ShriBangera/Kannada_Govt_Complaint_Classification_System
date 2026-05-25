
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

# DB helpers
from database import insert_complaint, find_employee_for_department, assign_complaint, create_tables
from database import get_employee_by_credentials, get_employee_by_email, register_employee, get_employee_by_id, get_complaint_by_id, get_complaints_for_department, update_complaint_status, add_complaint_update

app = Flask(__name__)
CORS(app)

# Load model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

@app.route('/')
def home():
    return "🚀 Complaint Classification API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data['text']

        vec = vectorizer.transform([text])
        category = model.predict(vec)[0]
        confidence = model.predict_proba(vec).max()

        # Map model category to department name
        department_map = {
            "water": "Water Department",
            "road": "Road Department",
            "electricity": "Electricity Board",
            "health": "Health Department",
            "police": "Police Department",
        }

        predicted_department = department_map.get(category, category)

        # Save to DB
        complaint_id = insert_complaint(text, predicted_department, float(confidence))

        assigned_employee = None
        if complaint_id:
            # Try to find an employee and assign
            emp = find_employee_for_department(predicted_department)
            if emp and emp.get('id'):
                success = assign_complaint(complaint_id, emp.get('id'))
                if success:
                    assigned_employee = {k: emp.get(k) for k in ('id', 'name', 'email', 'department')}

        response = {
            "input": text,
            "category": category,
            "confidence": round(float(confidence) * 100, 2),
            "predicted_department": predicted_department,
            "complaint_id": complaint_id,
            "assigned_employee": assigned_employee
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/employee/register', methods=['POST'])
def employee_register():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data or 'department' not in data:
        return jsonify({'error': 'Missing registration fields: name, email, password, department'}), 400

    email = data['email']
    if get_employee_by_email(email):
        return jsonify({'error': 'Employee already registered'}), 409

    success = register_employee(
        data['name'],
        data['email'],
        data['password'],
        data['department'],
        data.get('role', 'staff')
    )
    if not success:
        return jsonify({'error': 'Unable to register employee'}), 500

    return jsonify({'message': 'Employee registered successfully'}), 201


@app.route('/employee/login', methods=['POST'])
def employee_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': "Missing credentials"}), 400

    emp = get_employee_by_credentials(data['email'], data['password'])
    if not emp:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Return basic employee info (client will include employee id in actions)
    return jsonify({
        'id': emp['id'],
        'name': emp['name'],
        'email': emp['email'],
        'department': emp.get('department')
    })


@app.route('/employee/<int:emp_id>/complaints', methods=['GET'])
def employee_complaints(emp_id):
    status = request.args.get('status')
    emp = get_employee_by_id(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404

    complaints = get_complaints_for_department(emp.get('department'), status=status)
    return jsonify({'complaints': complaints})


@app.route('/complaint/<int:complaint_id>/action', methods=['POST'])
def complaint_action(complaint_id):
    data = request.get_json()
    if not data or 'action' not in data or 'employee_id' not in data:
        return jsonify({'error': 'Missing action or employee_id'}), 400

    action = data['action']
    emp_id = data['employee_id']
    remarks = data.get('remarks')

    if action == 'accept':
        assigned = assign_complaint(complaint_id, emp_id)
        if not assigned:
            return jsonify({'error': 'Could not accept complaint'}), 500
        status = 'Accepted'
    elif action == 'start':
        status = 'In Progress'
        success = update_complaint_status(complaint_id, status, employee_id=emp_id)
        if not success:
            return jsonify({'error': 'Could not update complaint status'}), 500
    elif action == 'resolve':
        status = 'Resolved'
        success = update_complaint_status(complaint_id, status, employee_id=emp_id, remarks=remarks)
        if not success:
            return jsonify({'error': 'Could not resolve complaint'}), 500
    elif action == 'reject':
        status = 'Rejected'
        success = update_complaint_status(complaint_id, status, employee_id=emp_id, remarks=remarks)
        if not success:
            return jsonify({'error': 'Could not reject complaint'}), 500
    else:
        return jsonify({'error': 'Unknown action'}), 400

    add_complaint_update(complaint_id, emp_id, status, remarks)
    return jsonify({'ok': True, 'status': status})


@app.route('/department-complaints/<department>', methods=['GET'])
def department_complaints(department):
    complaints = get_complaints_for_department(department)
    return jsonify(complaints)


@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    if not data or 'complaint_id' not in data or 'status' not in data:
        return jsonify({'error': 'Missing complaint_id or status'}), 400

    complaint_id = data['complaint_id']
    status = data['status']
    remarks = data.get('remarks')
    employee_id = data.get('employee_id')

    allowed_statuses = ['Pending', 'Accepted', 'In Progress', 'Resolved', 'Rejected']
    if status not in allowed_statuses:
        return jsonify({'error': 'Invalid status value'}), 400

    success = update_complaint_status(complaint_id, status, employee_id=employee_id, remarks=remarks)
    if not success:
        return jsonify({'error': 'Unable to update complaint status'}), 500

    add_complaint_update(complaint_id, employee_id, status, remarks)
    return jsonify({'message': 'Complaint updated successfully'})


@app.route('/track/<int:complaint_id>', methods=['GET'])
def track_complaint(complaint_id):
    emp = get_complaint_by_id(complaint_id)
    if not emp:
        return jsonify({'error': 'Complaint not found'}), 404
    return jsonify({
        'id': emp['id'],
        'status': emp['status'],
        'remarks': emp.get('remarks'),
        'assigned_employee_id': emp.get('assigned_employee_id'),
        'predicted_department': emp.get('predicted_department'),
        'updated_at': emp.get('updated_at')
    })


# Run app
if __name__ == '__main__':
    app.run(debug=True)
