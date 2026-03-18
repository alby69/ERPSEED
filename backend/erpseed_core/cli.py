"""
ERPSEED Core CLI - Command Line Interface

Provides commands for:
- new: Create new project
- build: Build project from JSON
- export: Export project to JSON
- import: Import project from JSON
- validate: Validate JSON schemas
- parse: Parse Python spec files
- serve: Run development server
- db: Database operations
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .builder import ModelBuilder, BlockBuilder, WorkflowBuilder, BusinessRuleBuilder
from .generator import export_project, export_model, export_block
from .parser import parse_spec_file
from .schemas import validate_against_schema


def cmd_new(args):
    """Create a new project structure"""
    project_name = args.name
    project_path = Path(args.output) / project_name if args.output else Path.cwd() / project_name
    
    project_path.mkdir(parents=True, exist_ok=False)
    
    project_json = {
        "name": project_name,
        "version": "1.0.0",
        "description": args.description or f"{project_name} ERP Project",
        "models": [],
        "blocks": [],
        "workflows": [],
        "business_rules": [],
        "settings": {
            "database": {"type": "sqlite", "name": f"{project_name}.db"},
            "auth": {"enabled": True},
            "theme": {"name": "default"}
        }
    }
    
    (project_path / "project.json").write_text(json.dumps(project_json, indent=2))
    (project_path / "models").mkdir()
    (project_path / "blocks").mkdir()
    (project_path / "workflows").mkdir()
    (project_path / "business_rules").mkdir()
    
    print(f"Created new project: {project_name} at {project_path}")
    return 0


def cmd_build(args):
    """Build project from JSON files"""
    project_path = Path(args.project)
    
    if not project_path.exists():
        print(f"Error: Project path {project_path} does not exist")
        return 1
    
    project_json = project_path / "project.json"
    if not project_json.exists():
        print(f"Error: project.json not found in {project_path}")
        return 1
    
    data = json.loads(project_json.read_text())
    
    model_builder = ModelBuilder()
    block_builder = BlockBuilder()
    workflow_builder = WorkflowBuilder()
    business_rule_builder = BusinessRuleBuilder()
    
    for model_file in (project_path / "models").glob("*.json"):
        model_data = json.loads(model_file.read_text())
        model_builder.build(model_data)
    
    for block_file in (project_path / "blocks").glob("*.json"):
        block_data = json.loads(block_file.read_text())
        block_builder.build(block_data)
    
    for wf_file in (project_path / "workflows").glob("*.json"):
        wf_data = json.loads(wf_file.read_text())
        workflow_builder.build(wf_data)
    
    for br_file in (project_path / "business_rules").glob("*.json"):
        br_data = json.loads(br_file.read_text())
        business_rule_builder.build(br_data)
    
    print(f"Built project: {data.get('name', 'Unknown')}")
    return 0


def cmd_export(args):
    """Export project to JSON"""
    project_path = Path(args.project)
    output_path = Path(args.output) if args.output else project_path / "export.json"
    
    data = export_project(project_path)
    output_path.write_text(json.dumps(data, indent=2))
    
    print(f"Exported project to: {output_path}")
    return 0


def cmd_import(args):
    """Import project from JSON"""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        return 1
    
    data = json.loads(input_path.read_text())
    project_path = Path(args.output) if args.output else Path.cwd() / data.get("name", "imported_project")
    
    project_path.mkdir(parents=True, exist_ok=False)
    (project_path / "project.json").write_text(json.dumps(data, indent=2))
    
    print(f"Imported project to: {project_path}")
    return 0


def cmd_validate(args):
    """Validate JSON files against schemas"""
    schema_type = args.schema
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        return 1
    
    data = json.loads(file_path.read_text())
    is_valid, errors = validate_against_schema(data, schema_type)
    
    if is_valid:
        print(f"✓ {schema_type} schema validation passed")
        return 0
    else:
        print(f"✗ {schema_type} schema validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1


def cmd_parse(args):
    """Parse Python spec files"""
    spec_path = Path(args.file)
    
    if not spec_path.exists():
        print(f"Error: Spec file {spec_path} does not exist")
        return 1
    
    output_path = Path(args.output) if args.output else spec_path.with_suffix(".json")
    
    data = parse_spec_file(spec_path)
    output_path.write_text(json.dumps(data, indent=2))
    
    print(f"Parsed spec file to: {output_path}")
    return 0


def cmd_serve(args):
    """Run development server"""
    from .api import create_app
    
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


def cmd_db(args):
    """Database operations"""
    from .api import create_app
    from flask import Flask
    
    app = create_app()
    
    with app.app_context():
        if args.action == "init":
            from .builder.db import init_database
            init_database(args.type or "sqlite", args.dsn)
            print("Database initialized")
        elif args.action == "migrate":
            from .builder.db import run_migrations
            run_migrations()
            print("Migrations complete")
        elif args.action == "sync":
            from .builder.db import sync_database
            sync_database(args.source, args.target)
            print("Database sync complete")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="ERPSEED Core CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    new_parser = subparsers.add_parser("new", help="Create new project")
    new_parser.add_argument("name", help="Project name")
    new_parser.add_argument("--description", help="Project description")
    new_parser.add_argument("--output", help="Output directory")
    
    build_parser = subparsers.add_parser("build", help="Build project from JSON")
    build_parser.add_argument("project", help="Project directory path")
    
    export_parser = subparsers.add_parser("export", help="Export project to JSON")
    export_parser.add_argument("project", help="Project directory path")
    export_parser.add_argument("--output", help="Output file path")
    
    import_parser = subparsers.add_parser("import", help="Import project from JSON")
    import_parser.add_argument("input", help="Input JSON file")
    import_parser.add_argument("--output", help="Output directory")
    
    validate_parser = subparsers.add_parser("validate", help="Validate JSON against schema")
    validate_parser.add_argument("schema", choices=["model", "block", "module", "workflow", "business_rule", "project"])
    validate_parser.add_argument("file", help="JSON file to validate")
    
    parse_parser = subparsers.add_parser("parse", help="Parse Python spec file")
    parse_parser.add_argument("file", help="Python spec file")
    parse_parser.add_argument("--output", help="Output JSON file")
    
    serve_parser = subparsers.add_parser("serve", help="Run development server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port to bind")
    serve_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_parser.add_argument("action", choices=["init", "migrate", "sync"])
    db_parser.add_argument("--type", help="Database type (sqlite, postgresql)")
    db_parser.add_argument("--dsn", help="Database connection string")
    db_parser.add_argument("--source", help="Source database for sync")
    db_parser.add_argument("--target", help="Target database for sync")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "new": cmd_new,
        "build": cmd_build,
        "export": cmd_export,
        "import": cmd_import,
        "validate": cmd_validate,
        "parse": cmd_parse,
        "serve": cmd_serve,
        "db": cmd_db,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
