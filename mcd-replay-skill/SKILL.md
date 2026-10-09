---
name: mcd-replay
display_name: 麦麦回忆局
display_name_en: McD Replay
description: 把你授权查询到的麦当劳历史订单整理成有数据依据、保护隐私的个人回顾卡；需要时结合当前可用优惠给出下次点单参考。只读查询，绝不下单、不领券、不抽奖。
description_zh: 麦当劳个人订单回顾与隐私友好分享卡：月报摘要、消费画像、本地 HTML 回顾卡，以及按需的优惠券/下次点单参考（仅建议，不执行任何写操作）。
description_en: McD Replay turns your authorized McDonald's China order history (via the official MCP, read-only) into a privacy-friendly local recap card, with on-demand coupon-aware next-meal suggestions. Never places orders, claims coupons, or draws lotteries.
version: 1.0.0
author: 麦麦回忆局项目作者（个人参赛作品，非麦当劳官方产品）
---

# 麦麦回忆局（McD Replay）

把用户真实点过的麦当劳订单，整理成一份有数据依据、保护隐私、可以分享的个人回顾；用户明确需要时，再结合当前可用优惠给出下次点单参考。

**铁律（任何时候都适用）：**

1. 只使用只读 MCP 工具。禁止调用 `create-order`、`cancel-order`、`auto-bind-coupons`、`draw-lottery`、`mall-create-order`、`party-order-create`、`delivery-create-address` 等任何会改变账户状态的工具。
2. 真实订单数据不写入项目文件、样例、截图、Git 或分享内容；除生成卡片所需的去标识化临时输入外，不落盘保存 MCP 原始响应。
3. 分享卡只出现汇总统计，绝不出现姓名、手机号、地址、订单号、会员号、Token、券码、精确门店地址或单笔订单明细。
4. 接口返回什么就统计什么：没有某字段就不推断、不编造；退款/取消/失败订单单独说明，不静默算作成功消费。
5. 历史为空、连接失败或认证失败时，说明原因并给下一步建议；绝不用合成数据冒充真实结果。
6. 不声称自己是麦当劳官方产品。

工具调用前必读 @references/mcp-tool-map.md，确认工具名称、参数与返回字段以连接器运行时实际展示为准。

## 场景 A：我的麦麦月报 / 回顾

触发词示例：“帮我做一份麦麦月报”“回顾一下我最近的麦当劳订单”“生成我的麦麦回忆卡”。

步骤：

1. **确认时间范围预期。** 询问用户想要的回顾范围（如“最近一个月”）。同时说明：`order-list` 返回的是接口实际提供的近期记录，统计范围以返回数据为准，不把它包装成完整月报或全年账单。
2. **调用 `order-list`**（只读）获取历史订单。失败时按“故障处理”一节说明。
3. **构造去标识化输入 JSON。** 在工作区临时目录（如 `tmp/recap-input.json`）写入仅含以下字段的汇总对象，**丢弃** orderId、storeCode、storeName、beCode、beType 等一切标识字段：

   ```json
   {
     "meta": {
       "title": "我的麦麦回顾",
       "generated_at": "当前时间（可调用 now-time-info 获取）",
       "is_sample": false,
       "scope_note": "仅统计本次接口返回记录",
       "persona": "由你根据统计结果写的一句轻松、有尊重感的画像"
     },
     "orders": [
       {
         "create_time": "YYYY-MM-DD HH:MM:SS",
         "status": "订单状态原文",
         "channel": "到店/外送（能判定才填，不能判定则省略）",
         "amount": 0.0,
         "items": [{"name": "餐品名", "quantity": 1}]
       }
     ]
   }
   ```

   - `items` 需把套餐子项（comboItemList）也摊平计入，子项字段名可能是 `name`。
   - `amount` 取订单实付金额字段（如 `realTotalAmount`），无法解析的留空。
   - 若接口返回区间明显不完整，`scope_note` 必须写“仅统计本次接口返回记录”。
4. **运行脚本生成卡片：**

   ```bash
   python <技能目录>/scripts/build_recap.py tmp/recap-input.json tmp/recap-card.html
   ```

   金额、订单数、时段、餐品统计全部以脚本输出为准，不要自行改写统计数字；你只负责写 `persona` 画像文案和向用户解释。
5. **用 present_files 把生成的 HTML 卡片交付给用户**，并口头概述：已完成订单数、统计区间、消费合计与平均单笔、常点餐品/时段、以及单独说明的非成功订单。除非用户主动要求，不要在聊天里复述单笔明细。
6. **清理临时输入文件**（含真实订单字段的 tmp JSON），生成给用户留存的卡片除外。

## 场景 B：我的下一餐优惠（仅在用户明确提出时）

触发词示例：“下次怎么用券”“按我的预算推荐一餐”“这附近有什么优惠”。

步骤：

1. 调用 `query-my-coupons` 查当前可用券；用户明确要求时调用 `campaign-calendar` 查当月活动。
2. **只在用户提供或确认门店和取餐方式后**，才调用 `query-meals`、`query-store-coupons` 查询该门店在售菜单与可用券。缺少门店/取餐方式时先询问最少必要信息，不索要精确家庭地址。
3. 对候选组合调用 `calculate-price`，以工具返回的实付金额作为唯一价格依据，并说明券的适用条件与查询时点。
4. 给出最多 3 项备选及依据。只给建议，绝不代下单、付款、领券或抽奖。

## 故障处理

- **401**：Token 无效或过期。提示用户到 https://open.mcd.cn/mcp 控制台重新获取 Token，并在 WorkBuddy 连接器配置中更新；不要索要或复述 Token。
- **429**：触发限流（每 Token 每分钟 600 次）。降低调用频率后重试。
- **返回记录为空或区间过短**：如实告知“本次接口未返回满足条件的记录”，并说明可能原因（近期无订单/接口仅返回近期记录）。
- **字段缺失**：对应统计项直接标注“本次返回记录中无此字段”，不做推测。

## 合成演示数据

`examples/synthetic-recap.json` 是完全虚构的合成示例，可用于离线演示：`python scripts/build_recap.py examples/synthetic-recap.json examples/synthetic-recap-card.html`。演示截图必须保留“示例数据”水印，不得伪装成真实用户结果。
