# ADR-002: LLM Provider Abstraction

## Status

Accepted

## Context

Atlas needs to integrate with external LLM providers while avoiding application-level coupling to a specific vendor.

LLM providers expose different SDKs, authentication mechanisms, response format, and operational characteristics.

Directly integration a provider into the API layer would make future provider changes and testing more difficult.

## Decision

Atlas will define an internal 'LLMProvider' interface.

Provider-specific implementation will translate the internal request nand response contracts to and from the external provider's API.

The initial implementation are:

- Mock provider
- Azure OpenAI provider

## Consequences

### Positive

- Provider independence
- Easier testing
- Provider-specific logic remains
- Easier future provider additions
- Application code remains vendor-neutral

### Negative

- Additional abstaction
- Internal contracts must be maintained
- Provider-specific capabilities may require extensions to the abstraction

## Alteratnatives Considered

### Direct Azure OpenAI integration

Rejected because it would couple the application layer to a specific vendor and make testing more difficult.

### Generic third-party LLM abstraction

Not selected initially because Atlas should demonstrate control over its own application boundary and provider integration strategy.