"""
Block Builder - Creates UI blocks
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class BlockField:
    """Represents a field in a block"""
    model_field: str
    widget: str = "text"
    order: int = 0
    col_span: int = 12
    label: str = ""
    placeholder: str = ""
    visible: bool = True
    editable: bool = True
    readonly: bool = False
    required: bool = False
    help_text: str = ""


@dataclass
class Block:
    """Represents a UI block"""
    name: str
    technical_name: str
    type: str
    title: str = ""
    description: str = ""
    model: str = ""
    fields: List[BlockField] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)


class BlockBuilder:
    """Builds UI blocks from JSON configuration"""
    
    def __init__(self):
        self.blocks: Dict[str, Block] = {}
    
    def build(self, data: Dict[str, Any]) -> Block:
        """Build a block from JSON data"""
        fields = []
        for field_data in data.get("fields", []):
            field_obj = BlockField(
                model_field=field_data["model_field"],
                widget=field_data.get("widget", "text"),
                order=field_data.get("order", 0),
                col_span=field_data.get("col_span", 12),
                label=field_data.get("label", ""),
                placeholder=field_data.get("placeholder", ""),
                visible=field_data.get("visible", True),
                editable=field_data.get("editable", True),
                readonly=field_data.get("readonly", False),
                required=field_data.get("required", False),
                help_text=field_data.get("help_text", ""),
            )
            fields.append(field_obj)
        
        block = Block(
            name=data["name"],
            technical_name=data["technical_name"],
            type=data.get("type", "form"),
            title=data.get("title", data["name"]),
            description=data.get("description", ""),
            model=data.get("model", ""),
            fields=fields,
            permissions=data.get("permissions", {}),
            settings=data.get("settings", {}),
        )
        
        self.blocks[block.technical_name] = block
        return block
    
    def get_block(self, technical_name: str) -> Optional[Block]:
        """Get a block by technical name"""
        return self.blocks.get(technical_name)
    
    def list_blocks(self) -> List[Block]:
        """List all built blocks"""
        return list(self.blocks.values())
    
    def to_dict(self, block: Block) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "name": block.name,
            "technical_name": block.technical_name,
            "type": block.type,
            "title": block.title,
            "description": block.description,
            "model": block.model,
            "fields": [
                {
                    "model_field": f.model_field,
                    "widget": f.widget,
                    "order": f.order,
                    "col_span": f.col_span,
                    "label": f.label,
                    "placeholder": f.placeholder,
                    "visible": f.visible,
                    "editable": f.editable,
                    "readonly": f.readonly,
                    "required": f.required,
                    "help_text": f.help_text,
                }
                for f in block.fields
            ],
            "permissions": block.permissions,
            "settings": block.settings,
        }
