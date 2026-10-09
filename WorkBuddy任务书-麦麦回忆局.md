# WorkBuddy 项目任务书：麦麦回忆局

> 版本：1.0  
> 规则核对日期：2026-10-09（北京时间）  
> 目标：把本文交给 WorkBuddy，在当前工作区完成一个可安装、可演示、可公开参赛的 WorkBuddy Skill 项目。

## 一、项目内容

**项目名：麦麦回忆局**  
**英文名：McD Replay**  
**一句话：把你真实点过的麦当劳订单，整理成一份有数据依据、保护隐私、可以分享的个人回顾；需要时再结合当前可用优惠给出下次点单参考。**

主打功能不是泛泛地“推荐套餐”，而是从用户自己的订单记录出发，回答“我最近都点了什么、花了多少、什么时候最常点、下次有什么现成优惠可用”。它通过 WorkBuddy 调用麦当劳 MCP 的只读查询工具，生成可在本地查看的个人回顾卡。项目不自动下单、不自动领券、不抽奖、不另行收集或上传订单历史；真实查询仍会经过用户授权的麦当劳 MCP 和 WorkBuddy 对话链路。

我选择这个方向，是因为截至 2026-10-09，比赛报名 Issue 中已经出现大量营养配餐、省钱、套餐优化和通用点餐助手；订单历史复盘和隐私友好分享卡更容易形成清晰的区别。GitHub 报名 Issue 可见 [当前参赛项目列表](https://github.com/M-China/mcd-developer-innovation-challenge/issues)。

## 二、WorkBuddy 执行要求

请把本任务书作为产品和交付依据，在工作区 `F:\xm\MDL` 下创建独立项目目录：

```text
F:\xm\MDL\mcd-replay\
```

在开始写入文件前，先阅读本任务书、比赛仓库的 `README.md`、`activityGuidelines.md`、`CONTEST_DECLARATION.md`，以及麦当劳官方 MCP Server 使用说明。比赛材料位于：

```text
F:\xm\MDL\mcd-developer-innovation-challenge-main\
```

保持该比赛材料目录原样。不要创建 GitHub 远程仓库、推送代码、提交报名 Issue、发布社交媒体内容，也不要执行任何会改变麦当劳账户状态的 MCP 操作。所有本地文件和演示材料完成后，向我交付路径、安装包位置和我必须亲自完成的发布步骤。

如果麦当劳 MCP 连接器尚未在 WorkBuddy 中启用，继续完成不依赖在线连接的项目文件；在说明中明确标出尚未完成的真实 MCP 验证，不要编造调用记录或成功结果。连接器可用时，只执行本项目需要的只读查询。

## 三、比赛事实和不可违反的要求

以官方仓库中的完整活动规则为准。官方链接：

- [比赛主页及参与指南](https://github.com/M-China/mcd-developer-innovation-challenge)
- [完整活动规则](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md)
- [官方 MCP Server 接入和工具清单](https://github.com/M-China/mcd-mcp-server)
- [WorkBuddy 技能开发说明](https://open.workbuddy.cn/docs/skill)
- [WorkBuddy 连接器说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector)

比赛规则摘要：

1. 报名期为北京时间 **2026-10-09 10:30 至 2026-10-25 23:59**；排行榜在北京时间 **2026-10-26 00:00** 定榜。现在立即制作和报名。
2. 参赛项目仓库须是 GitHub **Public**，创建时间须在北京时间 **2025-12-25 00:00 至 2026-10-25 23:59**。
3. 排名以项目公开 Star 数为准；Star 数为 0 的项目不进入排行榜。原则上前 100 个项目进入榜单，同 Star 按规则并列；同一 GitHub 账号提交多个项目时，仅最高 Star 项目入榜。
4. 必须真实使用麦当劳 MCP。参与 WorkBuddy 专项奖励时，还必须真实使用腾讯 WorkBuddy。
5. 完整规则列出的交付文件包括 `README.md`、`CONTEST_DECLARATION.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`；使用 WorkBuddy 参加专项奖励时，再提交 `workbuddy.md`。其中官方 README 明确规定 `CONTEST_DECLARATION.md` 的文件名和内容都不可修改，必须从官方比赛仓库原样复制。
6. 项目及 GitHub 账号须符合规则的资格、原创、内容合规和信息安全要求。规则要求参与者为中国大陆地区合法居民；年满 18 周岁，或未满 18 周岁但已取得法定监护人同意。
7. 规则明确禁止刷榜、机器人/脚本操纵 Star、批量或控制多个账号等不正当行为。只做真实用户传播，不承诺名次。
8. WorkBuddy 专项奖励：符合入榜条件且真实使用 WorkBuddy、提交真实 `workbuddy.md` 的前 100 名作品可获得 3000 WorkBuddy 积分；前三名另有 10240 WorkBuddy 积分奖励（依活动规则执行）。排行榜奖励和前三名的兑换资格也以官方规则为准。

README 的文件清单比完整规则简略；本项目同时遵守完整规则中更完整的清单，务必包含 `mcp-config.example.json`。

## 四、产品范围

### 核心场景 A：我的麦麦月报 / 回顾

用户在 WorkBuddy 中说“帮我做一份麦麦月报”或“回顾一下我最近的麦当劳订单”。Skill 先确认时间范围；如果 MCP 工具只返回有限的近期记录，就明确展示服务实际返回的记录区间，不把它说成完整月报或全年账单。然后通过麦当劳 MCP 的订单历史查询工具读取可用记录，按返回字段生成一份摘要。

只在 MCP 返回字段确实支持时计算并展示以下内容：

- 成功/已完成订单数、查询覆盖时间范围；
- 有效记录中的消费金额、平均单笔金额；
- 常见餐品或套餐、常见点餐时段、到店/外送等渠道占比；
- 退款、取消、失败或无法判定状态的记录单独说明，不能静默算作成功消费；
- 用户的一句轻松、有尊重感的“麦麦消费画像”，每个判断都能由数据解释。

若 MCP 返回的数据没有某项字段，就不推断、不编造该统计。若用户历史为空、连接失败或认证失败，说明原因并给下一步；不要拿合成数据冒充用户真实结果。

### 核心场景 B：我的下一餐优惠

用户明确询问“下次怎么用券”“按我的预算推荐一餐”时再进入此流程：

1. 查询用户当前可用优惠券；用户明确要求时，可查询当月活动日历。
2. 只有在用户提供或确认门店和取餐方式后，才查询该门店的实时在售菜单及门店可用券。
3. 对候选组合使用官方价格计算工具，以工具返回的实付金额作为价格依据；说明券的适用条件和查询时点。
4. 提供最多三项清楚的备选，并说明依据；若缺少门店/订单类型等必需信息，先询问最少必要信息，不索要精确家庭地址。
5. 该功能只给选择建议，绝不自动创建订单、付款、领券或执行积分抽奖。

### 分享卡与隐私

- 从真实记录生成简洁、精致的本地 HTML/SVG 回顾卡，中文优先，适配手机竖屏，便于用户自己截图分享。
- 分享卡只允许出现经过汇总的统计，不得出现姓名、手机号、地址、订单号、会员号、Token、券码、精确门店地址或单笔订单明细。
- 视觉使用原创图形和普通字体，不复制麦当劳官方 Logo、图片或受限制素材，不暗示本项目是麦当劳官方产品。
- 卡片标注“个人数据回顾；数据来自用户授权的麦当劳 MCP 查询；仅供个人参考”。若数据区间不完整，要显著注明“仅统计本次接口返回记录”。
- 真实订单查询会经过用户已配置的麦当劳 MCP 服务和 WorkBuddy 对话链路，相关数据处理及对话留存遵守这两个服务各自的条款。项目自身不增加数据上传服务、不记录 MCP 原始响应。除非用户明确要求，不把真实记录写入项目文件、样例、截图、报告或 Git。
- 演示用数据必须是明显标注的合成数据；样例不可仿造真实账户、真实订单号或真实 Token。

## 五、MCP 工具使用约定

官方 MCP Server 地址为 `https://mcp.mcd.cn`，使用 Streamable HTTP。连接器需由用户在 WorkBuddy 里配置真实 Token。候选只读工具（以连接器运行时实际展示的工具名称和参数 Schema 为准）：

- `order-list`：查询近期到店/外送历史订单，是核心数据源；
- `query-my-coupons`：查询用户当前可用优惠券；
- `campaign-calendar`：用户要求时查询活动日历；
- `query-meals`、`query-store-coupons`、`calculate-price`：用户提供门店/取餐方式并请求下次点餐建议时使用。

请在实际调用前读取 WorkBuddy 连接器暴露的工具描述和输入参数。不要假设参数名、分页范围或返回字段。`MCP_INTEGRATION.md` 中写清本项目确实调用过哪些工具、每个工具的输入来源、调用顺序、返回字段如何进入报告、对用户的业务价值；尚未实测的工具标成“未验证”，不可写成已完成。

不得在项目脚本中直接硬编码 Token 或绕过 WorkBuddy/MCP Connector 自行请求 MCP。不要调用 `create-order`、`cancel-order`、`auto-bind-coupons`、`draw-lottery`、`mall-create-order`、`party-order-create` 等写操作。对订单历史的查询只限用户已授权的账户数据。

## 六、实现和交付结构

请用适合 WorkBuddy Skill 导入、依赖少且容易维护的方式实现。按 WorkBuddy 官方技能格式使用 YAML frontmatter + Markdown 正文；官方技能包结构要求一个技能目录中有 `SKILL.md`，可用 `references/`、`scripts/`、`templates/` 等子目录。至少产出：

```text
mcd-replay/
├── README.md
├── CONTEST_DECLARATION.md       # 从官方比赛仓库逐字复制，不改名、不修改任何内容
├── MCP_INTEGRATION.md
├── mcp-config.example.json      # 仅使用环境变量占位符
├── workbuddy.md                 # 由本次真实 WorkBuddy 开发过程整理并脱敏
├── .gitignore
├── mcd-replay-skill/
│   ├── SKILL.md
│   ├── references/
│   │   └── mcp-tool-map.md
│   ├── scripts/
│   │   └── build_recap.py       # 只处理传入的汇总数据并生成本地卡片，不联网、不读密钥
│   ├── templates/
│   │   └── recap-card.html
│   └── examples/
│       └── synthetic-recap.json # 合成数据，并在文件和页面醒目标识“示例数据”
└── dist/
    └── mcd-replay-skill.zip     # 可导入的 Skill 包；内含一个技能目录
```

按 WorkBuddy 当前官方文档补齐可导入 ZIP 的精确目录结构和元数据。如果打包器要求 ZIP 内技能根目录直接包含 `SKILL.md`，就按实际导入要求调整 ZIP；仓库中的源目录仍清晰保留。

技术约束：

- MCP 查询由 WorkBuddy 通过其配置好的麦当劳连接器完成；Python 脚本仅接收去标识化汇总对象，负责稳定地计算展示字段/生成 HTML，不直接接触 Token 或 MCP 网络接口。
- 对“金额、时间范围、订单数、餐品统计”等可计算字段，尽量使用脚本确定性计算；模型负责解释，不自行改写统计结果。
- 生成文件时采用安全的 HTML 转义；不把 MCP 返回文本作为 HTML/脚本执行。
- `.gitignore` 至少覆盖 `.env`、本地 Token 文件、真实订单数据、未脱敏导出文件、个人报告和临时文件。合成示例允许提交。
- `mcp-config.example.json` 的 Token 值只能是环境变量占位符，例如 `Bearer ${MCD_MCP_TOKEN}`。在 README 中说明该文件是文档样例；真实 Token 只在 WorkBuddy 连接器配置界面输入，不能写进仓库或聊天记录。
- 从比赛源目录原样复制 `CONTEST_DECLARATION.md`：`F:\xm\MDL\mcd-developer-innovation-challenge-main\CONTEST_DECLARATION.md`。
- 不复制麦当劳 MCP 仓库中非必要的大段文档/图片，不复用官方 Logo。注明 MCP/品牌归属及非官方项目声明。

## 七、README 必须写到可照着做

`README.md` 使用中文为主，至少包括：

1. 作品一句话介绍、问题场景、目标用户、功能截图/合成示例卡；
2. Skill 的目录说明、安装方式和更新方式；
3. 申请 MCP Token 的官方入口、在 WorkBuddy 新建连接器的完整步骤、启用连接器、导入 Skill ZIP 的完整步骤；
4. 至少 3 个可直接复制的使用示例，包括月报、隐私回顾卡、优惠查询；
5. 实际调用哪些 MCP 工具、需要用户授权什么、哪些功能只读；
6. 隐私、安全、合成示例说明和常见故障（401 Token 无效/过期，429 限流，订单范围不完整，门店信息不足）；
7. 免责声明：个人参赛作品，非麦当劳官方产品；价格、餐品、活动、优惠以用户当前 MCP 查询和官方渠道为准；不构成理财、医疗或营养建议；
8. 项目亮点、工作流图或 Mermaid 简图、开发方式以及 WorkBuddy 的真实使用说明；
9. 比赛报名简介草稿（控制在 1000 字内，不放图片，报名时可直接复制）。

让 README 首屏 10 秒内能看懂“输入什么—调用什么—产出什么”。示例截图和分享卡必须标注为合成数据演示，不要伪装成真实用户结果。

## 八、workbuddy.md 的真实性

本次项目计划参与 WorkBuddy 专项奖励，所以需要 `workbuddy.md`。请在完成实际 WorkBuddy 开发后，从真实工作过程整理：用户给 WorkBuddy 的核心任务、WorkBuddy 完成的主要工作、对话中对方案/实现的关键选择、实际 MCP 验证情况、人工修改或检查内容。保留足以核验的上下文，但删除 Token、邮箱、手机号、地址、订单号、会员号、券码和其他个人数据。不得伪造对话、假装 MCP 工具调用成功、虚构人工贡献或验证数据。若 WorkBuddy 可导出真实聊天记录，优先从真实记录整理并在提交前脱敏。

## 九、完成条件

完成后给我一份简短的交付清单，明确列出：

- 项目绝对路径；
- Skill 源目录和可导入 ZIP 路径；
- 必需参赛文件是否齐全；
- MCP 哪些工具已通过真实 WorkBuddy 连接调用，哪些没有；
- README 中演示数据是否为合成数据；
- 我需要手动完成的 GitHub 建仓、推送、报名和自然传播步骤。

不要声称已部署/已报名/已获 Star；不要替我创建公开 GitHub 仓库或发表 Issue。

---

## 官方来源

- [比赛 README](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/README.md)
- [完整比赛规则 activityGuidelines.md](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md)
- [官方不可修改参赛声明](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/CONTEST_DECLARATION.md)
- [麦当劳 MCP Server 接入指南和工具列表](https://github.com/M-China/mcd-mcp-server)
- [WorkBuddy 开放平台：技能包结构](https://open.workbuddy.cn/docs/skill)
- [WorkBuddy 官方：MCP 连接器](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector)
- [官方参赛 Issue 列表](https://github.com/M-China/mcd-developer-innovation-challenge/issues)
