from sqlalchemy.orm import RelationshipProperty
from backend.extensions import db
from backend.models import SysModel, SysField, Project, User


def _map_column_type(col):
    """Map SQLAlchemy column type to SysField type string."""
    t = str(col.type).lower()
    if "integer" in t or "int" in t:
        return "integer"
    if "float" in t or "double" in t or "numeric" in t or "decimal" in t:
        return "float"
    if "boolean" in t:
        return "boolean"
    if "date" in t:
        if "time" in t:
            return "datetime"
        return "date"
    if "text" in t or "clob" in t:
        return "text"
    return "string"


def _map_relationship_type(direction):
    """Map SA relationship direction to SysField type."""
    from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
    if direction == MANYTOONE:
        return "many2one"
    if direction == ONETOMANY:
        return "one2many"
    if direction == MANYTOMANY:
        return "many2many"
    return "string"


def _get_project_id():
    """Get or create a default project for system models."""
    project = Project.query.filter_by(name="Default").first()
    if project:
        return project.id

    user = User.query.first()
    if not user:
        user = User(
            username="system",
            email="system@erpseed.local",
            password_hash="",
            role="admin",
        )
        db.session.add(user)
        db.session.flush()

    project = Project(
        name="Default",
        title="Default Project",
        description="Default system project for scanned models",
        owner_id=user.id,
    )
    db.session.add(project)
    db.session.flush()
    return project.id


def scan_static_models():
    """
    Scan all registered SQLAlchemy static models and create
    SysModel + SysField entries for any that don't already exist.
    Returns a summary dict.
    """
    db.session.rollback()

    models_created = 0
    fields_created = 0
    relations_found = 0

    project_id = _get_project_id()

    mapper_registry = db.Model.registry._class_registry

    for class_name, cls in mapper_registry.items():
        if not hasattr(cls, "__tablename__"):
            continue
        if not hasattr(cls, "__table__"):
            continue

        table_name = cls.__tablename__

        is_abstract = cls.__dict__.get("__abstract__", False)
        if is_abstract:
            continue

        if cls.__name__.startswith("_"):
            continue

        if not cls.__table__.columns:
            continue

        existing = SysModel.query.filter_by(table_name=table_name, projectId=project_id).first()
        if existing:
            continue

        model = SysModel(
            name=class_name.lower(),
            technical_name=f"static.{class_name.lower()}",
            title=class_name,
            table_name=table_name,
            projectId=project_id,
            is_system=True,
            is_active=True,
            status="published",
        )
        db.session.add(model)
        db.session.flush()
        models_created += 1

        seen_columns = set()
        for col in cls.__table__.columns:
            col_name = col.name
            if col_name in seen_columns:
                continue
            seen_columns.add(col_name)

            is_pk = col.primary_key
            is_nullable = col.nullable
            field_type = _map_column_type(col)

            field = SysField(
                name=col_name.replace("_", " ").title(),
                technical_name=col_name,
                title=col_name.replace("_", " ").title(),
                type=field_type,
                required=(not is_nullable and not is_pk),
                is_unique=col.unique or is_pk,
                is_index=bool(col.index) or is_pk,
                is_active=True,
                order=col.name and 0,
                modelId=model.id,
            )
            db.session.add(field)
            fields_created += 1

        seen_relations = set()
        for rel_key, rel in cls.__mapper__.relationships.items():
            if rel_key in seen_relations:
                continue
            seen_relations.add(rel_key)

            target_class = rel.mapper.class_
            target_table = target_class.__tablename__ if hasattr(target_class, "__tablename__") else None
            target_sysmodel = SysModel.query.filter_by(table_name=target_table, projectId=project_id).first() if target_table else None
            target_name = target_sysmodel.technical_name if target_sysmodel else (target_class.__name__.lower() if target_class else "")

            rel_type = _map_relationship_type(rel.direction)

            existing_field = SysField.query.filter_by(
                technical_name=rel_key, modelId=model.id
            ).first()
            if existing_field:
                existing_field.type = rel_type
                existing_field.relation_model = target_name
                existing_field.relation_type = rel_type
                if rel.back_populates:
                    existing_field.relation_field = rel.back_populates
                relations_found += 1
            else:
                field = SysField(
                    name=rel_key.replace("_", " ").title(),
                    technical_name=rel_key,
                    title=rel_key.replace("_", " ").title(),
                    type=rel_type,
                    relation_model=target_name,
                    relation_type=rel_type,
                    relation_field=rel.back_populates if rel.back_populates else None,
                    is_active=True,
                    modelId=model.id,
                )
                db.session.add(field)
                fields_created += 1
                relations_found += 1

    db.session.commit()

    return {
        "models_created": models_created,
        "fields_created": fields_created,
        "relations_found": relations_found,
    }
