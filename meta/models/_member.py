from pydantic import BaseModel, Field


class Member(BaseModel):
    """Member record loaded from `members/*.toml`."""

    full_name: str = Field(alias="full-name")
    andrew_id: str | None = Field(alias="andrew-id", default=None)
