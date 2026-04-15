from dataclasses import dataclass

@dataclass
class CreateProjectCommand:
    name: str
    title: str
    description: str = None
    owner_id: int = None

@dataclass
class UpdateProjectCommand:
    projectId: int
    userId: int
    data: dict

@dataclass
class DeleteProjectCommand:
    projectId: int
    userId: int

@dataclass
class AddMemberCommand:
    projectId: int
    userId: int
    member_userId: int

@dataclass
class RemoveMemberCommand:
    projectId: int
    userId: int
    member_userId: int
