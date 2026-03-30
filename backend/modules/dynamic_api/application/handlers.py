import json
from sqlalchemy import select, insert, update, delete, func, or_
from backend.models import SysModel, User
from backend.extensions import db
from flask_smorest import abort
from backend.core.utils.utils import get_table_object, serialize_value, log_audit
from backend.core.events.triggers import on_record_created, on_record_updated, on_record_deleted

class RecordCommandHandler:
    def handle_create(self, cmd):
        sys_model = SysModel.query.filter_by(project_id=cmd.project_id, name=cmd.model_name).first()
        if not sys_model:
            abort(404, message=f"Model '{cmd.model_name}' not found.")

        schema_name = f"project_{cmd.project_id}"
        table = get_table_object(cmd.model_name, schema=schema_name)


        schema_name = f"project_{cmd.project_id}"
        table = get_table_object(cmd.model_name, schema=schema_name)

        # Simple validation & mapping (extracted from old service)
        validated_data = {}
        for field in sys_model.fields:
            if field.type in ["formula", "summary", "lookup", "calculated", "lines"]:
                continue
            val = cmd.data.get(field.technical_name or field.name)
            if val is not None:
                validated_data[field.name] = val

        stmt = insert(table).values(validated_data).returning(table)
        result = db.session.execute(stmt).mappings().one()

        db.session.commit()
        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}


        stmt = insert(table).values(validated_data).returning(table)
        result = db.session.execute(stmt).mappings().one()

        db.session.commit()
        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}

        try:
            on_record_created(cmd.model_name, result.id, result_dict, cmd.project_id)
        except Exception:
            pass


        return result_dict

    def handle_update(self, cmd):
        schema_name = f"project_{cmd.project_id}"
        table = get_table_object(cmd.model_name, schema=schema_name)

        stmt = update(table).where(table.c.id == cmd.item_id).values(cmd.data).returning(table)
        result = db.session.execute(stmt).mappings().one()
        db.session.commit()


        stmt = update(table).where(table.c.id == cmd.item_id).values(cmd.data).returning(table)
        result = db.session.execute(stmt).mappings().one()
        db.session.commit()

        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}
        try:
            on_record_updated(cmd.model_name, cmd.item_id, result_dict, cmd.project_id)
        except Exception:
            pass
        return result_dict

    def handle_delete(self, cmd):
        schema_name = f"project_{cmd.project_id}"
        table = get_table_object(cmd.model_name, schema=schema_name)

        stmt = delete(table).where(table.c.id == cmd.item_id)
        db.session.execute(stmt)
        db.session.commit()


        stmt = delete(table).where(table.c.id == cmd.item_id)
        db.session.execute(stmt)
        db.session.commit()

        try:
            on_record_deleted(cmd.model_name, cmd.item_id, cmd.project_id)
        except Exception:
            pass
        return True
