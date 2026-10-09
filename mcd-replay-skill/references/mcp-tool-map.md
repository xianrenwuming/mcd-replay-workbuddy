# 麦当劳 MCP 工具映射（麦麦回忆局专用）

> 官方 MCP Server：`https://mcp.mcd.cn`（Streamable HTTP，`Authorization: Bearer <Token>`）。
> 完整工具清单以官方仓库 https://github.com/M-China/mcd-mcp-server 与连接器运行时实际展示为准。
> 本项目只使用下表中的**只读**工具；任何写操作工具一律禁用。

## 本项目使用的只读工具

| 工具 | 用途 | 何时调用 | 关键参数（以运行时 Schema 为准） | 返回中本项目用到的字段 |
|---|---|---|---|---|
| `order-list` | 查询近期到店/外送历史订单（非商城订单） | 场景 A 核心数据源 | 无参数（实测 2026-10-09） | `data.list[]`：`createTime`、`orderStatus`、`realTotalAmount`、`orderProductList[].productName/quantity/comboItemList[].name`。**`orderId`、`storeCode`、`storeName`、`beCode`、`beType` 属标识字段，统计前必须丢弃** |
| `now-time-info` | 获取服务器当前时间 | 生成卡片 `generated_at`、判断券有效期 | 无参数 | `data.formatted`、`data.date` |
| `query-my-coupons` | 查询用户当前拥有的优惠券 | 场景 B 第 1 步 | `page`（默认 1，最多 5 页）、`pageSize`（默认/最大 200） | 券名、用券价格、有效期、使用标签（到店/外送等）。券码类信息不进入任何输出 |
| `campaign-calendar` | 查询当月营销活动日历 | 场景 B，且用户明确要求时 | `specifiedDate`（可选，yyyy-MM-dd；不填返回当月） | 活动日期、标题、内容简介 |
| `query-meals` | 查询指定门店当前可售餐品 | 场景 B，用户确认门店+取餐方式后 | 门店标识、取餐方式（以运行时为准） | 餐品分类、餐品编码、名称 |
| `query-store-coupons` | 查询指定门店当前可用券 | 场景 B，用户确认门店+取餐方式后 | 门店标识（以运行时为准） | 门店可用券列表及条件 |
| `calculate-price` | 计算选购清单实付金额（含券） | 场景 B 第 3 步，价格唯一依据 | 商品列表、可选券（以运行时为准） | 商品金额、配送费、优惠金额、应付总价 |

## 实测情况（2026-10-09，通过 WorkBuddy mcd-mcp 连接器）

- `now-time-info`、`order-list`、`query-my-coupons`、`campaign-calendar`：已真实调用成功。
- `query-meals`、`query-store-coupons`、`calculate-price`：未在本次开发中实测（需要用户提供门店/取餐方式），按“未验证”处理，首次使用前必须读取运行时 Schema。

## 明确禁用的写操作工具

`create-order`、`cancel-order`、`auto-bind-coupons`、`draw-lottery`、`mall-create-order`、`party-order-create`、`delivery-create-address`，以及官方后续新增的任何会改变账户状态的工具。

## 隐私处理约定

- 统计输入只保留：`createTime` → `create_time`，`orderStatus` → `status`，`realTotalAmount` → `amount`，`productName`/`comboItemList[].name` + `quantity` → `items`，渠道（能判定才填）→ `channel`。
- 订单类型字段（如 `orderType`、`beType`）与渠道语义的对应关系官方未给出公开枚举，不能判定时不要猜测，直接省略 `channel`。
- 生成卡片用的临时输入 JSON 用完即删；卡片本身只含汇总统计。
