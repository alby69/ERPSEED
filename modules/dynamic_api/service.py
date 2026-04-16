from .application.handlers import RecordCommandHandler
from .application.commands.record_commands import CreateRecordCommand, UpdateRecordCommand, DeleteRecordCommand
from modules.dynamic_api.services.dynamic_api_service import DynamicApiService

class DynamicApiServiceWrapper:
    """Wrapper that combines old logic with new command pattern"""
    def __init__(self):
        self.handler = RecordCommandHandler()
        self.legacy_service = DynamicApiService()

    def create_record(self, project_id, model_name, data):
        cmd = CreateRecordCommand(project_id, model_name, data)
        # Use legacy service for complex validation/file handling for now
        # but the actual write should go through handler eventually
        return self.legacy_service.create_record(project_id, model_name, data)

    def update_record(self, project_id, model_name, item_id, data):
        return self.legacy_service.update_record(project_id, model_name, item_id, data)

    def delete_record(self, project_id, model_name, item_id):
        return self.legacy_service.delete_record(project_id, model_name, item_id)

    def list_records(self, project_id, model_name, page=1, per_page=10):
        return self.legacy_service.list_records(project_id, model_name, page, per_page)

    def get_record(self, project_id, model_name, item_id):
        return self.legacy_service.get_record(project_id, model_name, item_id)

    def bulk_delete(self, project_id, model_name, ids_to_delete):
        return self.legacy_service.bulk_delete(project_id, model_name, ids_to_delete)

    def get_model_metadata(self, project_id, model_name):
        return self.legacy_service.get_model_metadata(project_id, model_name)

    def clone_record(self, project_id, model_name, item_id):
        return self.legacy_service.clone_record(project_id, model_name, item_id)

    def import_csv(self, project_id, model_name, file):
        return self.legacy_service.import_csv(project_id, model_name, file)

def get_dynamic_api_service():
    return DynamicApiServiceWrapper()
