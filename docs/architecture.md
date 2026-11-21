# Architecture

## Components

| Component | Role |
|---|---|
| **Copilot Studio agent** | Conversational front end with generative orchestration. Decides which tool to call, combines results and explains the recommendation. Surfaced inside Microsoft 365 Copilot so agents do not need a new app. |
| **Instruction file** | About 8,000 characters defining the 8 target fields, the order to ask questions in, how to express confidence, and hard rules (recommend only, cite history, say when data is thin). |
| **Knowledge documents** | 5 reference documents (field definitions, code lists, trade and markup conventions). |
| **Starter prompts** | 8 prompts that show agents what to ask. |
| **Power Automate flows (3)** | Each flow exposes one lookup as a tool. Inputs are validated and passed as parameters to fixed T-SQL. |
| **Azure SQL** | A work-order table of about 96,000 rows covering about 5 years, refreshed daily from the ERP. |
| **Nightly verification** | A query with 9 flag types that compares each new work order against the history for its customer, site and trade. |

## Request flow

1. The agent asks for the customer and site. A lookup flow resolves them against history, handling inconsistent site names.
2. For each remaining field, the agent calls the history flows and receives counts and shares, not just a single answer.
3. The agent recommends a value with a confidence level based on how dominant it is for this customer and trade, and says when the history is too thin to recommend.
4. The contact centre agent confirms and enters the values in the ERP.

## Why flows instead of direct database access

- **Safety:** the model never writes SQL. Every query is fixed and parameterised.
- **Auditability:** each tool call is a flow run with inputs and outputs recorded.
- **Cost control:** fewer, better-shaped tool calls. Removing one redundant call cut credits per setup by about 23%.

## Handover

A 19-document handover pack covered configuration, the instruction file, each flow, the SQL, the verification rules, test cases and an operations runbook.
