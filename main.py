import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List

import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

app = FastAPI()

# Métricas Prometheuss
REQUEST_COUNT = Counter("request_count", "Número de requisições recebidas", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Tempo de resposta das requisições", ["method", "endpoint"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)

    return response

from fastapi import Request

@app.get("/metrics", summary="Métricas Prometheus", description="Exibe métricas no formato Prometheus.")
async def metrics(request: Request):
    allowed_ips = ["127.0.0.1", "localhost", "host.docker.internal"]  # adicione outros IPs se necessário
    client_host = request.client.host
    if client_host not in allowed_ips:
        return Response(status_code=403, content="Forbidden")
    return Response(generate_latest(), media_type="text/plain")

log_memory = []  

class MemoryLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_memory.append(log_entry)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  
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

@app.get("/health", summary="Healthcheck da API", description="Retorna o status e métricas básicas da API.")
def health():
    return {
        "status": "ok",
        "total_livros": len(livros),
        "total_logs": len(log_memory),
        "mensagem": "API funcionando normalmente"
    }

@app.get("/logs", summary="Acessar logs", description="Retorna os logs da aplicação em formato HTML.", response_class=HTMLResponse)
def acessar_logs():
    if not log_memory:
        logging.warning("Nenhum log encontrado")
        raise HTTPException(status_code=404, detail="Nenhum log encontrado")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logs da Aplicação</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                color: #444;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background: #f9f9f9;
                margin: 10px 0;
                padding: 10px;
                border-left: 4px solid #007BFF;
                border-radius: 4px;
                font-size: 14px;
            }
            li:nth-child(odd) {
                background: #e9ecef;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Logs da Aplicação</h1>
            <ul>
    """
    for log in log_memory:
        html_content += f"<li>{log}</li>"
    html_content += """
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/", summary="Homepage", description="Informações sobre a API e como utilizá-la.", response_class=HTMLResponse)
def homepage():
    logging.info("Acessando a homepage")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bem-vindo à API de Livros</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                color: #444;
            }
            p {
                text-align: center;
                font-size: 16px;
                color: #666;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background: #f9f9f9;
                margin: 10px 0;
                padding: 10px;
                border-left: 4px solid #007BFF;
                border-radius: 4px;
                font-size: 14px;
            }
            li:nth-child(odd) {
                background: #e9ecef;
            }
            footer {
                text-align: center;
                margin-top: 20px;
                font-size: 14px;
                color: #888;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bem-vindo à API de Livros!</h1>
            <p>Esta API permite gerenciar um catálogo de livros. Você pode listar, buscar, adicionar, atualizar e deletar livros.</p>
            <h2>Endpoints Disponíveis</h2>
            <ul>
                <li><strong>Listar Livros:</strong> <code>/livros (GET)</code></li>
                <li><strong>Buscar Livro por ID:</strong> <code>/livros/{id} (GET)</code></li>
                <li><strong>Buscar Livros por Título ou Autor:</strong> <code>/livros/buscar (GET)</code></li>
                <li><strong>Adicionar Livro:</strong> <code>/livros (POST)</code></li>
                <li><strong>Atualizar Livro:</strong> <code>/livros/{id} (PUT)</code></li>
                <li><strong>Deletar Livro:</strong> <code>/livros/{id} (DELETE)</code></li>
                <li><strong>Acessar Logs:</strong> <code>/logs (GET)</code></li>
                <li><strong>Healthcheck:</strong> <code>/health (GET)</code></li>
            </ul>
            <p>Acesse a <a href="/docs">documentação interativa (Swagger UI)</a> ou a <a href="/redoc">documentação alternativa (ReDoc)</a>.</p>
        </div>
        <footer>
            Criado por Caio Gonçalves - 5º semestre
        </footer>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
