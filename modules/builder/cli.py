"""
Builder CLI Commands
"""
import click
import json
import yaml
from pathlib import Path


@click.group(name='builder')
def builder_cli():
    """Builder commands for generating modules."""
    pass


@builder_cli.command(name='build')
@click.option('--template', '-t', required=True, help='Template file (YAML or JSON)')
@click.option('--output', '-o', required=True, help='Output directory')
@click.option('--format', '-f', type=click.Choice(['python', 'yaml']), default='python', help='Output format')
def build_module(template, output, format):
    """Build a module from template file."""
    click.echo(f"Building module from {template}...")

    template_path = Path(template)
    if not template_path.exists():
        click.echo(f"Error: Template file not found: {template}", err=True)
        return

    with open(template_path, 'r') as f:
        if template_path.suffix in ('.yaml', '.yml'):
            template_data = yaml.safe_load(f)
        else:
            template_data = json.load(f)

    from modules.builder.generator import AdaptiveBuilder
    from extensions import create_app, db

    app = create_app()
    with app.app_context():
        builder = AdaptiveBuilder(app, db)

        try:
            code = builder.build_from_template(template_data)

            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)

            (output_path / 'model.py').write_text(code['model'])
            (output_path / 'api.py').write_text(code['api'])
            (output_path / 'service.py').write_text(code['service'])

            click.echo(f"Module generated successfully in {output}")
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)


@builder_cli.command(name='validate')
@click.argument('template')
def validate_template(template):
    """Validate a template file."""
    click.echo(f"Validating {template}...")

    template_path = Path(template)
    if not template_path.exists():
        click.echo(f"Error: Template file not found: {template}", err=True)
        return

    with open(template_path, 'r') as f:
        if template_path.suffix in ('.yaml', '.yml'):
            template_data = yaml.safe_load(f)
        else:
            template_data = json.load(f)

    errors = []

    if 'name' not in template_data:
        errors.append("Missing required field: name")

    if 'fields' not in template_data:
        errors.append("Missing required field: fields")
    elif not template_data['fields']:
        errors.append("fields cannot be empty")

    if errors:
        click.echo("Validation FAILED:")
        for error in errors:
            click.echo(f"  - {error}")
    else:
        click.echo("Validation PASSED")


@builder_cli.command(name='generate')
@click.argument('modelId', type=int)
@click.option('--api-prefix', default='/api', help='API prefix')
def generate_code(modelId, api_prefix):
    """Generate code for an existing model."""
    from modules.builder.generator import CodeGenerator, TemplateValidator
    from extensions import create_app, db
    from modules.builder.service import get_builder_service as BuilderService

    app = create_app()
    with app.app_context():
        service = BuilderService()
        model = service.get_model(modelId)

        if not model:
            click.echo(f"Error: Model {modelId} not found", err=True)
            return

        validator = TemplateValidator()
        errors = validator.validate(model)

        if errors:
            click.echo("Validation errors:")
            for error in errors:
                click.echo(f"  - {error}")
            return

        generator = CodeGenerator()
        code = generator.generate_module(model, api_prefix)

        click.echo(f"\n=== MODEL ({model.name}) ===")
        click.echo(code['model'])

        click.echo(f"\n=== API ({model.name}) ===")
        click.echo(code['api'])

        click.echo(f"\n=== SERVICE ({model.name}) ===")
        click.echo(code['service'])


if __name__ == '__main__':
    builder_cli()
