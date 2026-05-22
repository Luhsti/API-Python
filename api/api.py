
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app=FastAPI(title="API de Livros")

class Livro(BaseModel):
    uuid: UUID
    id: int
    titulo: str
    autor: str

class LivroPostPut(BaseModel):
    titulo: str
    autor: str

class LivroPatch(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None

class ConfirmaDelete(BaseModel):
    message: str
    uuid: UUID


livros_db = {
    1: {"uuid": uuid4(), "id": 1, "titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien"},
    2: {"uuid": uuid4(), "id": 2, "titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling"},
}

async def get_livros():
    return list(livros_db.values())

async def get_livro(livro_id: UUID):
    for livro in livros_db.values():
        if livro["uuid"] == livro_id:
            return livro    

@app.get("/livros", response_model=list[Livro])
async def read_livros() -> List[Livro]:
    return await get_livros()

@app.get("/livros/{livro_id}", response_model=Livro,
         responses={404: {"description": "Livro não encontrado"}})
async def read_livro(livro_id: UUID) -> Livro:
    livro = await get_livro(livro_id)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro    

@app.post("/livros", response_model=Livro, status_code=201, responses={201: {"description": "Livro criado com sucesso"}})
async def create_livro(livro: LivroPostPut) -> Livro:
    novo_uuid = uuid4()
    livro_id = len(livros_db) + 1 if livros_db else 1
    novo_livro = Livro(uuid=novo_uuid, id=livro_id, titulo=livro.titulo, autor=livro.autor)
    livros_db[livro_id] = novo_livro.model_dump()
    return novo_livro

@app.put("/livros/{livro_id}", response_model=Livro, responses={404: {"description": "Livro não encontrado"}})
async def update_livro(livro_id: UUID, livro: LivroPostPut) -> Livro:
    livro_salvo = await get_livro(livro_id)
    if livro_salvo is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    livro_salvo["titulo"] = livro.titulo
    livro_salvo["autor"] = livro.autor  
    return livro_salvo 


@app.patch("/livros/{livro_id}", response_model=Livro, responses={404: {"description": "Livro não encontrado"}})
async def patch_livro(livro_id: UUID, livro: LivroPatch) -> Livro:
    livro_salvo = await get_livro(livro_id)
    if livro_salvo is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    for key, value in livro.model_dump(exclude_defaults=True).items():
        livro_salvo[key] = value
    return livro_salvo      

@app.delete("/livros/{livro_id}", status_code=200, responses={404: {"description": "Livro não encontrado"}})
async def delete_livro(livro_id: UUID) -> ConfirmaDelete:
    livro_salvo = await get_livro(livro_id)
    if livro_salvo is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    del livros_db[livro_salvo["id"]]    
    return ConfirmaDelete(message=f"Livro {livro_salvo['titulo']} excluído com sucesso", uuid=livro_salvo["uuid"])       
