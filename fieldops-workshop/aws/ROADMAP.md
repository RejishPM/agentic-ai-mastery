# Live AWS integration checkpoints

These are planned integrations, not claims of deployed resources.

1. Bedrock: attach nova-inference-policy.json to fieldops-dev using an authorized IAM administrator. Replace the account wildcard with your account ID for tighter scoping. Verify one small Converse call using profile fieldops. No root keys.
2. Guardrails: create a guardrail denying instructions for bypassing safety interlocks; add sensitive information filters. Add ApplyGuardrail permission scoped to its ARN. Test allowed maintenance questions, prohibited requests, and false positives. Content filtering does not authorize tool calls.
3. Runtime: wrap the tested graph in the AgentCore runtime SDK entrypoint, build using the installed CLI's supported workflow, inspect all generated resources, then deploy. Execution role receives only required model and service permissions. Never package local AWS credentials.
4. Gateway: expose simulated read and draft tools through MCP. Verify authenticated MCP discovery and calls before removing local tools. Keep mutation approval in backend application logic.
5. Policy: create and attach a Cedar policy engine to Gateway in ENFORCE mode. Use the deployed Gateway's actual schema and tool action names. Test explicit allow, default deny, cross-site denial, and role denial. Client-provided role and site are not trusted claims.
6. Identity: distinguish inbound caller authentication from outbound delegated credentials. Derive principal and site from verified identity and server-side assignment. Do not accept actorId as authorization. Add an outbound mock-provider credential exercise only if needed; never commit secrets.
7. Memory: persist session events with principal-scoped namespaces, add a long-term strategy, test recall in a new session and isolation between two callers. Graph checkpointing and semantic memory solve different problems.
8. Observability: enable supported framework tracing, correlate request/session/tool spans, redact sensitive text, limit retention, inspect policy denials and failed tool calls.
9. Cleanup: record every created ARN and deployment stack. Remove only workshop-owned resources using the chosen deployment tool, verify deletion, and stop unused Codespaces compute.

## Completion evidence

Keep sanitized evidence of a local graph run, live model usage, Runtime invocation, MCP call, managed policy denial, approval resume, guardrail intervention, isolated memory recall, and trace inspection. Document exact tested package versions and any incomplete checkpoints.

## References

- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-cli-get-started.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-getting-started.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html
