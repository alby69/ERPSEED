"""
HR Plugin Models.

Human Resources functionality:
- Employees
- Departments
- Attendance
- Leave Management
- Payroll
- Training & Skills
"""
from datetime import datetime, date
from backend.extensions import db


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

    parent = db.relationship('Department', remote_side=lambda: [Department.id], backref='children')
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


# ──────────────────────────────────────────────
# Payroll
# ──────────────────────────────────────────────

class PayrollPeriod(db.Model):
    __tablename__ = 'hr_payroll_periods'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('year', 'month', name='uq_payroll_period'),
    )

    def __repr__(self):
        return f'<PayrollPeriod {self.code}>'


class Payslip(db.Model):
    __tablename__ = 'hr_payslips'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('hr_payroll_periods.id'), nullable=False)
    payslip_number = db.Column(db.String(50), nullable=False, index=True)
    gross_pay = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_pay = db.Column(db.Float, default=0.0)
    taxes = db.Column(db.Float, default=0.0)
    employer_contributions = db.Column(db.Float, default=0.0)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', backref='payslips')
    period = db.relationship('PayrollPeriod', backref='payslips')
    lines = db.relationship('PayslipLine', back_populates='payslip', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Payslip {self.payslip_number}>'


class PayslipLine(db.Model):
    __tablename__ = 'hr_payslip_lines'

    id = db.Column(db.Integer, primary_key=True)
    payslip_id = db.Column(db.Integer, db.ForeignKey('hr_payslips.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, default=0.0)

    payslip = db.relationship('Payslip', back_populates='lines')

    def __repr__(self):
        return f'<PayslipLine {self.description}: {self.amount}>'


# ──────────────────────────────────────────────
# Training & Skills
# ──────────────────────────────────────────────

class Course(db.Model):
    __tablename__ = 'hr_courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    provider = db.Column(db.String(200))
    duration_hours = db.Column(db.Float)
    cost = db.Column(db.Float)
    category = db.Column(db.String(50))
    is_mandatory = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    records = db.relationship('TrainingRecord', back_populates='course', lazy='dynamic')

    def __repr__(self):
        return f'<Course {self.code}: {self.title}>'


class TrainingRecord(db.Model):
    __tablename__ = 'hr_training_records'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('hr_courses.id'), nullable=False)
    completion_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    score = db.Column(db.Float)
    result = db.Column(db.String(20), default='passed')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='training_records')
    course = db.relationship('Course', back_populates='records')

    def __repr__(self):
        return f'<TrainingRecord emp={self.employee_id} course={self.course_id}>'


class Certification(db.Model):
    __tablename__ = 'hr_certifications'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200))
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    certificate_number = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='certifications')

    def __repr__(self):
        return f'<Certification {self.name} emp={self.employee_id}>'


class Skill(db.Model):
    __tablename__ = 'hr_skills'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.code}: {self.name}>'


class SkillMatrix(db.Model):
    __tablename__ = 'hr_skill_matrix'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hr_employees.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('hr_skills.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    years_experience = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', backref='skills')
    skill = db.relationship('Skill')
    verifier = db.relationship('User', foreign_keys=[verified_by])

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'skill_id', name='uq_employee_skill'),
    )

    def __repr__(self):
        return f'<SkillMatrix emp={self.employee_id} skill={self.skill_id} level={self.level}>'
