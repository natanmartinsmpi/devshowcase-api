from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nome do arquivo do nosso banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres.joioddbsyjjdglojxduc:JA25piNS38sm50@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

# O "motor" que vai executar os comandos no banco
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# A "fábrica" de sessões (conexões temporárias para salvar/buscar dados)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe base que nossas tabelas vão herdar
Base = declarative_base()