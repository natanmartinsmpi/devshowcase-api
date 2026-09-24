from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

# Importando nossos próprios arquivos
import models
import schemas
from database import engine, SessionLocal

# 1. Cria as tabelas no banco de dados SQLite (se não existirem)
models.Base.metadata.create_all(bind=engine)

# 2. Inicia a aplicação FastAPI
app = FastAPI(title="DevShowcase API")

# --- TRATAMENTO GLOBAL DE ERROS ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": True, "mensagem_amigavel": f"Ops! {exc.detail}"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, # Converte validações padrão para erro 400
        content={"erro": True, "mensagem_amigavel": "Dados incorretos enviados na requisição.", "detalhes": exc.errors()}
    )

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

# --- GET AVANÇADO DE PROJETOS ---
@app.get("/api/projects", response_model=list[schemas.ProjectResponse])
def get_projects(skip: int = 0, limit: int = 10, tecnologia: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    
    # Se o utilizador pesquisou por tecnologia, aplica o filtro
    if tecnologia:
        query = query.join(models.Project.tecnologias).filter(models.Technology.nome.ilike(f"%{tecnologia}%"))
        
    # Devolve a lista com paginação
    return query.offset(skip).limit(limit).all()

# --- ENDPOINTS DA ATIVIDADE 2 ---

@app.post("/api/projects/{project_id}/feedbacks", response_model=schemas.FeedbackResponse, status_code=201)
def create_feedback(project_id: int, feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o projeto existe
    projeto = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # 2. Cria e salva o feedback
    novo_feedback = models.Feedback(**feedback.model_dump(mode="json"), projeto_id=project_id)
    db.add(novo_feedback)
    db.commit()
    db.refresh(novo_feedback)
    
    # 3. Recalcula a média do projeto
    todos_feedbacks = db.query(models.Feedback).filter(models.Feedback.projeto_id == project_id).all()
    soma_notas = sum([f.nota for f in todos_feedbacks])
    projeto.media_notas = soma_notas / len(todos_feedbacks)
    db.commit()
    
    return novo_feedback

@app.put("/api/projects/{project_id}/upvote", response_model=schemas.ProjectResponse)
def upvote_project(project_id: int, db: Session = Depends(get_db)):
    # 1. Procura o projeto na base de dados usando o ID da URL
    projeto = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    # 2. Se o projeto não existir, devolve um erro 404
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    # 3. Pega no valor atual de upvotes e soma +1
    projeto.upvotes += 1
    
    # 4. Guarda a alteração na base de dados
    db.commit()
    db.refresh(projeto)
    
    return projeto