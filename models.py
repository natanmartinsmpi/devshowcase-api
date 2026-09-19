from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Tabela de Junção
project_technology_association = Table(
    "project_technology",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("technology_id", Integer, ForeignKey("technologies.id"), primary_key=True)
)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telefone = Column(String(20))
    bio = Column(Text)
    github_url = Column(String(200))
    linkedin_url = Column(String(200))

    # O "atalho mágico": diz que um Perfil tem vários projetos
    projetos = relationship("Project", back_populates="perfil")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text)
    url_repositorio = Column(String(200))
    
    # A Chave Estrangeira: liga este projeto ao ID de um perfil
    perfil_id = Column(Integer, ForeignKey("profiles.id"))

    # O "atalho mágico" de volta: diz a qual perfil este projeto pertence
    perfil = relationship("Profile", back_populates="projetos")

    # CORRIGIDO: Nome da classe Feedback escrito corretamente
    feedbacks = relationship("Feedback", back_populates="projeto")

    # Linha para fazer o caminho de volta (agora o Python já conhece a tabela de junção)
    tecnologias = relationship("Technology", secondary=project_technology_association, back_populates="projetos")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    comentario = Column(Text, nullable=False)
    
    # 1. Crie a Chave Estrangeira apontando para a tabela de projetos (especificamente para o 'id')
    projeto_id = Column(Integer, ForeignKey("projects.id"))

    # 2. Crie o "atalho mágico" apontando para a classe do Projeto
    projeto = relationship("Project", back_populates="feedbacks")


# A Classe Technology
class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)

    # O "atalho mágico" que passa pela tabela de junção
    projetos = relationship("Project", secondary=project_technology_association, back_populates="tecnologias")