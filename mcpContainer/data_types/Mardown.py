from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MarkdownCell:
    cell_type: str = field(init=False, default="markdown")
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    attachments: Optional[Dict[str, Dict[str, Any]]] = None



