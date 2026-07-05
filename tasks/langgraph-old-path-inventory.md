# LangGraph 旧线性路径迁移盘点

## 目的

这份文件记录旧架构中仍承担编排职责的模块和函数，给后续退役旧路径使用。当前项目处于 LangGraph 迁移期：普通文本消息优先进入 MVP message graph，部分工具和主动能力仍保留旧路径兼容。当前阶段不删除运行代码，只标注迁移策略。

## 状态分类

- `keep_adapter`：长期保留为外部系统适配层。
- `wrap_temporarily`：迁移期包装复用，后续可能替换。
- `replace_with_graph`：应迁移为 LangGraph 节点、工具或图入口。
- `remove_later`：等 graph 等价路径稳定后删除。

## 入口与适配层

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `__init__.py:private_msg` | 注册 nonebot 私聊消息监听 | keep_adapter | 保留为 QQ 入口。 |
| `__init__.py:handle_private_message` | 图片、表情、流程 session、文本入口分流 | wrap_temporarily | 逐步缩减为 event adapter + graph output executor。 |
| `adapters/onebot.py:event_to_inbound_message` | OneBot event 转 `InboundMessage` | keep_adapter | 作为新架构长期边界保留。 |
| `__init__.py:_send_event_reply` / `_send_private_reply` | QQ 消息发送与分片 | keep_adapter | 后续可移动到 `adapters/`，不属于智能编排。 |

## 普通文本消息编排

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `__init__.py:_process_text_message` | 真实 OneBot event 先走 MVP graph，工具型请求 fallback 旧 handler | wrap_temporarily | US-022 后减少 fallback 条件。 |
| `message_handler.py:MessageHandler.process_text` | 旧文本主编排：保存消息、提醒、日历、命令、记忆检索、prompt、LLM、摘要 | replace_with_graph | 拆成 graph nodes/tools/providers 后逐步退役。 |
| `message_handler.py:MessageHandler._call_llm` | 旧 LLM 与 web_search function calling 编排 | replace_with_graph | web search 迁移为 graph tool 后删除或缩减。 |
| `__init__.py:_GraphLLMAdapter` | 临时把旧 `LLMClient.chat` 接到 graph response node | wrap_temporarily | 后续移到专门 LLM adapter 模块。 |

## 记忆与上下文

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `__init__.py:_maybe_extract_memories` | 对话后自动抽取长期记忆 | wrap_temporarily | 迁移为 graph 后置节点或后台 memory job。 |
| `__init__.py:_handle_memory_management_command` | 记忆查看、删除、边界、偏好命令 | replace_with_graph | 迁移为 memory tool / command node。 |
| `__init__.py:_retrieve_timeline_for_turn` | 时间线检索 | replace_with_graph | 迁移进 `MemoryProvider`。 |
| `memory.py:MemoryStore` | SQLite 存储、消息、记忆、提醒底层持久化 | keep_adapter | 暂不重写数据库，先通过 provider/tool adapter 复用。 |
| `memory_graph/provider.py` | 新 graph memory provider contract | keep_adapter | 后续加入 `MemoryStore` adapter。 |

## 工具能力

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `reminders.py:ReminderService` | 本地提醒解析、创建、扫描、发送 | wrap_temporarily | 已有 `tools/reminder.py` 包装，后续让 graph tool path 接管创建。扫描发送仍保留。 |
| `tools/reminder.py` | graph reminder tool adapter | keep_adapter | 作为第一个真实 graph tool 迁移样板。 |
| `feishu_calendar.py` | 飞书日历解析与创建 | replace_with_graph | 迁移为 calendar tool descriptor + executor。 |
| `web_search.py` + `WEB_SEARCH_TOOL` | 旧 LLM function calling 搜索 | replace_with_graph | 迁移为 web_search tool descriptor + executor。 |
| `flows.py:FlowManager` | 多轮流程工具 session | wrap_temporarily | 短期保留，后续拆成 graph tool / subgraph。 |
| `content_fetcher.py:BilibiliFetcher` | 定时内容推送 | wrap_temporarily | 后续接 proactive graph 或独立 scheduled graph。 |
| `diary.py:DiaryWriter` | 每日日记生成 | wrap_temporarily | 后续接 scheduled graph。 |

## 主动行为

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `proactive.py:ProactiveChat.try_proactive` | 旧主动聊天调度入口 | replace_with_graph | 迁移到 `graphs/proactive.py` 后退役。 |
| `proactive.py:ProactiveChat._should_send` | 冷却、免打扰、忽略次数、活跃时间判断 | replace_with_graph | 拆为 proactive decision nodes。 |
| `proactive.py:ProactiveChat._select_topic` | 主动话题选择 | replace_with_graph | 拆为 candidate action node。 |
| `proactive.py:ProactiveChat._build_proactive_prompt` | 主动消息 prompt 构建 | replace_with_graph | 拆为 proactive prompt builder。 |
| `graphs/proactive.py` | 新保守 proactive graph skeleton | keep_adapter | 后续逐步接入真实上下文和发送决策。 |

## Prompt 与人格

| 位置 | 当前职责 | 分类 | 后续动作 |
| --- | --- | --- | --- |
| `prompt_builder.py:PromptBuilder` | 旧普通回复 prompt 编排 | wrap_temporarily | 逐步迁移到 `prompts/response.py` 和 graph state 输入。 |
| `personality.py` | 人格 system prompt | wrap_temporarily | 保留内容，改由 response prompt builder 消费。 |
| `turn_context.py` | 回合分析、情绪、回复模式、token 策略 | wrap_temporarily | 拆成 decision/context nodes 或 provider。 |
| `relationship.py` | 关系画像 prompt | wrap_temporarily | 后续接 memory provider 或 prompt builder。 |
| `knowledge.py` | 知识库检索与显化知识 prompt | wrap_temporarily | 后续接 memory/context provider。 |

## US-022 删除前条件

- 普通文本消息 graph 路径通过测试，并覆盖直接聊天、澄清、不回复。
- 至少提醒工具已可通过 graph tool routing + execution 端到端运行。
- 日历和搜索仍依赖旧 handler 时，不删除 `MessageHandler.process_text` 的对应分支。
- 图片、表情和 flow session 仍由旧入口处理时，不删除 `handle_private_message` 中对应分支。
- `MemoryStore` 只作为持久化 adapter 保留，不在本阶段重写数据库。

## 建议下一步

US-022 不应一次性删除整个 `MessageHandler`。建议先删除或绕过已被 graph 覆盖的普通 direct chat 编排，把提醒、日历、搜索、flow 等未迁移能力继续 fallback，直到各自迁移完成。
