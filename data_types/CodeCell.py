from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class CodeCell:
    cell_type: str = field(init=False, default="code")
    execution_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    outputs: List[Dict[str, Any]] = field(default_factory=list)