# MCP_INTEGRATION —— 麦当劳 MCP 实际集成说明

- **MCP Server**：`https://mcp.mcd.cn`（Streamable HTTP），官方文档：https://github.com/M-China/mcd-mcp-server
- **接入方式**：用户在 WorkBuddy【连接器 → 自定义连接器 → 配置 MCP】中自行配置真实 Token（`Authorization: Bearer <Token>`）。本项目代码不含、也不需要任何 Token；所有 MCP 调用均由 WorkBuddy 经用户已配置的 `mcd-mcp` 连接器发起。
- **本项目只用只读工具**；禁用 `create-order`、`cancel-order`、`auto-bind-coupons`、`draw-lottery`、`mall-create-order`、`party-order-create`、`delivery-create-address` 等全部写操作。

## 一、已真实验证的工具（2026-10-09，经 WorkBuddy mcd-mcp 连接器实测）

| 工具 | 输入来源 | 返回结构（关键字段） | 返回字段如何进入报告 | 业务价值 |
|---|---|---|---|---|
| `order-list` | 无参数，直接调用 | `data.list[]`：`orderId`、`orderType`、`createTime`、`beType`、`beCode`、`storeCode`、`storeName`、`orderStatus`、`orderProductList[].productCode/productName/quantity/comboItemList[].name`、`realTotalAmount`（字符串金额） | 仅 `createTime`、`orderStatus`、`realTotalAmount`、`productName/comboItemList[].name+quantity` 进入去标识化统计输入；`orderId`、`storeCode`、`storeName`、`beCode`、`beType` 在进入统计前**丢弃**，不出现在任何文件或卡片中 | 核心数据源：回答“最近点了什么、花了多少、什么时候最常点” |
| `now-time-info` | 无参数 | `data.formatted`、`data.date`、`data.timestamp` 等 | 作为卡片“生成时间”与券有效期判断基准 | 保证“快到期券”“本月活动”等判断有统一时间基准 |
| `query-my-coupons` | `page=1`、`pageSize=200` | 券列表：券名、用券价格、有效期（含星期/时段限制）、使用标签（到店/外送专用等） | 场景 B 中按有效期排序提示“快到期券”；券码类信息不进入任何输出 | 让用户知道“手上已有什么券” |
| `campaign-calendar` | 无参数（默认当月） | 按日期分组的活动：标题、内容简介、进行状态（往期/今日/未来） | 场景 B 中用户明确要求时，补充“本月可参与活动” | 补充优惠之外的官方活动信息 |

**调用顺序（场景 A）**：`now-time-info` → `order-list` → 本地去标识化 → `scripts/build_recap.py` → 本地 HTML 卡片。
**调用顺序（场景 B）**：`query-my-coupons`（→ `campaign-calendar`，可选）→ 用户确认门店/取餐方式 → `query-meals` + `query-store-coupons` → `calculate-price`。

**实测说明**：上述 4 个工具均返回 `success: true`；真实返回内容仅用于核对字段结构，未写入任何项目文件、样例或截图。

## 二、尚未实测的工具（标为“未验证”）

| 工具 | 计划用途 | 未验证原因 |
|---|---|---|
| `query-meals` | 查指定门店当前可售餐品 | 需要用户提供的门店标识与取餐方式，本次开发未获取 |
| `query-store-coupons` | 查指定门店当前可用券 | 同上 |
| `calculate-price` | 候选组合实付金额计算（价格唯一依据） | 依赖前两个工具的门店/商品上下文，同上 |

首次使用这三个工具前，必须读取连接器运行时展示的最新参数 Schema，不假设参数名与返回字段。

## 三、隐私与安全约定

1. 统计输入为去标识化汇总对象（时间/状态/金额/餐品名+数量/可选渠道），由 `scripts/build_recap.py` 做确定性计算并渲染本地 HTML；脚本不联网、不读密钥。
2. 卡片只含汇总统计；退款/取消/失败订单单独列出，不计入消费统计；返回区间不完整时标注“仅统计本次接口返回记录”。
3. 项目不记录 MCP 原始响应；真实查询经用户授权的麦当劳 MCP 与 WorkBuddy 对话链路，数据处理遵守两服务各自条款。
4. `mcp-config.example.json` 仅含环境变量占位符 `Bearer ${MCD_MCP_TOKEN}`，真实 Token 只出现在 WorkBuddy 连接器配置界面。
