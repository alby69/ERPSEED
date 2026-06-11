"""Test per moduli Payroll e Formazione (HR)."""


def _create_employee(client, auth_headers):
    payload = {
        "employee_number": "EMP001",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.com",
        "job_title": "Sviluppatore",
        "hire_date": "2025-01-15",
        "salary": 40000,
    }
    resp = client.post("/api/v1/hr/employees", json=payload, headers=auth_headers)
    if resp.status_code == 201:
        return resp.get_json()
    return None


# ── Payroll Period ──

def test_create_payroll_period(client, auth_headers):
    resp = client.post("/api/v1/hr/payroll-periods", json={"year": 2026, "month": 6, "name": "Giugno 2026"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "2026-06"


def test_list_payroll_periods(client, auth_headers):
    resp = client.get("/api/v1/hr/payroll-periods", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_close_payroll_period(client, auth_headers):
    created = client.post("/api/v1/hr/payroll-periods", json={"year": 2026, "month": 7}, headers=auth_headers).get_json()
    pid = created["id"]
    resp = client.post(f"/api/v1/hr/payroll-periods/{pid}/close", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "closed"


# ── Payslip ──

def test_create_payslip(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    period = client.post("/api/v1/hr/payroll-periods", json={"year": 2026, "month": 8}, headers=auth_headers).get_json()
    payload = {
        "employee_id": emp_id,
        "period_id": period["id"],
        "gross_pay": 3500.0,
        "deductions": 700.0,
        "net_pay": 2800.0,
        "taxes": 500.0,
        "employer_contributions": 1200.0,
        "lines": [
            {"description": "Stipendio base", "type": "earning", "amount": 3500.0},
            {"description": "IRPEF", "type": "deduction", "amount": -500.0},
        ],
    }
    resp = client.post("/api/v1/hr/payslips", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "draft"
    assert data["gross_pay"] == 3500.0


def test_list_payslips(client, auth_headers):
    resp = client.get("/api/v1/hr/payslips", headers=auth_headers)
    assert resp.status_code == 200


def test_approve_payslip(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    period = client.post("/api/v1/hr/payroll-periods", json={"year": 2026, "month": 9}, headers=auth_headers).get_json()
    ps = client.post("/api/v1/hr/payslips", json={
        "employee_id": emp_id, "period_id": period["id"],
        "gross_pay": 3000.0, "net_pay": 2400.0,
    }, headers=auth_headers).get_json()
    resp = client.post(f"/api/v1/hr/payslips/{ps['id']}/approve", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "approved"


def test_pay_payslip(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    period = client.post("/api/v1/hr/payroll-periods", json={"year": 2026, "month": 10}, headers=auth_headers).get_json()
    ps = client.post("/api/v1/hr/payslips", json={
        "employee_id": emp_id, "period_id": period["id"],
        "gross_pay": 3000.0, "net_pay": 2400.0,
    }, headers=auth_headers).get_json()
    client.post(f"/api/v1/hr/payslips/{ps['id']}/approve", headers=auth_headers)
    resp = client.post(f"/api/v1/hr/payslips/{ps['id']}/pay", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "paid"


# ── Course ──

def test_create_course(client, auth_headers):
    payload = {"code": "SIC-01", "title": "Sicurezza sul Lavoro", "category": "sicurezza", "duration_hours": 8, "is_mandatory": True}
    resp = client.post("/api/v1/hr/courses", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["code"] == "SIC-01"


def test_list_courses(client, auth_headers):
    resp = client.get("/api/v1/hr/courses", headers=auth_headers)
    assert resp.status_code == 200


def test_list_courses_by_category(client, auth_headers):
    resp = client.get("/api/v1/hr/courses?category=informatica", headers=auth_headers)
    assert resp.status_code == 200


# ── Training Record ──

def test_create_training_record(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    course = client.post("/api/v1/hr/courses", json={"code": "CS-01", "title": "Corso SQL"}, headers=auth_headers).get_json()
    payload = {
        "employee_id": emp_id,
        "course_id": course["id"],
        "completion_date": "2026-06-01",
        "score": 95,
        "result": "passed",
    }
    resp = client.post("/api/v1/hr/training-records", json=payload, headers=auth_headers)
    assert resp.status_code == 201


# ── Certification ──

def test_create_certification(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    payload = {
        "employee_id": emp_id,
        "name": "AWS Solutions Architect",
        "issuer": "Amazon",
        "issue_date": "2026-05-01",
        "certificate_number": "AWS-12345",
    }
    resp = client.post("/api/v1/hr/certifications", json=payload, headers=auth_headers)
    assert resp.status_code == 201


# ── Skill ──

def test_create_skill(client, auth_headers):
    payload = {"code": "PY", "name": "Python", "category": "programmazione"}
    resp = client.post("/api/v1/hr/skills", json=payload, headers=auth_headers)
    assert resp.status_code == 201


def test_list_skills(client, auth_headers):
    resp = client.get("/api/v1/hr/skills", headers=auth_headers)
    assert resp.status_code == 200


# ── Skill Matrix ──

def test_create_skill_matrix(client, auth_headers):
    emp = _create_employee(client, auth_headers)
    emp_id = emp.get("id", 1) if emp else 1
    skill = client.post("/api/v1/hr/skills", json={"code": "JS", "name": "JavaScript"}, headers=auth_headers).get_json()
    payload = {"employee_id": emp_id, "skill_id": skill["id"], "level": 4, "years_experience": 5}
    resp = client.post("/api/v1/hr/skill-matrix", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["level"] == 4


def test_list_skill_matrix(client, auth_headers):
    resp = client.get("/api/v1/hr/skill-matrix", headers=auth_headers)
    assert resp.status_code == 200
