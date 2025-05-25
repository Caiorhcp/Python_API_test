# API de Livros - FastAPI + Prometheus + Grafana

Este projeto é uma **API para gerenciamento de um catálogo de livros**, desenvolvida em **FastAPI**.  
Inclui monitoramento com **Prometheus** e visualização de métricas com **Grafana**.

> **Trabalho de Faculdade**  
> Sistemas de Informação - 5º semestre  
> Autor: Caio Gonçalves

---

## Funcionalidades

- **CRUD de Livros**: Adicione, liste, busque, atualize e remova livros.
- **Logs**: Visualize logs da aplicação em HTML.
- **Healthcheck**: Endpoint `/health` para status e métricas básicas.
- **Métricas Prometheus**: Endpoint `/metrics` para monitoramento.
- **Dashboard Grafana**: Visualize requisições, latência e status HTTP.

---

## Endpoints Principais

- `GET /livros` — Lista todos os livros
- `GET /livros/{id}` — Busca livro por ID
- `GET /livros/buscar` — Busca por título ou autor
- `POST /livros` — Adiciona um novo livro
- `PUT /livros/{id}` — Atualiza um livro
- `DELETE /livros/{id}` — Remove um livro
- `GET /logs` — Visualiza logs da aplicação
- `GET /health` — Healthcheck da API
- `GET /metrics` — Métricas Prometheus

---

## Como rodar localmente

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd python_API
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a API**
   ```bash
   uvicorn main:app --reload
   ```

4. **Acesse**
   - API: [http://localhost:8000](http://localhost:8000)
   - Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Como rodar com Docker Compose (API + Prometheus + Grafana)

1. **Certifique-se de ter o Docker e Docker Compose instalados.**

2. **Execute:**
   ```bash
   docker-compose up --build
   ```

3. **Acesse:**
   - API: [http://localhost:8000](http://localhost:8000)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Grafana: [http://localhost:3000](http://localhost:3000)  
     (Usuário/senha padrão: admin/admin, ou conforme definido no docker-compose)

---

## Observações

- O endpoint `/metrics` pode ser protegido para acesso apenas pelo Prometheus.
- O dashboard do Grafana pode ser customizado conforme sua necessidade.
- Este projeto é um exemplo prático de integração de API REST com monitoramento moderno.

---

**Desenvolvido para fins acadêmicos — Sistemas de Informação, 5º semestre.**