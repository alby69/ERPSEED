from dataclasses import dataclass

@dataclass
class CreateProjectCommand:
    name: str
    title: str
    description: str = None
    owner_id: int = None

@dataclass
class UpdateProjectCommand:
    project_id: int
    user_id: int
    data: dict

@dataclass
class DeleteProjectCommand:
    project_id: int
    user_id: int

@dataclass
class AddMemberCommand:
    project_id: int
    user_id: int
    member_user_id: int

@dataclass
class RemoveMemberCommand:
    project_id: int
    user_id: int
    member_user_id: int
