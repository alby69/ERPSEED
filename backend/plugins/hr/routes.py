"""
HR Plugin Routes.

API endpoints for HR operations:
- Department management
- Employee management
- Attendance tracking
- Leave requests
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

from .models import Department, Employee, Attendance, LeaveRequest

blp = Blueprint("hr", __name__, url_prefix="/hr", description="Human Resources Operations")


@blp.route("/departments")
class DepartmentList(MethodView):
    """Department endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all departments."""
        query = Department.query.filter_by(is_active=True).order_by(Department.code)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create new department."""
        data = request.get_json()
        
        existing = Department.query.filter_by(code=data['code']).first()
        if existing:
            abort(409, message=f"Department code '{data['code']}' already exists.")
        
        department = Department(
            code=data['code'],
            name=data['name'],
            parent_id=data.get('parent_id'),
            manager_id=data.get('manager_id')
        )
        
        from backend.extensions import db
        db.session.add(department)
        db.session.commit()
        
        return department, 201


@blp.route("/departments/<int:dept_id>")
class DepartmentResource(MethodView):
    """Single Department."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, dept_id):
        """Get department."""
        return Department.query.get_or_404(dept_id)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, dept_id):
        """Update department."""
        data = request.get_json()
        dept = Department.query.get_or_404(dept_id)
        
        for key, value in data.items():
            if hasattr(dept, key):
                setattr(dept, key, value)
        
        from backend.extensions import db
        db.session.commit()
        return dept
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, dept_id):
        """Deactivate department."""
        dept = Department.query.get_or_404(dept_id)
        dept.is_active = False
        
        from backend.extensions import db
        db.session.commit()
        return '', 204


@blp.route("/employees")
class EmployeeList(MethodView):
    """Employee endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List employees."""
        status = request.args.get('status')
        department_id = request.args.get('department_id')
        
        query = Employee.query
        if status:
            query = query.filter_by(status=status)
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        return query.order_by(Employee.last_name, Employee.first_name).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create new employee."""
        data = request.get_json()
        
        existing = Employee.query.filter_by(employee_number=data['employee_number']).first()
        if existing:
            abort(409, message=f"Employee number '{data['employee_number']}' already exists.")
        
        employee = Employee(
            employee_number=data['employee_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            job_title=data.get('job_title'),
            hire_date=data.get('hire_date') or datetime.date.today(),
            employee_type=data.get('employee_type', 'full-time'),
            salary=data.get('salary')
        )
        
        from backend.extensions import db
        db.session.add(employee)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_employee_created
            on_employee_created(employee)
        except Exception:
            pass
        
        return employee, 201


@blp.route("/employees/<int:emp_id>")
class EmployeeResource(MethodView):
    """Single Employee."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, emp_id):
        """Get employee."""
        return Employee.query.get_or_404(emp_id)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, emp_id):
        """Update employee."""
        data = request.get_json()
        emp = Employee.query.get_or_404(emp_id)
        
        for key, value in data.items():
            if hasattr(emp, key):
                setattr(emp, key, value)
        
        from backend.extensions import db
        db.session.commit()
        return emp
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, emp_id):
        """Terminate employee."""
        emp = Employee.query.get_or_404(emp_id)
        emp.status = 'terminated'
        emp.termination_date = datetime.date.today()
        
        from backend.extensions import db
        db.session.commit()
        return '', 204


@blp.route("/attendance")
class AttendanceList(MethodView):
    """Attendance endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List attendance records."""
        employee_id = request.args.get('employee_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Attendance.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if date_from:
            query = query.filter(Attendance.date >= date_from)
        if date_to:
            query = query.filter(Attendance.date <= date_to)
        
        return query.order_by(Attendance.date.desc()).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Record attendance."""
        data = request.get_json()
        
        attendance = Attendance(
            employee_id=data['employee_id'],
            date=data.get('date', datetime.date.today()),
            check_in=data.get('check_in'),
            check_out=data.get('check_out'),
            break_duration=data.get('break_duration', 0),
            overtime_hours=data.get('overtime_hours', 0),
            status=data.get('status', 'present'),
            notes=data.get('notes')
        )
        
        from backend.extensions import db
        db.session.add(attendance)
        db.session.commit()
        
        return attendance, 201


@blp.route("/leave")
class LeaveRequestList(MethodView):
    """Leave request endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List leave requests."""
        employee_id = request.args.get('employee_id')
        status = request.args.get('status')
        
        query = LeaveRequest.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(LeaveRequest.start_date.desc()).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Submit leave request."""
        data = request.get_json()
        
        start = data.get('start_date')
        end = data.get('end_date')
        
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        if isinstance(end, str):
            end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        
        days = (end - start).days + 1
        
        leave = LeaveRequest(
            employee_id=data['employee_id'],
            leave_type=data['leave_type'],
            start_date=start,
            end_date=end,
            days=days,
            reason=data.get('reason')
        )
        
        from backend.extensions import db
        db.session.add(leave)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_leave_requested
            on_leave_requested(leave)
        except Exception:
            pass
        
        return leave, 201


@blp.route("/leave/<int:leave_id>/approve")
class LeaveApproval(MethodView):
    """Leave approval."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, leave_id):
        """Approve or reject leave request."""
        data = request.get_json()
        
        leave = LeaveRequest.query.get_or_404(leave_id)
        
        if leave.status != 'pending':
            abort(400, message="Only pending requests can be approved/rejected.")
        
        leave.status = data.get('status', 'approved')
        leave.approved_by = get_jwt_identity()
        leave.approved_at = datetime.datetime.utcnow()
        
        from backend.extensions import db
        db.session.commit()
        
        if leave.status == 'approved':
            try:
                from backend.webhook_triggers import on_leave_approved
                on_leave_approved(leave)
            except Exception:
                pass
        
        return leave


@blp.route("/reports/attendance-summary")
class AttendanceSummary(MethodView):
    """Attendance reports."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get attendance summary."""
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if not date_from:
            date_from = datetime.date.today().replace(day=1)
        if not date_to:
            date_to = datetime.date.today()
        
        employees = Employee.query.filter_by(status='active').all()
        
        from backend.extensions import db
        from sqlalchemy import func
        
        result = []
        for emp in employees:
            stats = db.session.query(
                func.count(Attendance.id),
                func.sum(Attendance.overtime_hours)
            ).filter(
                Attendance.employee_id == emp.id,
                Attendance.date >= date_from,
                Attendance.date <= date_to
            ).scalar()
            
            result.append({
                'employee': emp.full_name,
                'employee_number': emp.employee_number,
                'days_present': stats[0] or 0,
                'overtime_hours': stats[1] or 0
            })
        
        return result
