from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nome do arquivo do nosso banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./devshowcase.db"

# O "motor" que vai executar os comandos no banco
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A "fábrica" de sessões (conexões temporárias para salvar/buscar dados)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe base que nossas tabelas vão herdar
Base = declarative_base()