from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Importando nossos próprios arquivos
import models
import schemas
from database import engine, SessionLocal

# 1. Cria as tabelas no banco de dados SQLite (se não existirem)
models.Base.metadata.create_all(bind=engine)

# 2. Inicia a aplicação FastAPI
app = FastAPI(title="DevShowcase API")

# 3. Função auxiliar para abrir e fechar a conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. O NOSSO PRIMEIRO ENDPOINT: Criar Perfil
@app.post("/api/profiles", response_model=schemas.ProfileResponse, status_code=201)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    
    # Verifica se o email já existe no banco
    db_profile = db.query(models.Profile).filter(models.Profile.email == profile.email).first()
    if db_profile:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    
    # Transforma o DTO de entrada em um Modelo do Banco
    novo_perfil = models.Profile(**profile.model_dump(mode="json"))
    
    # Salva no banco de dados
    db.add(novo_perfil)
    db.commit()
    db.refresh(novo_perfil)
    
    # Retorna o perfil salvo (o FastAPI vai usar o ProfileResponse automaticamente)
    return novo_perfil

# Buscar perfil por ID
@app.get("/api/profiles/{profile_id}", response_model=schemas.ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    # O filtro compara a coluna ID do banco com o ID que veio na URL
    perfil_encontrado = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    
    if not perfil_encontrado:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
    return perfil_encontrado

# --- ENDPOINTS DE TECNOLOGIAS ---

# Cadastrar tecnologia
@app.post("/api/technologies", response_model=schemas.TechnologyResponse, status_code=201)
def create_technology(tech: schemas.TechnologyCreate, db: Session = Depends(get_db)):
    # Verifica se já existe uma tecnologia com esse nome
    db_tech = db.query(models.Technology).filter(models.Technology.nome == tech.nome).first()
    if db_tech:
        raise HTTPException(status_code=400, detail="Tecnologia já cadastrada.")
    
    nova_tech = models.Technology(**tech.model_dump(mode="json"))
    db.add(nova_tech)
    db.commit()
    db.refresh(nova_tech)
    return nova_tech

# Listar todas as tecnologias
@app.get("/api/technologies", response_model=list[schemas.TechnologyResponse])
def get_technologies(db: Session = Depends(get_db)):
    # O .all() traz todos os registros da tabela em formato de lista
    return db.query(models.Technology).all()

# --- ENDPOINTS DE PROJETOS ---

# Cadastrar projetos
@app.post("/api/projects", response_model=schemas.ProjectResponse, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    
    # Verifica se o perfil associado ao projeto realmente existe
    perfil = db.query(models.Profile).filter(models.Profile.id == project.perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil associado não encontrado.")
    
    # Salva o projeto
    novo_projeto = models.Project(**project.model_dump(mode="json"))
    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)
    return novo_projeto

# Listar todos os projetos
@app.get("/api/projects", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    # Traz todos os projetos
    return db.query(models.Project).all()