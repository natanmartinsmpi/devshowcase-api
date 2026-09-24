from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional

# --- PROFILES ---
class ProfileCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None

class ProfileResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: Optional[str] = None

    class Config:
        from_attributes = True

# --- PROJECTS ---
class ProjectCreate(BaseModel):
    # O Field(..., min_length=1) garante que a string não pode ser vazia
    titulo: str = Field(..., min_length=1, description="O título não pode ser vazio")
    descricao: Optional[str] = None
    url_repositorio: Optional[HttpUrl] = None
    perfil_id: int # Obrigatório para sabermos de quem é o projeto

class ProjectResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    perfil_id: int
    upvotes: int
    media_notas: float

    class Config:
        from_attributes = True

# --- TECHNOLOGIES ---
class TechnologyCreate(BaseModel):
    nome: str = Field(..., min_length=1)

class TechnologyResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True

# --- SCHEMAS PARA FEEDBACK ---
class FeedbackCreate(BaseModel):
    nota: int = Field(..., ge=1, le=5, description="A nota deve ser entre 1 e 5")
    comentario: str = Field(..., min_length=3, description="O comentário deve ter no mínimo 3 caracteres")
class FeedbackResponse(BaseModel):
    id: int
    nota: int
    comentario: str
    projeto_id: int
    class Config:
        from_attributes = True