# ADR-003: PostgresSQL and pgvector for Vector Storage

## Status

Accepted

## Context

Atlas requires vector storage for semantic document retrieval.

The platform already uses PostgresSQL for transactional application data.

A separate vector database could provide specialized vector-search capabilities but would introduce an additional infrastructure dependency.

## Decision

Atlas will initially use PostgresSQL with the pgvector extension for vector storage and similarity search.

## Rationale

This provides:

- a single persistence platform
- transactional consistency
- relational metadata filtering
- simpler local development
- reduced infrastructure complexity

The retrieval abstraction allows a dedicated vector database to be introduced later if scale or performance requirements justify it.

## Consequences

### Positive

- Reduced operational complexity
- Simple local development
- Shared transactional database
- Strong metadata filtering
- Easy integration with existing SQLAlchemy models

## Negative

- Vector search and transactional workloads share infrastructure
- Very large-scale workloads may require a specialized vector store
- Vector performance must be monitored as the dataset grows

## Alternatives Considered

### Dedicated vector database

Examples include Qdrant, Pinecone, Weaviate, and Milvus.

Not selected initially because the expected scale does not justify the additional infrastructure complexity.