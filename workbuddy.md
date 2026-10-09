# workbuddy.md —— WorkBuddy 真实开发过程记录（已脱敏）

> 本文件用于参赛核验“真实使用腾讯 WorkBuddy 开发”。内容从 2026-10-09 的真实开发会话整理，已删除 Token、手机号、地址、订单号、门店名、券码及一切个人数据；不含任何虚构的工具调用或验证结论。

## 1. 用户给 WorkBuddy 的核心任务

用户在工作区提供了一份自拟的《WorkBuddy 项目任务书》（产品方向、范围、交付结构、合规红线均由用户事先拟定），要求 WorkBuddy：

1. 阅读任务书、比赛官方仓库的 README / activityGuidelines / CONTEST_DECLARATION，以及麦当劳 MCP Server 与 WorkBuddy 技能/连接器官方文档；
2. 在本地工作区完成“麦麦回忆局（McD Replay）”Skill 项目的全部文件与可导入 ZIP；
3. 优先使用已启用的 `mcd-mcp` 连接器完成真实**只读**调用验证；
4. 不输出/保存 Token 与个人订单数据；不创建 GitHub 远程仓库、不推送、不报名、不执行任何写操作 MCP 调用；
5. 完成后报告交付路径、实际验证情况与需要用户亲自完成的步骤。

## 2. WorkBuddy 完成的主要工作

1. **规则核对**：通读任务书与本地比赛材料（README.md、activityGuidelines.md、CONTEST_DECLARATION.md、RANKING.md），并通过 WebFetch 核对官方在线文档（麦当劳 mcd-mcp-server 工具清单、WorkBuddy 技能包结构）。
2. **真实 MCP 只读验证**：通过已配置的 `mcd-mcp` 连接器，实际调用并成功返回 4 个只读工具：`now-time-info`、`order-list`、`query-my-coupons`、`campaign-calendar`。返回内容仅用于核对字段结构，未落盘、未写入任何文件。`query-meals`、`query-store-coupons`、`calculate-price` 因需要用户提供门店/取餐方式，本次未实测，已在 MCP_INTEGRATION.md 中如实标注“未验证”。
3. **项目实现**：创建 `mcd-replay/` 项目目录；逐字复制官方 `CONTEST_DECLARATION.md`（diff 校验一致）；编写 `SKILL.md`、`references/mcp-tool-map.md`、`scripts/build_recap.py`、`templates/recap-card.html`、`examples/synthetic-recap.json`、`.gitignore`、`mcp-config.example.json`、`README.md`、`MCP_INTEGRATION.md`。
4. **测试**：用合成示例数据运行脚本，验证统计结果正确（完成单数、合计、均值与手工核算一致）；构造含 `<script>`/`<img onerror>` 的注入输入，确认生成 HTML 全部转义、无可执行注入；检查生成卡片无未填充占位符、含“示例数据”水印。
5. **打包**：生成 `dist/mcd-replay-skill.zip`（ZIP 内技能根目录直接包含 `SKILL.md`），并对全项目做敏感信息扫描（无 Token、手机号、订单号、门店名等）。

## 3. 对话中对方案/实现的关键选择

- **差异化定位**：按用户任务书确定的方向——订单历史复盘 + 隐私友好分享卡，而非重复度高的套餐推荐。
- **统计可信**：金额/订单数/时段/餐品等可计算字段交给 Python 脚本确定性计算，AI 只写画像文案与解释，不改写数字。
- **隐私边界**：标识字段（订单号、门店编码/名称等）在进入统计前即丢弃；分享卡只含汇总；真实数据与合成示例严格分离；卡片注明“个人数据回顾；数据来自用户授权的麦当劳 MCP 查询；仅供个人参考”。
- **诚实标注**：接口只返回有限近期记录时，明确标注“仅统计本次接口返回记录”；未实测的工具一律标“未验证”。

## 4. 实际 MCP 验证情况

- 已实测（真实 WorkBuddy 连接器调用成功）：`now-time-info`、`order-list`、`query-my-coupons`、`campaign-calendar`。
- 未实测：`query-meals`、`query-store-coupons`、`calculate-price`（需用户提供门店与取餐方式后再验证）。
- 未执行任何写操作工具调用。

## 5. 人工修改或检查内容

- 任务书本身由用户撰写，确定了产品方向、合规红线与交付清单。
- 用户需亲自完成的步骤（WorkBuddy 未代办）：申请/保管 MCP Token、在 WorkBuddy 连接器界面粘贴 Token、上传导入 Skill ZIP、创建 GitHub Public 仓库并推送、提交报名 Issue、合规争取真实 Star。
- 建议用户提交前复查：仓库中无 Token、真实订单、手机号、地址、订单号或私人截图；`CONTEST_DECLARATION.md` 与官方源文件一致。
