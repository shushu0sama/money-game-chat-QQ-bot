# PRD: QQ Chat Bot LangGraph 新架构改造

## Current implementation status

This PRD is the architecture plan for the LangGraph migration, not a snapshot of fully completed work. The repository currently has the MVP graph packages in place (`adapters/`, `graphs/`, `state/`, `nodes/`, `tools/`, `memory_graph/`) and normal text messages are routed through the MVP message graph before falling back to legacy paths when needed.

Implemented or partially implemented:
- Typed graph state and graph output models.
- OneBot event normalization into graph input.
- MVP message graph for input normalization, context loading, reply decision, response generation, and output finalization.
- Reply policies for direct reply, no reply, clarification, and tool-needed decisions.
- Graph diagnostics and graph-focused tests that run without a live QQ bot.
- Tool registry, tool routing, tool execution nodes, and a reminder graph adapter.
- Proactive graph skeleton with conservative/no-op behavior.

Still in migration:
- Calendar, web search, flow tools, some memory management commands, and mature proactive behavior still rely on legacy handler paths.
- `MessageHandler` remains as a compatibility path for tool-like requests until graph equivalents are stable.
- Old orchestration should be retired incrementally, not deleted in one pass.

## Introduction

当前 QQ Chat Bot 使用较简易的线性架构，随着长期记忆、主动聊天、提醒、日历、搜索、工具调用和人格策略等能力增加，现有结构已经难以清晰扩展。新增功能时需要在 handler、LLM 调用、上下文拼接和工具逻辑之间交叉修改，导致行为难以预测、测试困难、回归风险高。

本次改造的目标是将 bot 核心推翻重建为基于 LangGraph 的智能体架构。nonebot 继续作为 QQ 消息入口和事件适配层，核心智能行为迁移到 LangGraph graph 中，通过显式状态模型、节点、边、条件路由和可测试的执行链路，让 bot 能在陪伴、主动行为和工具助理之间根据场景切换。

## Goals

- 建立以 LangGraph 为核心的 bot 智能体执行框架。
- 将 QQ 事件接入层与智能体决策层解耦。
- 定义统一的 graph state，用于承载用户消息、会话上下文、记忆检索结果、工具意图、回复策略和执行结果。
- 支持分阶段迁移旧功能，允许旧架构能力逐步替换，但最终核心逻辑不依赖旧线性 handler。
- 降低新增工具、节点和行为策略的成本。
- 让关键智能行为可以通过单元测试和集成测试验证。
- 形成 MVP / Phase 2 / Phase 3 的长期蓝图，后续可转换为 Ralph 可执行 stories。

## User Stories

### US-001: Define LangGraph architecture boundaries
**Description:** As a developer, I want a clear boundary between nonebot event handling and LangGraph agent execution so that future features are added to the graph instead of scattered across handlers.

**Acceptance Criteria:**
- [ ] Document that nonebot handles QQ event adaptation only.
- [ ] Document that LangGraph owns message analysis, memory use, tool routing, reply decision, and response generation.
- [ ] Define module boundaries for event adapter, graph builder, graph state, nodes, tools, and persistence adapters.
- [ ] Identify old modules that are migration references rather than long-term architecture constraints.
- [ ] Typecheck passes.

### US-002: Create core graph state model
**Description:** As a developer, I want a typed graph state model so that every LangGraph node reads and writes predictable fields.

**Acceptance Criteria:**
- [ ] Define state fields for incoming event metadata, normalized user message, conversation context, memory results, intent classification, tool plan, reply policy, generated response, and diagnostics.
- [ ] State model supports both normal QQ message handling and future proactive tasks.
- [ ] State model avoids direct dependency on nonebot event objects outside the adapter layer.
- [ ] Tests cover state initialization from a normalized message.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-003: Build MVP message graph skeleton
**Description:** As a bot maintainer, I want a minimal LangGraph message graph so that a QQ message can flow through structured nodes before producing a reply.

**Acceptance Criteria:**
- [ ] Implement graph builder for the MVP message graph.
- [ ] MVP graph includes nodes for input normalization, context loading, intent/reply decision, response generation, and output finalization.
- [ ] Graph can be invoked from a simple Python test without starting nonebot.
- [ ] Graph returns a structured result that includes whether to reply and the final reply text if applicable.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-004: Integrate nonebot entrypoint with LangGraph MVP
**Description:** As a QQ user, I want messages to be processed by the new LangGraph pipeline so that future bot behavior comes from the new intelligent architecture.

**Acceptance Criteria:**
- [ ] nonebot message handler converts raw QQ events into normalized graph input.
- [ ] Handler invokes the LangGraph MVP message graph.
- [ ] Handler sends a QQ reply only when graph output says a reply should be sent.
- [ ] Existing essential behavior is preserved for basic direct chat messages.
- [ ] Errors are logged with graph diagnostics but do not expose internal traces to QQ users.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-005: Add reply decision node
**Description:** As a QQ user, I want the bot to decide when to answer, stay quiet, ask a follow-up, or use tools so that it behaves less mechanically.

**Acceptance Criteria:**
- [ ] Reply decision node classifies at least: reply now, no reply, ask clarification, tool-needed.
- [ ] Decision uses normalized message, recent context, and available memory summary fields.
- [ ] Decision result is written to graph state in a typed structure.
- [ ] Tests cover direct mention, casual message, ambiguous request, and tool-like request.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-006: Add memory retrieval node interface
**Description:** As a QQ user, I want the bot to use relevant prior context so that conversations feel continuous rather than isolated.

**Acceptance Criteria:**
- [ ] Define a memory retrieval node with a stable input/output contract.
- [ ] Node can initially wrap existing memory logic if available, but graph state must not expose old implementation details.
- [ ] Memory output distinguishes recent context, durable user facts, preferences, and candidate topic continuations.
- [ ] Tests can run with a fake memory provider.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-007: Add tool routing node interface
**Description:** As a bot maintainer, I want tool routing to be represented as graph logic so that adding reminders, calendar, search, and future tools does not require editing the main handler.

**Acceptance Criteria:**
- [ ] Define a tool registry interface for available tools.
- [ ] Define a tool routing node that produces a tool plan instead of directly executing arbitrary code.
- [ ] Tool plan includes tool name, arguments, confidence, and whether user confirmation is required.
- [ ] Tests cover routing to at least one fake tool and declining when no tool fits.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-008: Add response generation node
**Description:** As a QQ user, I want the bot response to combine message intent, memory, tool results, and persona rules so that replies are coherent and context-aware.

**Acceptance Criteria:**
- [ ] Response generation node receives only graph state fields, not raw nonebot events.
- [ ] Node supports normal reply, clarification question, and tool-result reply modes.
- [ ] Prompt construction is isolated behind a function or class that can be unit tested.
- [ ] Tests verify that generated prompt inputs include relevant memory and exclude unavailable fields.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-009: Add proactive behavior graph skeleton
**Description:** As a bot maintainer, I want proactive behavior to have its own graph entrypoint so that scheduled checks and主动关心 are not hacked into normal message handling.

**Acceptance Criteria:**
- [ ] Define a separate proactive graph entrypoint for scheduled or background events.
- [ ] Proactive state includes trigger reason, user context, recent interaction state, candidate action, and final decision.
- [ ] MVP proactive graph can decide no-op without sending a message.
- [ ] Proactive graph does not send QQ messages directly; it returns an action for the adapter to execute.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-010: Add observability for graph execution
**Description:** As a developer, I want graph execution diagnostics so that failed or strange bot behavior can be debugged by looking at node decisions.

**Acceptance Criteria:**
- [ ] Each graph run has a run id.
- [ ] Diagnostics include visited nodes, major decisions, selected tool plan, and final reply policy.
- [ ] Logs avoid storing secrets or full sensitive user content unless already allowed by existing project policy.
- [ ] Tests verify diagnostics are attached to graph output.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-011: Migrate existing tool capabilities into graph tools
**Description:** As a QQ user, I want existing reminders, calendar, search, and related assistant capabilities to continue working under the LangGraph architecture.

**Acceptance Criteria:**
- [ ] Existing tool-like functions are inventoried and mapped to graph tool registry entries.
- [ ] At least one existing tool is migrated end-to-end through tool routing, execution, and response generation.
- [ ] Tool execution result is represented in graph state.
- [ ] Regression tests cover the migrated tool path.
- [ ] Typecheck passes.
- [ ] Tests pass.

### US-012: Retire old linear orchestration path
**Description:** As a maintainer, I want old orchestration code removed or reduced to adapters so that future behavior is not split between two architectures.

**Acceptance Criteria:**
- [ ] Identify old code paths replaced by LangGraph.
- [ ] Remove or isolate obsolete orchestration logic after equivalent graph paths pass tests.
- [ ] Keep only compatibility adapters where necessary for nonebot integration or persistence.
- [ ] Tests verify the active message handler uses LangGraph path.
- [ ] Typecheck passes.
- [ ] Tests pass.

## Functional Requirements

- FR-1: The system must use LangGraph as the primary orchestration layer for bot intelligence.
- FR-2: The nonebot layer must only adapt QQ events into normalized graph inputs and execute final graph outputs.
- FR-3: The graph state must be typed and independent from raw nonebot event classes.
- FR-4: The MVP message graph must support at least input normalization, context loading, reply decision, response generation, and output finalization.
- FR-5: The architecture must allow old functions to be wrapped temporarily during migration, but graph contracts must not depend on old module internals.
- FR-6: The reply decision node must explicitly decide whether to reply, stay silent, ask clarification, or route to tools.
- FR-7: The memory node must produce structured memory output rather than unstructured prompt text only.
- FR-8: The tool routing node must produce a structured tool plan before tool execution.
- FR-9: Tool execution must be separated from tool selection.
- FR-10: Response generation must consume graph state and produce a final reply candidate.
- FR-11: Proactive behavior must use a separate graph entrypoint rather than being mixed into message handling.
- FR-12: Every graph run must expose diagnostics useful for debugging and tests.
- FR-13: Tests must be able to invoke graph code without starting a live QQ bot.
- FR-14: The migration must be staged so that each phase leaves the bot runnable.

## Non-Goals

- This project will not migrate away from nonebot as the QQ adapter in the first version.
- This project will not build a web admin UI or visual graph editor in the first version.
- This project will not add a new LLM provider as part of the architecture MVP.
- This project will not become a generic multi-tenant SaaS bot platform.
- This project will not require all old features to be migrated in the first MVP milestone.
- This project will not optimize for perfect proactive behavior before the basic graph architecture is stable.

## Design Considerations

- The bot should behave as a hybrid companion and assistant.
- In casual conversation, it should prioritize continuity, emotional appropriateness, and not over-answering.
- In task-like requests, it should prioritize intent recognition, tool selection, confirmation when needed, and reliable execution.
- In proactive scenarios, it should be conservative by default and avoid sending unnecessary messages.
- Graph output should distinguish between internal reasoning artifacts and user-visible messages.

## Technical Considerations

- LangGraph should be introduced as a core dependency and isolated behind project-owned graph builder modules.
- Suggested module layout:
  - `adapters/`: nonebot event normalization and QQ output execution.
  - `graphs/`: graph builders and graph entrypoints.
  - `state/`: typed graph state and output models.
  - `nodes/`: reusable LangGraph nodes.
  - `tools/`: tool registry, tool schemas, and tool executors.
  - `memory/`: memory provider interfaces and adapters.
  - `prompts/`: prompt construction for reply and decision nodes.
- Existing modules can be wrapped during migration, but new graph-facing interfaces should be clean and explicit.
- Tests should prefer fake memory providers, fake LLM clients, and fake tools for deterministic graph behavior.
- The final architecture should make it easy to add a new tool by registering it and adding tests, not by editing the main QQ message handler.

## Phasing

### MVP: LangGraph foundation

MVP should establish the new skeleton without requiring every old feature to be migrated.

Included:
- Typed graph state.
- MVP message graph.
- nonebot-to-graph adapter.
- reply decision node.
- basic response generation node.
- diagnostics.
- tests that invoke graph without live QQ.

Not required in MVP:
- Full proactive behavior.
- Full migration of every existing tool.
- Perfect long-term memory behavior.
- Removal of every old module.

### Phase 2: Memory and tools migration

Included:
- Structured memory retrieval node.
- Tool registry and tool routing node.
- Tool execution node.
- Migration of reminders, calendar, search, and other existing tools.
- Regression tests for migrated capabilities.

### Phase 3: Proactive intelligence and old path retirement

Included:
- Proactive graph entrypoint.
- Conservative proactive decision policy.
- Relationship/topic continuation logic.
- Better diagnostics for graph decisions.
- Removal or isolation of old linear orchestration paths.

## Success Metrics

- A new developer can understand the main message flow by reading the graph builder and state model rather than tracing multiple handlers.
- A new tool can be added through the tool registry and tests without editing the main QQ message handler.
- Core message graph tests run without launching nonebot.
- Basic direct chat still works after MVP integration.
- The bot can explicitly decide no reply, normal reply, clarification, or tool route.
- Existing key tool capabilities can be migrated one by one without blocking the whole rearchitecture.

## Open Questions

- Which existing features are mandatory to preserve in MVP direct chat behavior?
- Should graph state use Pydantic models, TypedDict, dataclasses, or a mixed approach?
- Which LangGraph persistence/checkpoint mechanism should be used for conversation continuity?
- Should tool execution happen inside the graph or through an adapter after graph planning for the first version?
- What is the minimum acceptable proactive behavior before old proactive logic is retired?
- Which test runner/type checker commands should Ralph use as the standard verification gate?
