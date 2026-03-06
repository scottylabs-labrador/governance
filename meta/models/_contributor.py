from pydantic import BaseModel, Field


class Contributor(BaseModel):
    """Contributor record loaded from `contributors/*.toml`."""

    full_name: str = Field(alias="full-name")
    andrew_id: str | None = Field(alias="andrew-id", default=None)
