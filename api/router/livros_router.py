
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Response
from sqlmodel import Session, func, insert, select

from api.database import get_session
from api.models import ConfirmaDelete, Livro, LivroBase, LivroPatch, LivroPostPut, LivroRespostas


router = APIRouter(prefix="/livros", tags=["livros"])
SessionDep = Annotated[Session, Depends(get_session)]


async def get_livros(session: SessionDep, response: Response, page:int) -> list[LivroRespostas]:
    PAGE_SIZE = 10
    total_itens = session.exec(select(func.count()).select_from(Livro)).one()
    total_pages = (total_itens + PAGE_SIZE - 1) // PAGE_SIZE
    if page > total_pages and total_pages > 0:
        page = total_pages
    offset = (page - 1) * PAGE_SIZE
    query = select(Livro).limit(PAGE_SIZE).offset(offset)
    livros = session.exec(query).all()

    response.headers["X-Total-Count"] = str(total_itens)
    response.headers["X-Total-Pages"] = str(total_pages)

    return [LivroRespostas.model_validate(livro) for livro in livros]

async def get_livro(livro_id: UUID, session: SessionDep):
    if livro := session.exec(select(Livro).where(Livro.uuid == livro_id)).first():
        return LivroRespostas.model_validate(livro)
    raise HTTPException(status_code=404, detail="Livro nao encontrado") 


@router.get("", response_model=list[LivroRespostas])
async def read_livros(session: SessionDep, response: Response, page:int = Query(1, ge=1)) -> list[LivroRespostas]:
    return await get_livros(session, response, page)

@router.get("/{livro_id}", response_model=LivroRespostas)
async def read_livro(livro_id: UUID, session: SessionDep) -> LivroRespostas:
    return await get_livro(livro_id, session)

@router.post("", response_model=LivroRespostas, status_code=201, responses={201: {"description": "Livro criado com sucesso"}})
async def create_livro(livro: LivroPostPut, session: SessionDep) -> LivroRespostas:
    livro_validado = Livro(
        titulo=livro.titulo,
        autor=livro.autor,
        editora=livro.editora,
        ano_publicacao=livro.ano_publicacao
    )

    session.add(livro_validado)
    session.commit()
    session.refresh(livro_validado)

    return LivroRespostas.model_validate(livro_validado)

@router.put("/{livro_id}", response_model=LivroRespostas, status_code=201, responses={201: {"description": "Livro atualizado com sucesso"}})
async def update_livro(livro: LivroPostPut, livro_id: UUID, session: SessionDep) -> LivroRespostas:
    
    livro_update = session.exec(select(Livro).where(Livro.uuid == livro_id)).first()

    if not livro_update:
        raise HTTPException(status_code=404,detail="Livro nao encontrado")

    livro_data = livro.model_dump()

    for key, value in livro_data.items():
        setattr(livro_update, key, value)

    session.add(livro_update)
    session.commit()
    session.refresh(livro_update)

    return LivroRespostas.model_validate(livro_update)


@router.patch("/{livro_id}", response_model=LivroRespostas, status_code=201, responses={201: {"description": "Livro atualizado com sucesso"}})
async def patch_livro(livro: LivroPatch, livro_id: UUID, session: SessionDep) -> LivroRespostas:
    
    livro_update = session.exec(select(Livro).where(Livro.uuid == livro_id)).first()

    if not livro_update:
        raise HTTPException(status_code=404,detail="Livro nao encontrado")

    livro_data = livro.model_dump(exclude_unset=True)

    for key, value in livro_data.items():
        setattr(livro_update, key, value)

    session.add(livro_update)
    session.commit()
    session.refresh(livro_update)

    return LivroRespostas.model_validate(livro_update)

@router.delete("/{livro_id}", response_model=ConfirmaDelete, status_code=201, responses={201: {"description": "Livro excluido com sucesso"}})
async def delete_livro(livro_id: UUID, session: SessionDep) -> ConfirmaDelete:
    
    livro_delete = session.exec(select(Livro).where(Livro.uuid == livro_id)).first()

    if not livro_delete:
        raise HTTPException(status_code=404,detail="Livro nao encontrado")
    
    livro_data = livro_delete.model_dump()
    
    session.delete(livro_delete)
    session.commit()

    return ConfirmaDelete(message=f"Livro {livro_data['titulo']} excluído com sucesso", uuid=livro_id)  