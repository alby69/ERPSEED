"""
Create initial tenant and admin user.
"""
import click
from backend.extensions import db
from backend.core.models import Tenant, User


@click.command('create-tenant')
@click.option('--name', prompt='Organization name', help='Name of the organization')
@click.option('--slug', prompt='Organization slug (URL)', help='URL slug (e.g., mycompany)')
@click.option('--email', prompt='Admin email', help='Admin user email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--first-name', default='', help='Admin first name')
@click.option('--last-name', default='', help='Admin last name')
def create_tenant(name, slug, email, password, first_name, last_name):
    """Create initial tenant and admin user."""
    
    # Check if tenant exists
    if Tenant.query.filter_by(slug=slug).first():
        click.echo(f'Error: Tenant with slug "{slug}" already exists', err=True)
        return
    
    # Check if email exists
    if User.query.filter_by(email=email.lower()).first():
        click.echo(f'Error: User with email "{email}" already exists', err=True)
        return
    
    # Create tenant
    tenant = Tenant(
        name=name,
        slug=slug,
        is_active=True,
        plan='enterprise',
        max_users=50,
        max_storage_mb=10240
    )
    db.session.add(tenant)
    db.session.flush()
    
    # Create admin user
    user = User(
        tenant_id=tenant.id,
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        role='admin',
        is_primary=True,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    
    db.session.commit()
    
    click.echo(f'Successfully created tenant "{name}" (slug: {slug})')
    click.echo(f'Admin user: {email}')
    click.echo(f'Access URL: https://{slug}.flaskerp.com')


if __name__ == '__main__':
    create_tenant()
