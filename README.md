# 艾琳娜 — Money Game Chat QQ Bot

一个具备哲学内核的 QQ 个人陪伴机器人。不只是聊天——它懂一本特定的书，能带你走书里的工具，记得你说过的话，会主动关心你，还能帮你记日记。

当前项目基于 **NoneBot2 + OneBot V11 + LangGraph + DeepSeek V4-Pro**。NoneBot 负责 QQ 事件接入，LangGraph 正在逐步接管消息决策、回复生成、工具路由和主动行为编排；迁移期内，部分成熟能力仍由旧 handler 兼容承载。

## 为什么叫「艾琳娜」

> "我并不想成为一个高高在上的导师或者工具人。我就是一个坐在你旁边的朋友——有时候话多，有时候话少，有时候只想说一句「懂了」。" ——艾琳娜

## 与普通 ChatBot 的不同

| | 普通 QQ Bot | 艾琳娜 |
|---|---|---|
| 人格 | 一个固定的 system prompt | **6 种随机情绪状态**，30% 概率每轮切换，有口语和口癖 |
| 知识 | 泛泛的通用知识 | **内置一本书的完整哲学体系**（12 个概念 + 情境映射） |
| 引导 | "你可以试试放松一下" | **交互式流程工具**，一步步带你走书里的实操方法 |
| 记忆 | 记不住或靠 RAG | **SQLite 长期记忆 + 时间线记忆 + 可控边界/偏好**，记住偏好、经历、情绪模式，也能按具体日期回忆旧事 |
| 主动性 | 被动回复 | **主动问候 + 主题选择器 + B 站视频推荐**，有活跃时段、冷却机制、勿扰保护和暂停/恢复控制 |
| 日记 | 无 | **每天午夜自动生成个人日记**，三段式 Markdown 格式 |
| 回复决策 | 规则散落在消息处理里 | **LangGraph 消息图**统一判断回复、不回复、澄清追问和工具路由 |
| 多用户 | 消息混淆 | **按 QQ 号隔离**，每个人的记忆和日记完全独立 |

## 当前架构状态

项目正在从旧的线性 `MessageHandler` 迁移到 LangGraph 架构：

```text
QQ / OneBot 事件
  -> NoneBot 适配层
  -> InboundMessage 标准化输入
  -> LangGraph GraphState
  -> 输入、上下文、决策、回复、工具等节点
  -> GraphOutput
  -> NoneBot 发送回复或保持沉默
```

当前状态：

- 普通文本消息优先进入 LangGraph MVP 消息图。
- 消息图已覆盖直接回复、不回复、澄清追问和工具意图识别。
- 提醒工具已有 graph adapter，并有工具路由和工具执行节点测试覆盖。
- 日历、网页搜索、流程工具、部分记忆管理和主动推送仍保留旧路径作为迁移期兼容能力。
- `MessageHandler` 仍承担部分成熟工具和旧编排职责，后续会逐步缩减为适配器或被 graph 节点/工具替代。

## 核心功能

### 1. 人格系统

艾琳娜有 6 种情绪状态，按权重随机滚动：

```text
正常(35%)  话少/累(20%)  话多/兴奋(15%)
摆烂模式(15%)  温柔感性(10%)  有点烦(5%)
```

每次对话有 30% 概率切换状态。回复会带有口语感和情绪惯性，而不是固定模板。

### 2. 哲学知识库

内置罗伯特·沙因费尔德《你值得过更好的生活》（*Busting Loose from the Money Game*）的 12 个核心概念：

```text
全息图 · 金钱游戏 · 第一阶段与第二阶段
赞赏感谢 · 流程工具 · 迷你流程 · 让话语充满力量
彩蛋 · 能量场 · 彻底解脱点 · 电影隐喻 · 大我
```

知识库通过关键词和情境映射参与 prompt 构建，让回复自然带出相关视角，而不是说教式输出。

### 3. 交互式流程工具

当用户说「陪我走流程」等触发语时，艾琳娜会进入引导模式，带用户完成书中的实操方法：

```text
步骤 1：正面迎击 — 找到身体里的不适感
步骤 2：彻底感受 — 放大它，不逃避
步骤 3：说出真相 — 在感受最强时宣告真相
步骤 4：收回力量 — 把情绪能量转化为自己的力量
步骤 5：绽放自己 — 切换到无限存有的视角
步骤 6：赞赏感谢 — 感谢这个体验带给你的礼物
```

还支持「迷你流程」和「赞赏感谢」练习。用户可以随时退出，流程 session 有超时清理。

### 4. 长期记忆

SQLite 记忆系统按 QQ 用户 ID 隔离，支持：

| 机制 | 说明 |
|---|---|
| 显式记忆 | 说「记住：我养了一只猫」后写入长期记忆 |
| 自然边界/偏好 | 识别「以后晚上别提醒我任务」「我希望你回复短一点」等偏好 |
| 记忆管理 | 支持查看、删除、结束事项、避免重复提及等管理命令 |
| 自动提取 | 周期性从对话中提取事实并去重 |
| 关键词检索 | 使用 jieba 分词和模糊匹配召回相关记忆 |
| 时间线记忆 | 自动记录带日期的事件，支持按具体日期回忆旧事 |
| 对话摘要 | 周期性摘要历史上下文，压缩长期对话记录 |

### 5. 主动推送

主动能力目前由旧主动系统承载，新 proactive graph 已有骨架和测试，后续会逐步接管。

当前主动能力包括：

- 对话式问候：定期检查是否适合主动关心，遵守活跃时段、冷却、勿扰和暂停/恢复控制。
- 主题选择器：在轻问候、进行中的事、显化 check-in、频率急救等主题之间保守选择。
- B 站内容推送：定期拉取热门/知识/科技区内容，用兴趣匹配和 LLM 推荐语筛选推送。

### 6. 每日日记

每天午夜自动将当天对话整理为个人日记：

```markdown
# 2026年05月13日 日记

## 聊聊
- 上午你分享了工作中的一个困惑...

## 今日心情
整体来看你今天状态偏放松...

## 艾琳娜的碎碎念
感觉你今天比上周更愿意聊自己的感受了...
```

日记按用户分目录存储：`diaries/{user_id}/YYYY-MM-DD.md`。

### 7. LangGraph 消息图

普通文本消息会先进入 LangGraph MVP 消息图。图中按顺序完成输入标准化、上下文加载、回复决策、回复生成和输出整理。

当前图能明确区分：

```text
reply_now          直接生成回复
no_reply           不打扰、不补话
ask_clarification  信息不足时先追问
tool_needed        进入工具计划或迁移期 fallback
```

图相关模块包括：

- `adapters/`：OneBot event 到 graph 输入的适配。
- `graphs/`：消息图和主动行为图入口。
- `state/`：图状态、输入/输出模型和 diagnostics。
- `nodes/`：输入、上下文、记忆、决策、回复、工具节点。
- `tools/`：Graph 工具注册表和工具 adapter。
- `memory_graph/`：Graph 记忆 provider 契约。

### 8. 网页搜索、日历和提醒

- 网页搜索：旧路径通过 DeepSeek function calling 判断是否搜索，默认 Bing CN 后端，支持页面正文抓取和失败回退。
- 飞书日历：旧路径负责日程解析和创建，后续计划迁移为 graph calendar tool。
- 提醒：底层提醒服务保留，graph reminder adapter 已作为工具迁移样板。

### 9. 多用户隔离

多人同时私聊时，每个人的消息、记忆、日记和主动记录都按 QQ 号隔离。

## 项目结构

```text
money-game-chat-QQ-bot/
├── 启动艾琳娜.bat                       # 一键启动 NapCat + Bot
├── bot.py                              # NoneBot 入口
├── .env.example                        # 配置模板
├── pyproject.toml                      # 项目依赖声明
├── tests/                              # 单元测试、图测试、工具测试和 UX 回归测试
├── tasks/                              # PRD、迁移盘点和任务文档
└── nonebot_plugin_personal_companion/
    ├── __init__.py                     # NoneBot 适配层、启动初始化和迁移期兼容包装
    ├── adapters/                       # OneBot event -> graph 输入适配
    ├── graphs/                         # LangGraph 消息图和主动行为图
    ├── state/                          # 图状态、输入/输出模型和 diagnostics
    ├── nodes/                          # 输入、上下文、记忆、决策、回复、工具节点
    ├── tools/                          # Graph 工具注册表和提醒工具 adapter
    ├── memory_graph/                   # Graph 记忆 provider 契约
    ├── prompts/                        # YAML prompt 和 graph response prompt 构建
    ├── services.py                     # AppServices 依赖容器
    ├── message_handler.py              # 迁移期旧文本主流程和工具 fallback
    ├── command_router.py               # 记忆、显化、时间等命令路由
    ├── prompt_builder.py               # 旧路径 LLM messages / prompt 拼装
    ├── personality.py                  # 人格状态和 prompt 构建
    ├── knowledge.py                    # 哲学知识库检索
    ├── flows.py                        # 交互式流程工具 session 状态机
    ├── llm_client.py                   # DeepSeek API 封装
    ├── memory.py                       # SQLite 记忆系统
    ├── proactive.py                    # 旧主动聊天和主题选择器
    ├── reminders.py                    # 提醒解析、创建和扫描发送
    ├── feishu_calendar.py              # 飞书日程解析和创建
    ├── content_fetcher.py              # B 站内容拉取和兴趣匹配
    ├── diary.py                        # 每日日记生成
    ├── relationship.py                 # 用户关系画像
    └── web_search.py                   # 联网搜索后端
```

## 快速开始

### 环境要求

- Python 3.10+
- NapCatQQ（或其他 OneBot V11 实现）
- DeepSeek API Key

### 安装

```bash
git clone https://github.com/shushu0sama/money-game-chat-QQ-bot.git
cd money-game-chat-QQ-bot

python -m venv venv
venv\Scripts\activate

pip install -e ".[dev]"
```

如果不需要开发依赖，也可以使用：

```bash
pip install -e .
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入 DeepSeek API Key 和需要启用的功能配置。

### 启动

```bash
# 方式一：一键启动
双击 启动艾琳娜.bat

# 方式二：终端启动
venv\Scripts\python bot.py
```

### 连接 QQ

在 NapCatQQ 中配置反向 WebSocket：

```text
ws://127.0.0.1:18080/onebot/v11/ws
```

## 自定义

个性化内容主要在 YAML 文件中：

```text
nonebot_plugin_personal_companion/prompts/default.yaml                 # 人格模板
nonebot_plugin_personal_companion/prompts/philosophy_knowledge.yaml    # 哲学知识库
nonebot_plugin_personal_companion/prompts/flow_steps.yaml              # 流程步骤模板
```

## 测试

运行全部测试：

```bash
python -m pytest
```

运行 UX 回归测试：

```bash
python -m pytest tests/test_ux_eval.py -q
```

测试覆盖记忆系统、流程引擎、LangGraph 消息图、主动行为图、工具注册/执行、提醒工具迁移、OneBot adapter 和 UX 场景。测试数量会随迁移进度变化，文档不固定写死。

## 技术栈

| 层 | 技术 |
|---|---|
| 框架 | NoneBot2 + OneBot V11 适配器 |
| 智能体编排 | LangGraph（消息图、主动行为图、工具路由/执行节点） |
| 大模型 | DeepSeek V4-Pro |
| 分词 | jieba |
| 存储 | SQLite（WAL 模式，多用户隔离、长期记忆和时间线记忆） |
| 调度 | nonebot-plugin-apscheduler / APScheduler |
| HTTP | httpx |
| 配置 | Pydantic v2 + python-dotenv |
| 日志 | nonebot.log.logger |
| 测试 | pytest |
| 类型检查 | mypy |
| Lint | ruff |

## 相关文档

- `介绍.md`：更短的中文项目介绍。
- `tasks/prd-qq-chat-bot-langgraph-rearchitecture.md`：LangGraph 新架构 PRD（英文标题/中英混排）。
- `tasks/prd-qq-chat-bot-langgraph-rearchitecture-zh.md`：LangGraph 新架构 PRD（中文）。
- `tasks/langgraph-old-path-inventory.md`：旧线性路径迁移盘点。

## License

MIT
