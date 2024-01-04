from dataclasses import dataclass


@dataclass
class JobParams:
    source_table: str
    target_table: str
