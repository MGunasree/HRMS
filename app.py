from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date_of_joining = db.Column(db.Date, nullable=False)

# Attendance Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)

# Create Database Tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

# Add New Employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    new_employee = Employee(
        name=data['name'],
        designation=data['designation'],
        department=data['department'],
        date_of_joining=datetime.strptime(data['date_of_joining'], '%Y-%m-%d').date()
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'New employee added successfully!'}), 201

# Get Employees
@app.route('/employees', methods=['GET'])
def get_employees():
    name = request.args.get('name')
    if name:
        employees = Employee.query.filter(Employee.name.ilike(f'%{name}%')).all()
    else:
        employees = Employee.query.all()

    employee_list = [{'id': emp.id, 'name': emp.name, 'designation': emp.designation,
                      'department': emp.department, 'date_of_joining': emp.date_of_joining} for emp in employees]
    return jsonify(employee_list), 200

# Mark Attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    new_attendance = Attendance(
        employee_id=data['employee_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        status=data['status']
    )
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance marked successfully!', 'employee_id': data['employee_id']}), 201

# Get Attendance
@app.route('/attendance/<int:employee_id>', methods=['GET'])
def get_attendance(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    attendance_records = Attendance.query.filter_by(employee_id=employee_id).all()
    attendance_list = [{'date': record.date, 'status': record.status} for record in attendance_records]

    return jsonify({
        'employee': {'id': employee.id, 'name': employee.name, 'designation': employee.designation},
        'attendance': attendance_list
    }), 200

# Load Department Report
@app.route('/department_report', methods=['GET'])
def department_report():
    report = db.session.query(Employee.department, db.func.count(Employee.id)).group_by(Employee.department).all()
    report_dict = {dept: count for dept, count in report}
    return jsonify(report_dict), 200

if __name__ == '__main__':
    app.run(debug=True)
