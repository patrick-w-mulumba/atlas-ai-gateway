# atlas-ai-gateway

Production-oriented enterprise AI gateway built around a grounded
Retrieval-Augmented Generation (RAG) architecture.

Atlas provides a clean service boundary to between client applications, 
retrieval infrastructure, embedding providers, and LLM providers.

The project is designed to demonstrate production-oriented AI engineering practices including provider abstraction, 
vector search, request validation, observability, graceful resource management, and automated testing.

---

## Overview

Atlas AI Gateway exposes an API for querying enterprise knowledge using Retrieval-Augmented Generation

A typical request flows through:

Client
  ↓
FastAPI
  ↓
RAGService
  ↓
Embedding Provider
  ↓
PgVectorRetriever
  ↓
PostgreSQL + pgvector
  ↓
Retrieved Context
  ↓
LLM Provider
  ↓
Grounded Response

The Architecture deliberately separates retrieval and generation providers so that the system can operate with 
deterministic mock providers during the development and integrate with production LLM providers such as Azure OpenAI.

---

## Key Capabilities

- Retrieval-Augmented Generation (RAG)
- PostgreSQL + pgvector retrieval
- Metadata filtering
- Configurable relevance thresholds
- LLM provider abstraction
- Embedding provider abstraction
- Azure OpenAI integration
- Deterministic mock providers for development and testing
- FastAPI request validation
- Structured API error responses
- OpenTelemetry distributed tracing
- Jaeger trace visualization
- Trace/span correlation in application logs
- Health and readiness endpoints
- Graceful application shutdown
- Docker Compose development infrastructure
- Automated unit and integration testing
- 90% test coverage

---

## Technology Stack

| Component | Technology |
|---|---|
|API| FastAPI|
|Language| Python|
|Database| PostgreSQL|
|Vector Search | pgvetor|
|Cache | Redis |
|LLM | Azure OpenAI / Mock |
|Embeddings | Configurable provider|
|ORM | SQLAlchemy|
| Validation | Pydantic |
| Observability | OpenTelemetry |
| Tracing  | Jaeger |
| Containers | Docker Compose | 
| Testing | Pytest |
| Coverage | pytest-cov |

---

## Achitecture

                        ┌─────────────────┐
                        │     Client      │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     FastAPI     │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    RAGService   │
                        └───────┬─┬───────┘
                                │ │
                  ┌─────────────┘ └──────────────┐
                  ▼                              ▼
        ┌──────────────────┐          ┌──────────────────┐
        │ EmbeddingProvider│          │  LLM Provider    │
        └────────┬─────────┘          └────────┬─────────┘
                 │                             │
                 ▼                             ▼
        ┌──────────────────┐          ┌──────────────────┐
        │ PgVectorRetriever│          │ Azure OpenAI     │
        └────────┬─────────┘          │ / Mock Provider  │
                 │                    └──────────────────┘
                 ▼
        ┌──────────────────┐
        │ PostgreSQL       │
        │ + pgvector       │
        └──────────────────┘

                 OpenTelemetry
                       │
                       ▼
                    Jaeger
                    
---

## Project Structure

---

## Local Development

### Prerequisites
- Python 3.12+
- Docker
- Docker Compose
- Git


### Environment Configuration

Copy the example environment variable

```cp .env.example .env ```

The default development configuration uses deterministic mock providers:

``` 
LLM_PROVIDER=mock 
EMBEDDING_PROVIDER=mock
```

Azure OpenAI cna be enabled by configuring:
```
LLM_PROVIDER=azure-openai

AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-10-21
```
NEVER commit API keys or other secrets to source control.

### Start Infrastructure

Atlas uses Docker Compose for local infrastructure

Start PostgreSQL, Redis. and Jaeger:

```docker compose up -d ```

Chech the service status

``` docker compose ps ```

#### Infrastructure
|Service| Port|
|---|---|
|PostgreSQL | 5432|
| Redis | 6379 |
| Jaeger UI | 16686 |
| OTLP gRPC | 4317 |
| OTLP HTTP | 4318|

---

### Run the API

Install the dependencies

```commandline
pip install -e .
```

Start the application 

``` uvicorn app.main:app --reload```

API:


```http 
http://localhost:8000
```

Swagger/OpenAPI:

```http
http://localhost:8000/docs 
```

## Database Config

Make sure that the Database has vector database accept vector db commands
```commandline
docker exec -it atlas-postgres psql -U atlas -d atlas
```
Check if vector extension is enabled

```SQL
CREATE EXTENSION IF NOT EXISTS vector;
```

Run Alembic migrations

```commandline
alembic upgrade head
```



## API

### RAG Query

``` POST /rag/query ```

Example:

```json
{
  "question": "How long do customers have to request a refund?",
  "top_k": 5,
  "messages": [
    {"role": "user", "content": "Hello Atlas"}],
  "filters": {}
}
```

The response contains the generated answer and the sources used to produce it.

### Health

```http request
GET /health
```
Used to determine whether the application process is alive.

### Readiness

```http request
GET /readiness
```
Checks the application dependencies including PostgreSQL and Redis.

A healthy application returns :

```http request
200 OK
```

while an unavailable dependency results in:
```http request
503 Services Unavailable
```

---

### RAG Pipeline

The RAG pipeline consists of:
1. Validate the incoming request.
2. Generate an embedding for the question.
3. Perform vector similarity search using pgvector.
4. Apply metadata filters where provided.
5. Apply the configured minimum relevance threshold.
6. Construct grounded context.
7. Send the context and question to the configured LLM provider.
8. Return the generated answer and source metadata.

The system explicitly avoids generating answers from irrelevant retrieved context.

---

## LLM Provider Architecture

Atlas uses a provider abstraction to separate the RAG orchestration layer from the underlying LLM implementation

```text
LLMProvider
   │
   ├── MockLLMProvider
   │
   └── AzureOpenAIProvider
```
This allows:
- deterministic local development
- fast unit testing
- provider-independent RAG orchestration
- production Azure OpenAI integration

---

## Observability

Atlas uses OpenTelemetry for distributed tracing.

Enable tracing:

```yaml
OTEL_ENABLED=true
OTEL_ENDPOINT=http://localhost:4318/v1/traces
```

Jaeger UI:
```yaml
http://localhost:16686
```
RAG requests produce traceable operations covering areas such as 
- embedding
- retrieval
- generation

Application logs include:
```commandline
trace_id
span_id
```
allowing logs and Jaeger traces to be correlated.

---

## Testing

Run the complete test suite:

```commandline
pytest
```

Run with coverage:

```commandline
pytest --cov=app --cov-report=term-missing
```
Current test coverage:
```commandline
90%
```
The test suite includes:
- unit tests
- provider tests
- RAG service tests
- pgvector retrieval tests
- configuration tests
- logging tests
- lifecycle tests
- API tests
- end-to-end RAG integration tests

---

## Docker Infrastructure

The development environment is defined in 
```commandline
docker-compose.yml
```
Services include:
- PostreSQL with pgvevtor
- Redis
- Jaeger

Persistent data is stored using Docker volumes for PostgreSQL and Redis.

## Production Considerations

Atlas includes several production-oriented design decisions:
- Configuration through environment variables
- provider abstraction
- request validation
- bounder resource usage
- relevance thresholds
- structured error
- health/readiness separation
- graceful database shutdown
- OpenTelemetry lifecycle management
- trace/log correlation
- automated testing
- Docker-based infrastructure

Secrets should be supplied through a secure secret-management mechanism in production 
rather than committed configuration files

## Roadmap

Potential future improvements include:
- production authentication/authorization
- rate limiting
- streaming LLM responses
- additional LLM providers
- additional embedding providers
- Redis-backed cachine
- asynchronous ingestion workers
- richer metadata filtering
- evaluation datasets and RAG quality metrics
- CI/CD pipeline
- production Kubernetes deployment
