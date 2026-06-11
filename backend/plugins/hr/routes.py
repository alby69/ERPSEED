"""
HR Plugin Routes.

API endpoints for HR operations:
- Department management
- Employee management
- Attendance tracking
- Leave requests
- Payroll
- Training & Skills
"""
from flask.views import MethodView
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

from .models import Department, Employee, Attendance, LeaveRequest
from .models import PayrollPeriod, Payslip, PayslipLine, Course, TrainingRecord, Certification, Skill, SkillMatrix


def _to_dict(obj):
    """Convert a SQLAlchemy model to a dict."""
    if obj is None:
        return None
    cols = [c.name for c in obj.__table__.columns]
    d = {}
    for c in cols:
        val = getattr(obj, c)
        if isinstance(val, (datetime.date, datetime.datetime)):
            val = val.isoformat()
        d[c] = val
    # Include relationships for detail endpoints
    if hasattr(obj, 'lines') and obj.lines:
        d['lines'] = [
            {c.name: getattr(l, c.name) if not isinstance(getattr(l, c.name), (datetime.date, datetime.datetime))
             else getattr(l, c.name).isoformat()
             for c in l.__table__.columns}
            for l in obj.lines
        ]
    return d


def _parse_date(val):
    """Parse a date from string or return as-is if already a date."""
    if val is None:
        return None
    if isinstance(val, datetime.date):
        return val
    if isinstance(val, str):
        try:
            return datetime.datetime.strptime(val, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
    return None


blp = Blueprint("hr", __name__, description="Human Resources Operations")


@blp.route("/departments")
class DepartmentList(MethodView):
    """Department endpoints."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all departments."""
        query = Department.query.filter_by(is_active=True).order_by(Department.code)
        return jsonify([_to_dict(d) for d in query.all()])

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

        return jsonify(_to_dict(department)), 201



@blp.route("/departments/<int:dept_id>")
class DepartmentResource(MethodView):
    """Single Department."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, dept_id):
        """Get department."""
        return jsonify(_to_dict(Department.query.get_or_404(dept_id)))

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
        return jsonify(_to_dict(dept))

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

        return jsonify([_to_dict(e) for e in query.order_by(Employee.last_name, Employee.first_name).all()])

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
            hire_date=_parse_date(data.get('hire_date')) or datetime.date.today(),
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

        return jsonify(_to_dict(employee)), 201


@blp.route("/employees/<int:emp_id>")
class EmployeeResource(MethodView):
    """Single Employee."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, emp_id):
        """Get employee."""
        return jsonify(_to_dict(Employee.query.get_or_404(emp_id)))

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
        return jsonify(_to_dict(emp))

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

        return jsonify([_to_dict(a) for a in query.order_by(Attendance.date.desc()).all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Record attendance."""
        data = request.get_json()

        attendance = Attendance(
            employee_id=data['employee_id'],
            date=_parse_date(data.get('date')) or datetime.date.today(),
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

        return jsonify(_to_dict(attendance)), 201


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

        return jsonify([_to_dict(l) for l in query.order_by(LeaveRequest.start_date.desc()).all()])

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

        return jsonify(_to_dict(leave)), 201


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

        return jsonify(_to_dict(leave))


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


# ═══════════════════════════════════════════════
# Payroll
# ═══════════════════════════════════════════════

@blp.route("/payroll-periods")
class PayrollPeriodList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        year = request.args.get('year', type=int)
        status = request.args.get('status')
        q = PayrollPeriod.query.order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
        if year:
            q = q.filter_by(year=year)
        if status:
            q = q.filter_by(status=status)
        return jsonify([_to_dict(p) for p in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('year') or not data.get('month'):
            abort(400, message='year and month are required')
        existing = PayrollPeriod.query.filter_by(year=data['year'], month=data['month']).first()
        if existing:
            abort(409, message='Payroll period already exists')
        from backend.extensions import db
        period = PayrollPeriod(
            code=f"{data['year']}-{data['month']:02d}",
            name=data.get('name', f"Mese {data['month']} {data['year']}"),
            year=data['year'],
            month=data['month'],
            start_date=datetime.date(data['year'], data['month'], 1),
            end_date=datetime.date(data['year'], data['month'], 28),
        )
        db.session.add(period)
        db.session.commit()
        return jsonify(_to_dict(period)), 201


@blp.route("/payroll-periods/<int:period_id>/close")
class PayrollPeriodClose(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, period_id):
        period = PayrollPeriod.query.get_or_404(period_id)
        if period.status != 'open':
            abort(400, message='Period already closed')
        period.status = 'closed'
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(period))


@blp.route("/payslips")
class PayslipList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        employee_id = request.args.get('employee_id', type=int)
        period_id = request.args.get('period_id', type=int)
        q = Payslip.query.order_by(Payslip.payslip_number.desc())
        if employee_id:
            q = q.filter_by(employee_id=employee_id)
        if period_id:
            q = q.filter_by(period_id=period_id)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('employee_id') or not data.get('period_id'):
            abort(400, message='employee_id and period_id are required')
        existing = Payslip.query.filter_by(
            employee_id=data['employee_id'], period_id=data['period_id']
        ).first()
        if existing:
            abort(409, message='Payslip already exists for this employee and period')
        from backend.extensions import db
        last = Payslip.query.order_by(Payslip.payslip_number.desc()).first()
        next_num = 1
        if last:
            try:
                next_num = int(last.payslip_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                pass
        payslip = Payslip(
            employee_id=data['employee_id'],
            period_id=data['period_id'],
            payslip_number=f"PS-{datetime.date.today().year}-{next_num:05d}",
            gross_pay=float(data.get('gross_pay', 0)),
            deductions=float(data.get('deductions', 0)),
            net_pay=float(data.get('net_pay', 0)),
            taxes=float(data.get('taxes', 0)),
            employer_contributions=float(data.get('employer_contributions', 0)),
            payment_date=datetime.datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else None,
            status='draft',
            notes=data.get('notes'),
        )
        db.session.add(payslip)
        db.session.flush()
        for line_data in data.get('lines', []):
            line = PayslipLine(
                payslip_id=payslip.id,
                description=line_data['description'],
                type=line_data['type'],
                amount=float(line_data['amount']),
            )
            db.session.add(line)
        db.session.commit()
        return jsonify(_to_dict(payslip)), 201


@blp.route("/payslips/<int:payslip_id>")
class PayslipResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, payslip_id):
        return jsonify(_to_dict(Payslip.query.get_or_404(payslip_id)))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, payslip_id):
        payslip = Payslip.query.get_or_404(payslip_id)
        if payslip.status != 'draft':
            abort(400, message='Cannot modify a payslip that is not in draft status')
        data = request.get_json() or {}
        for field in ('gross_pay', 'deductions', 'net_pay', 'taxes', 'employer_contributions', 'notes'):
            if field in data:
                setattr(payslip, field, float(data[field]) if field != 'notes' else data[field])
        if 'payment_date' in data:
            payslip.payment_date = datetime.datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
        if 'lines' in data:
            PayslipLine.query.filter_by(payslip_id=payslip.id).delete()
            for line_data in data['lines']:
                line = PayslipLine(
                    payslip_id=payslip.id,
                    description=line_data['description'],
                    type=line_data['type'],
                    amount=float(line_data['amount']),
                )
                from backend.extensions import db
                db.session.add(line)
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(payslip))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, payslip_id):
        payslip = Payslip.query.get_or_404(payslip_id)
        if payslip.status != 'draft':
            abort(400, message='Cannot delete a payslip that is not in draft status')
        from backend.extensions import db
        db.session.delete(payslip)
        db.session.commit()
        return '', 204


@blp.route("/payslips/<int:payslip_id>/approve")
class PayslipApprove(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, payslip_id):
        payslip = Payslip.query.get_or_404(payslip_id)
        if payslip.status != 'draft':
            abort(400, message=f'Cannot approve payslip in status {payslip.status}')
        payslip.status = 'approved'
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(payslip))


@blp.route("/payslips/<int:payslip_id>/pay")
class PayslipPay(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, payslip_id):
        payslip = Payslip.query.get_or_404(payslip_id)
        if payslip.status != 'approved':
            abort(400, message=f'Cannot pay payslip in status {payslip.status}')
        payslip.status = 'paid'
        payslip.payment_date = datetime.date.today()
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(payslip))


# ═══════════════════════════════════════════════
# Training & Skills
# ═══════════════════════════════════════════════

@blp.route("/courses")
class CourseList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        category = request.args.get('category')
        q = Course.query.filter_by(is_active=True).order_by(Course.code)
        if category:
            q = q.filter_by(category=category)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('code') or not data.get('title'):
            abort(400, message='code and title are required')
        existing = Course.query.filter_by(code=data['code']).first()
        if existing:
            abort(409, message='Course code already exists')
        course = Course(
            code=data['code'],
            title=data['title'],
            description=data.get('description'),
            provider=data.get('provider'),
            duration_hours=float(data['duration_hours']) if data.get('duration_hours') else None,
            cost=float(data['cost']) if data.get('cost') else None,
            category=data.get('category'),
            is_mandatory=bool(data.get('is_mandatory', False)),
        )
        from backend.extensions import db
        db.session.add(course)
        db.session.commit()
        return jsonify(_to_dict(course)), 201


@blp.route("/courses/<int:course_id>")
class CourseResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, course_id):
        return jsonify(_to_dict(Course.query.get_or_404(course_id)))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, course_id):
        course = Course.query.get_or_404(course_id)
        data = request.get_json() or {}
        for key, value in data.items():
            if hasattr(course, key) and key != 'id':
                setattr(course, key, value)
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(course))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, course_id):
        course = Course.query.get_or_404(course_id)
        course.is_active = False
        from backend.extensions import db
        db.session.commit()
        return '', 204


@blp.route("/training-records")
class TrainingRecordList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        employee_id = request.args.get('employee_id', type=int)
        course_id = request.args.get('course_id', type=int)
        q = TrainingRecord.query.order_by(TrainingRecord.completion_date.desc())
        if employee_id:
            q = q.filter_by(employee_id=employee_id)
        if course_id:
            q = q.filter_by(course_id=course_id)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('employee_id') or not data.get('course_id'):
            abort(400, message='employee_id and course_id are required')
        record = TrainingRecord(
            employee_id=data['employee_id'],
            course_id=data['course_id'],
            completion_date=datetime.datetime.strptime(data['completion_date'], '%Y-%m-%d').date(),
            expiry_date=datetime.datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            score=float(data['score']) if data.get('score') else None,
            result=data.get('result', 'passed'),
            notes=data.get('notes'),
        )
        from backend.extensions import db
        db.session.add(record)
        db.session.commit()
        return jsonify(_to_dict(record)), 201


@blp.route("/certifications")
class CertificationList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        employee_id = request.args.get('employee_id', type=int)
        q = Certification.query.order_by(Certification.issue_date.desc())
        if employee_id:
            q = q.filter_by(employee_id=employee_id)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('employee_id') or not data.get('name'):
            abort(400, message='employee_id and name are required')
        cert = Certification(
            employee_id=data['employee_id'],
            name=data['name'],
            issuer=data.get('issuer'),
            issue_date=datetime.datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
            expiry_date=datetime.datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            certificate_number=data.get('certificate_number'),
        )
        from backend.extensions import db
        db.session.add(cert)
        db.session.commit()
        return jsonify(_to_dict(cert)), 201


@blp.route("/certifications/<int:cert_id>")
class CertificationResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, cert_id):
        cert = Certification.query.get_or_404(cert_id)
        from backend.extensions import db
        db.session.delete(cert)
        db.session.commit()
        return '', 204


@blp.route("/skills")
class SkillList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        category = request.args.get('category')
        q = Skill.query.filter_by(is_active=True).order_by(Skill.code)
        if category:
            q = q.filter_by(category=category)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('code') or not data.get('name'):
            abort(400, message='code and name are required')
        existing = Skill.query.filter_by(code=data['code']).first()
        if existing:
            abort(409, message='Skill code already exists')
        skill = Skill(
            code=data['code'],
            name=data['name'],
            category=data.get('category'),
            description=data.get('description'),
        )
        from backend.extensions import db
        db.session.add(skill)
        db.session.commit()
        return jsonify(_to_dict(skill)), 201


@blp.route("/skill-matrix")
class SkillMatrixList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        employee_id = request.args.get('employee_id', type=int)
        skill_id = request.args.get('skill_id', type=int)
        q = SkillMatrix.query.order_by(SkillMatrix.employee_id)
        if employee_id:
            q = q.filter_by(employee_id=employee_id)
        if skill_id:
            q = q.filter_by(skill_id=skill_id)
        return jsonify([_to_dict(m) for m in q.all()])

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        if not data.get('employee_id') or not data.get('skill_id'):
            abort(400, message='employee_id and skill_id are required')
        existing = SkillMatrix.query.filter_by(
            employee_id=data['employee_id'], skill_id=data['skill_id']
        ).first()
        if existing:
            abort(409, message='Skill already assigned to this employee')
        sm = SkillMatrix(
            employee_id=data['employee_id'],
            skill_id=data['skill_id'],
            level=data.get('level', 1),
            years_experience=float(data['years_experience']) if data.get('years_experience') else None,
            notes=data.get('notes'),
        )
        from backend.extensions import db
        db.session.add(sm)
        db.session.commit()
        return jsonify(_to_dict(sm)), 201


@blp.route("/skill-matrix/<int:sm_id>")
class SkillMatrixResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, sm_id):
        sm = SkillMatrix.query.get_or_404(sm_id)
        data = request.get_json() or {}
        for key, value in data.items():
            if hasattr(sm, key) and key != 'id':
                setattr(sm, key, value)
        from backend.extensions import db
        db.session.commit()
        return jsonify(_to_dict(sm))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, sm_id):
        sm = SkillMatrix.query.get_or_404(sm_id)
        from backend.extensions import db
        db.session.delete(sm)
        db.session.commit()
        return '', 204
