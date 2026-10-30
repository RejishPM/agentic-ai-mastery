# FieldOps agent workshop

A Python learning project for an Oil & Gas maintenance workflow. All equipment,
readings, identities, and work orders are simulated. Nothing controls equipment
or writes to a real maintenance system.

## Implemented in this starter

- LangGraph workflow: authorized read -> model assessment -> draft -> approval interrupt.
- Nova Micro through Amazon Bedrock Converse, enabled only with `--live`.
- Local mock assessments by default, with no AWS calls.
- Deny-by-default Python authorization: site isolation, technician draft permissions,
  supervisor approval permission, and no shutdown action.
- Explicit human review; model output cannot grant approval or permissions.
- Optional attachment of an **existing** Bedrock Guardrail ID/version. This does not
  create a guardrail. Blocked model responses stop the workflow before drafting.

## Run in Codespaces

Use a dedicated Python 3.12 virtual environment for this project, independent of
the Codespace's default Python:

```bash
cd fieldops-workshop
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
python -m unittest discover -s tests -v
fieldops
fieldops --role supervisor
```

The default technician run pauses at a pending draft. The supervisor run asks
for `approve` or `reject` and updates only the in-memory simulation.

Demonstrate policy denial:

```bash
fieldops --equipment P-202 --site WEST
```

## Live Bedrock test (billable)

Authenticate the `fieldops` AWS profile, attach model-scoped inference permissions,
then run:

```bash
export AWS_PROFILE=fieldops
export AWS_REGION=us-west-2
export BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0
fieldops --live --role supervisor
```

One assessment makes one bounded Converse request with at most 300 output tokens.
Automatic SDK retries are disabled. This is a request bound, **not** an AWS billing
cap. Model and guardrail calls incur charges; Codespaces has its own billing.
No AWS resource is provisioned by this code.

To attach a configured guardrail with `bedrock:ApplyGuardrail` permission:

```bash
fieldops --live --guardrail-id YOUR_ID --guardrail-version YOUR_VERSION
```

## Architecture and boundaries

The graph chooses workflow steps; the LLM only writes an assessment. This first
milestone deliberately uses deterministic tool routing so we can test boundaries
before adding autonomous model-selected tools. IAM authorizes AWS API calls;
the local Python policy authorizes simulated business actions. Bedrock Guardrails
filters model content. Human approval is a separate control.

`--role` and `--site` are **demonstration identity inputs**. They are not secure
authentication and must never become caller-controlled production claims. A
production endpoint must derive the principal from a verified identity token,
then enforce authorization at each tool boundary. No HTTP endpoint is exposed.

LangGraph's checkpointer is in memory: pending approvals disappear when the
process exits. This starter supports same-process supervisor review; it does not
yet implement durable handoff from technician to a different supervisor.
Supervisor self-review is permitted in this simulation; separation of duties
would require creator/reviewer checks and durable records.

## Planned, not implemented

AgentCore Runtime deployment; Gateway MCP targets; managed AgentCore Policy/Cedar;
AgentCore Identity; scoped Memory; exported OpenTelemetry traces/Observability;
durable authenticated approvals; model-selected tool calling; adversarial guardrail
evaluation and production-safe secret management. See `aws/ROADMAP.md` for AWS stages.

Do not present the local Python authorization as deployed AgentCore Policy.
Do not commit AWS credentials, authorization codes, environment files, or tokens.
