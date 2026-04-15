import os
import re

def refactor_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Rule 01 & 03: Replace common verbs and snake_case in routes
    replacements = [
        (r'@blp\.route\("/generate"\)', '@blp.route("/generations")'),
        (r'@blp\.route\("/apply"\)', '@blp.route("/applications")'),
        (r'@blp\.route\("/register"\)', '@blp.route("/registrations")'),
        (r'@auth_bp\.route\(\'/register\'\)', "@auth_bp.route('/registrations')"),
        (r'@auth_bp\.route\(\'/login\'\)', "@auth_bp.route('/logins')"),
        (r'@auth_bp\.route\(\'/refresh\'\)', "@auth_bp.route('/refreshes')"),
        (r'@blp\.route\(\'/module/status\'', "@blp.route('/module-statuses'"),
        (r'@blp\.route\(\'/modules/status\'', "@blp.route('/modules-statuses'"),
        (r'@blp\.route\("/import"\)', '@blp.route("/imports")'),
        (r'@blp\.route\("/export"\)', '@blp.route("/exports")'),
        (r'project_id', 'projectId'),
        (r'model_id', 'modelId'),
        (r'view_id', 'viewId'),
        (r'item_id', 'itemId'),
        (r'user_id', 'userId'),
        (r'workflow_id', 'workflowId'),
        (r'step_id', 'stepId'),
        (r'exec_id', 'executionId'),
        (r'modulo_nome', 'moduleName'),
        (r'suite_id', 'suiteId'),
        (r'case_id', 'caseId'),
        (r'invoice_id', 'invoiceId'),
        (r'order_id', 'orderId'),
        (r'quote_id', 'quoteId'),
        (r'module_id', 'moduleId'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Specific hierarchical/naming improvements
    content = content.replace('/suites/<int:suiteId>/run', '/suites/<int:suiteId>/runs')
    content = content.replace('/block/<int:blockId>/export-config', '/blocks/<int:blockId>/config-exports')
    content = content.replace('/sysmodel/<int:modelId>/export-config', '/sysmodels/<int:modelId>/config-exports')
    content = content.replace('/sysmodel/<int:modelId>/export-data', '/sysmodels/<int:modelId>/data-exports')
    content = content.replace('/sysmodel/<int:projectId>/import-config', '/sysmodels/projects/<int:projectId>/config-imports')
    content = content.replace('/sysmodel/<int:projectId>/import-data', '/sysmodels/projects/<int:projectId>/data-imports')

    with open(filepath, 'w') as f:
        f.write(content)

def walk_and_refactor(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') or file.endswith('.jsx') or file.endswith('.js'):
                refactor_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_refactor('backend')
    walk_and_refactor('frontend/src')
