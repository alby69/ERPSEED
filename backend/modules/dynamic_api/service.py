from .application.handlers import RecordCommandHandler
from .application.commands.record_commands import CreateRecordCommand, UpdateRecordCommand, DeleteRecordCommand
from backend.modules.dynamic_api.services.dynamic_api_service import DynamicApiService

class DynamicApiServiceWrapper:
    """Wrapper that combines old logic with new command pattern"""
    def __init__(self):
        self.handler = RecordCommandHandler()
        self.legacy_service = DynamicApiService()

    def create_record(self, projectId, model_name, data):
        cmd = CreateRecordCommand(projectId, model_name, data)
        # Use legacy service for complex validation/file handling for now
        # but the actual write should go through handler eventually
        return self.legacy_service.create_record(projectId, model_name, data)

    def update_record(self, projectId, model_name, itemId, data):
        return self.legacy_service.update_record(projectId, model_name, itemId, data)

    def delete_record(self, projectId, model_name, itemId):
        return self.legacy_service.delete_record(projectId, model_name, itemId)

    def list_records(self, projectId, model_name, page=1, per_page=10):
        return self.legacy_service.list_records(projectId, model_name, page, per_page)

    def get_record(self, projectId, model_name, itemId):
        return self.legacy_service.get_record(projectId, model_name, itemId)

    def bulk_delete(self, projectId, model_name, ids_to_delete):
        return self.legacy_service.bulk_delete(projectId, model_name, ids_to_delete)

    def get_model_metadata(self, projectId, model_name):
        return self.legacy_service.get_model_metadata(projectId, model_name)

    def clone_record(self, projectId, model_name, itemId):
        return self.legacy_service.clone_record(projectId, model_name, itemId)

    def import_csv(self, projectId, model_name, file):
        return self.legacy_service.import_csv(projectId, model_name, file)

def get_dynamic_api_service():
    return DynamicApiServiceWrapper()
