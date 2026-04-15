import logging
from backend.models.system import SysReadModel
from backend.extensions import db
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

def sync_to_read_model(event):
    """
    Sync record data to SysReadModel (JSONB).

    Expected event payload:
    {
        "model": str,
        "record_id": int,
        "projectId": int,
        "data": dict
    }
    """
    payload = event.payload
    event_type = event.event_type

    model_name = payload.get("model")
    record_id = payload.get("record_id")
    projectId = payload.get("projectId")
    data = payload.get("data")

    if not all([model_name, record_id, projectId]):
        logger.warning(f"Invalid payload for read model sync: {payload}")
        return

    try:
        if event_type == "record.deleted":
            db.session.query(SysReadModel).filter_by(
                model_name=model_name,
                record_id=record_id,
                projectId=projectId
            ).delete()
            logger.debug(f"Deleted read model for {model_name}:{record_id}")
        else:
            # Upsert for created and updated
            # Since we are using SQLAlchemy and might be on SQLite in dev,
            # we handle upsert carefully.

            existing = db.session.query(SysReadModel).filter_by(
                model_name=model_name,
                record_id=record_id,
                projectId=projectId
            ).first()

            if existing:
                existing.data = data
                existing.version += 1
                logger.debug(f"Updated read model for {model_name}:{record_id}")
            else:
                new_read_model = SysReadModel(
                    model_name=model_name,
                    record_id=record_id,
                    projectId=projectId,
                    data=data
                )
                db.session.add(new_read_model)
                logger.debug(f"Created read model for {model_name}:{record_id}")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing to read model: {e}")

def register_read_model_handlers(event_bus):
    """Register handlers for read model synchronization."""
    event_bus.subscribe("record.created", sync_to_read_model)
    event_bus.subscribe("record.updated", sync_to_read_model)
    event_bus.subscribe("record.deleted", sync_to_read_model)
    logger.info("Read model handlers registered.")
