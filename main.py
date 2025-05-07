import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

# Configuração de logs em memória
log_memory = []  # Lista para armazenar os logs em memória

# Função personalizada para registrar logs em memória
class MemoryLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_memory.append(log_entry)

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Exibe logs no console
    ]
)
memory_handler = MemoryLogHandler()
memory_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(memory_handler)

app = FastAPI()

class Livro(BaseModel):
    id: int = Field(gt=0, description="O ID deve ser um número positivo")
    titulo: str = Field(min_length=1, description="O título não pode estar vazio")
    autor: str = Field(min_length=1, description="O autor não pode estar vazio")

livros: List[Livro] = []

@app.get("/livros", summary="Listar todos os livros", description="Retorna todos os livros cadastrados com suporte à paginação.")
def listar_livros(skip: int = 0, limit: int = 10):
    logging.info("Listando livros com paginação: skip=%d, limit=%d", skip, limit)
    if not livros:
        logging.warning("Nenhum livro encontrado")
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    return livros[skip: skip + limit]

@app.get("/livros/{id}", summary="Buscar livro por ID", description="Retorna um livro específico pelo ID.")
def listar_livro_por_id(id: int):
    logging.info("Buscando livro com ID: %d", id)
    for livro in livros:
        if livro.id == id:
            return livro
    logging.error("Livro com ID %d não encontrado", id)
    raise HTTPException(status_code=404, detail=f"Livro com ID {id} não encontrado")

@app.get("/livros/buscar", summary="Buscar livros por título ou autor", description="Permite buscar livros pelo título ou autor.")
def buscar_livros(titulo: Optional[str] = None, autor: Optional[str] = None):
    logging.info("Buscando livros por título='%s' ou autor='%s'", titulo, autor)
    resultados = [livro for livro in livros if (titulo in livro.titulo if titulo else True) and (autor in livro.autor if autor else True)]
    if not resultados:
        logging.warning("Nenhum livro encontrado com os critérios fornecidos")
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado com os critérios fornecidos")
    return resultados

@app.post("/livros", summary="Adicionar um novo livro", description="Adiciona um livro ao catálogo.")
def adicionar_livro(livro: Livro):
    logging.info("Adicionando livro: %s", livro)
    for l in livros:
        if l.id == livro.id:
            logging.error("Livro com ID %d já existe", livro.id)
            raise HTTPException(status_code=400, detail=f"Livro com ID {livro.id} já existe")
    livros.append(livro)
    return {"message": "Livro adicionado com sucesso", "livro": livro}

@app.put("/livros/{id}", summary="Atualizar um livro", description="Atualiza as informações de um livro existente pelo ID.")
def atualizar_livro(id: int, livro_atualizado: Livro):
    logging.info("Atualizando livro com ID: %d", id)
    for index, livro in enumerate(livros):
        if livro.id == id:
            livros[index] = livro_atualizado
            return {"message": f"Livro com ID {id} atualizado com sucesso", "livro": livro_atualizado}
    logging.error("Livro com ID %d não encontrado para atualização", id)
    raise HTTPException(status_code=404, detail=f"Livro com ID {id} não encontrado")

@app.delete("/livros/{id}", summary="Deletar um livro", description="Remove um livro do catálogo pelo ID.")
def deletar_livro(id: int):
    logging.info("Deletando livro com ID: %d", id)
    for livro in livros:
        if livro.id == id:
            livros.remove(livro)
            return {"message": f"Livro com ID {id} deletado com sucesso"}
    logging.error("Livro com ID %d não encontrado para exclusão", id)
    raise HTTPException(status_code=404, detail=f"Livro com ID {id} não encontrado")

@app.get("/logs", summary="Acessar logs", description="Retorna os logs da aplicação.")
def acessar_logs():
    if not log_memory:
        logging.warning("Nenhum log encontrado")
        raise HTTPException(status_code=404, detail="Nenhum log encontrado")
    return {"logs": log_memory}

@app.get("/", summary="Homepage", description="Informações sobre a API e como utilizá-la.")
def homepage():
    logging.info("Acessando a homepage")
    return {
        "message": "Bem-vindo à API de Livros!",
        "descricao": "Esta API permite gerenciar um catálogo de livros. Você pode listar todos os livros, buscar um livro por ID, buscar por título ou autor, adicionar, atualizar e deletar livros.",
        "endpoints": {
            "listar_livros": "/livros (GET)",
            "listar_livro_por_id": "/livros/{id} (GET)",
            "buscar_livros": "/livros/buscar (GET)",
            "adicionar_livro": "/livros (POST)",
            "atualizar_livro": "/livros/{id} (PUT)",
            "deletar_livro": "/livros/{id} (DELETE)",
            "acessar_logs": "/logs (GET)"
        },
        "documentacao": "Acesse /docs para a documentação interativa (Swagger UI) ou /redoc para a documentação alternativa."
    }