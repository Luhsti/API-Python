from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class LivroBase(SQLModel):
    autor: str = Field(index=True)
    titulo: str = Field(index=True)
    editora: str = Field(index=True)
    ano_publicacao: int = Field(index=True)

class Livro(LivroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, unique=True)

class LivroRespostas(LivroBase):
    uuid: UUID

class LivroPostPut(LivroBase):
    ... 

class LivroPatch(SQLModel):
    autor: str | None = None
    titulo: str | None = None
    editora: str | None = None
    ano_publicacao: int | None = None

class ConfirmaDelete(BaseModel):    
    message: str
    uuid: UUID  