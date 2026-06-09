from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models import SysModel, SysField
from backend.modules.builder.models import Block, BlockRelationship
from .scanner import scan_static_models

relmgr_blp = Blueprint(
    "relationship_manager",
    __name__,
    description="Relationship Manager API"
)


def _serialize_model(m):
    return {
        "id": m.id,
        "name": m.name,
        "technical_name": m.technical_name,
        "title": m.title,
        "table_name": m.table_name,
        "is_system": m.is_system,
    }


def _serialize_field(f):
    return {
        "id": f.id,
        "name": f.name,
        "technical_name": f.technical_name,
        "type": f.type,
        "relation_model": f.relation_model,
        "relation_type": f.relation_type,
        "relation_field": f.relation_field,
        "modelId": f.modelId,
    }


@relmgr_blp.route("/relationship-manager/graph")
class GraphAPI(MethodView):
    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        nodes = []
        edges = []

        models = SysModel.query.filter_by(is_active=True).all()
        for m in models:
            field_list = []
            for f in (m.fields or []):
                field_list.append(_serialize_field(f))
            nodes.append({
                "id": f"model_{m.id}",
                "type": "model",
                "label": m.title or m.name,
                "table_name": m.table_name,
                "model_id": m.id,
                "fields": field_list,
                "origin": "scanned" if m.is_system else "dynamic",
            })

            for f in (m.fields or []):
                if f.type in ("many2one", "one2many", "many2many") and f.relation_model:
                    target = SysModel.query.filter_by(technical_name=f.relation_model).first()
                    if target:
                        edges.append({
                            "id": f"edge_{m.id}_{f.id}",
                            "source": f"model_{m.id}",
                            "target": f"model_{target.id}",
                            "label": f"{f.technical_name} ({f.type})",
                            "type": "field",
                            "field_id": f.id,
                            "rel_type": f.type,
                        })

        blocks = Block.query.filter_by(is_active=True).all()
        for b in blocks:
            nodes.append({
                "id": f"block_{b.id}",
                "type": "block",
                "label": b.title or b.name,
                "block_id": b.id,
            })

        rels = BlockRelationship.query.all()
        for r in rels:
            edges.append({
                "id": f"edge_block_{r.id}",
                "source": f"block_{r.block_id}",
                "target": f"block_{r.depends_on_id}",
                "label": r.rel_type,
                "type": "block_dependency",
                "rel_id": r.id,
                "rel_type": r.rel_type,
            })

        return {"nodes": nodes, "edges": edges}


@relmgr_blp.route("/relationship-manager/models")
class ModelsListAPI(MethodView):
    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        models_data = []
        models = SysModel.query.filter_by(is_active=True).order_by(SysModel.title).all()
        for m in models:
            fields = SysField.query.filter_by(modelId=m.id, is_active=True).order_by(SysField.order).all()
            models_data.append({
                **_serialize_model(m),
                "fields": [_serialize_field(f) for f in fields],
            })

        blocks = Block.query.filter_by(is_active=True).order_by(Block.name).all()
        for b in blocks:
            models_data.append({
                "id": b.id,
                "type": "block",
                "name": b.name,
                "title": b.title or b.name,
                "table_name": None,
            })

        return {"models": models_data}


@relmgr_blp.route("/relationship-manager/relationships", methods=["GET", "POST"])
class RelationshipsAPI(MethodView):
    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        results = []

        field_rels = SysField.query.filter(
            SysField.type.in_(["many2one", "one2many", "many2many"]),
            SysField.relation_model.isnot(None),
            SysField.relation_model != "",
        ).all()

        for f in field_rels:
            source_model = SysModel.query.get(f.modelId)
            target_model = SysModel.query.filter_by(technical_name=f.relation_model).first()
            results.append({
                "id": f"field_{f.id}",
                "type": "field",
                "source_type": "model",
                "source_id": f.modelId,
                "source_label": source_model.title if source_model else f.modelId,
                "source_field_id": f.id,
                "source_field_label": f.technical_name,
                "target_type": "model",
                "target_id": target_model.id if target_model else None,
                "target_label": target_model.title if target_model else f.relation_model,
                "target_field_id": None,
                "target_field_label": f.relation_field,
                "rel_type": f.type,
            })

        block_rels = BlockRelationship.query.all()
        for r in block_rels:
            source_block = Block.query.get(r.block_id)
            target_block = Block.query.get(r.depends_on_id)
            results.append({
                "id": f"block_{r.id}",
                "type": "block",
                "source_type": "block",
                "source_id": r.block_id,
                "source_label": source_block.title if source_block else r.block_id,
                "source_field_id": None,
                "source_field_label": None,
                "target_type": "block",
                "target_id": r.depends_on_id,
                "target_label": target_block.title if target_block else r.depends_on_id,
                "target_field_id": None,
                "target_field_label": None,
                "rel_type": r.rel_type,
            })

        total = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        page_items = results[start:end]

        return {
            "items": page_items,
            "total": total,
            "page": page,
            "pages": (total + per_page - 1) // per_page,
        }

    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data:
            abort(400, message="No data provided")

        rel_type = data.get("rel_type")
        source_type = data.get("source_type")
        source_id = data.get("source_id")
        target_type = data.get("target_type")
        target_id = data.get("target_id")

        if not all([rel_type, source_type, source_id, target_type, target_id]):
            abort(400, message="Missing required fields: rel_type, source_type, source_id, target_type, target_id")

        if source_type == "block" and target_type == "block":
            rel = BlockRelationship(
                block_id=source_id,
                depends_on_id=target_id,
                rel_type=rel_type,
            )
            db.session.add(rel)
            db.session.commit()
            return {"id": f"block_{rel.id}", "message": "Block relationship created"}, 201

        elif source_type == "model" and target_type == "model":
            source_field_id = data.get("source_field_id")
            source_field = SysField.query.get(source_field_id) if source_field_id else None
            target_model = SysModel.query.get(target_id)
            if not target_model:
                abort(404, message="Target model not found")

            if source_field:
                source_field.type = rel_type
                source_field.relation_model = target_model.technical_name
                source_field.relation_type = rel_type
                db.session.commit()
                return {"id": f"field_{source_field.id}", "message": "Field relationship updated"}, 200
            else:
                field = SysField(
                    name=data.get("name", "relation"),
                    technical_name=data.get("technical_name", "relation"),
                    title=data.get("title", "Relation"),
                    type=rel_type,
                    relation_model=target_model.technical_name,
                    relation_type=rel_type,
                    modelId=source_id,
                    is_active=True,
                )
                db.session.add(field)
                db.session.commit()
                return {"id": f"field_{field.id}", "message": "Field relationship created"}, 201

        abort(400, message="Invalid source_type/target_type combination")


@relmgr_blp.route("/relationship-manager/relationships/<string:rel_id>", methods=["DELETE"])
class RelationshipDeleteAPI(MethodView):
    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, rel_id):
        if rel_id.startswith("block_"):
            rid = int(rel_id.replace("block_", ""))
            rel = BlockRelationship.query.get(rid)
            if not rel:
                abort(404, message="Relationship not found")
            db.session.delete(rel)
            db.session.commit()
            return "", 204

        elif rel_id.startswith("field_"):
            fid = int(rel_id.replace("field_", ""))
            field = SysField.query.get(fid)
            if not field:
                abort(404, message="Field not found")
            field.type = "string"
            field.relation_model = None
            field.relation_type = None
            field.relation_field = None
            db.session.commit()
            return "", 204

        abort(404, message="Relationship not found")


@relmgr_blp.route("/relationship-manager/scan", methods=["POST"])
class ScanAPI(MethodView):
    @relmgr_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        result = scan_static_models()
        return result, 200
