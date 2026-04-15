"""
HR Plugin Models.

Human Resources functionality:
- Employees
- Departments
- Attendance
- Leave Management
"""
from datetime import datetime
from extensions import db


class Department(db.Model):
    """Department/Team."""
    __tablename__ = 'hr_departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('hr_departments.id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('Department', remote_side=[id], backref='children')
    employees = db.relationship('Employee', back_populates='department', lazy='dynamic', foreign_keys='Employee.department_id')
    manager = db.relationship('Employee', foreign_keys=[manager_id])

    def __repr__(self):
        return f'<Department {self.code}: {self.name}>'


class Employee(db.Model):
    """Employee records."""
    __tablename__ = 'hr_employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    department_id = db.Column(db.Integer, db.ForeignKey('hr_departments.id'))
    job_title = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    employee_type = db.Column(db.String(20), default='full-time')  # full-time, part-time, contractor
    salary = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = db.relationship('Department', back_populates='employees', foreign_keys=[department_id])
    user = db.relationship('User')
    attendances = db.relationship('Attendance', back_populates='employee', lazy='dynamic')
    leave_requests = db.relationship('LeaveRequest', back_populates='employee', lazy='dynamic')

    def __repr__(self):
        return f'<Employee {self.employee_number}: {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(db.Model):
    """Daily attendance tracking."""
    __tablename__ = 'hr_attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    break_duration = db.Column(db.Integer, default=0)  # minutes
    overtime_hours = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='present')  # present, absent, late, leave
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='attendances')

    def __repr__(self):
        return f'<Attendance {self.employee_id} - {self.date}>'

    @property
    def work_hours(self):
        if self.check_in and self.check_out:
            from datetime import datetime, timedelta
            if isinstance(self.check_in, datetime):
                check_in = self.check_in.time()
            else:
                check_in = self.check_in
            if isinstance(self.check_out, datetime):
                check_out = self.check_out.time()
            else:
                check_out = self.check_out

            diff = datetime.combine(datetime.today(), check_out) - datetime.combine(datetime.today(), check_in)
            hours = diff.total_seconds() / 3600 - (self.break_duration / 60)
            return max(0, hours)
        return 0


class LeaveRequest(db.Model):
    """Leave/Time-off requests."""
    __tablename__ = 'hr_leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    leave_type = db.Column(db.String(30), nullable=False)  # vacation, sick, personal, maternity, paternity
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='leave_requests')
    approver = db.relationship('User')

    def __repr__(self):
        return f'<LeaveRequest {self.employee_id}: {self.leave_type} {self.start_date}>'
