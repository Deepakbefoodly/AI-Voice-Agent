import re
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

class RAGQueryInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)

    _injection_patterns: ClassVar[tuple[str, ...]] = (
        r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
        r"\bforget\s+(all\s+)?(previous|prior|above)\s+instructions\b",
        r"\boverride\s+(the\s+)?(system|developer|assistant)\s+instructions\b",
        r"\bbypass\s+(the\s+)?(safety|guardrails|rules|instructions)\b",
        r"\breveal\s+(the\s+)?(system|developer|hidden)\s+(prompt|message|instructions)\b",
        r"\bshow\s+(me\s+)?(the\s+)?(system|developer|hidden)\s+(prompt|message|instructions)\b",
        r"\bjailbreak\b",
        r"\bdo\s+anything\s+now\b",
        r"<\s*/?\s*(system|developer|assistant)\s*>",
    )

    @classmethod
    def reject_prompt_injection(cls, value: str) -> str:
        normalized = re.sub(r"\s+", " ", value.lower()).strip()

        for pattern in cls._injection_patterns:
            if re.search(pattern, normalized):
                raise ValueError("Question failed safety validation.")

        return value


class RAGOutput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    answer: str = Field(..., min_length=1, max_length=4000)
