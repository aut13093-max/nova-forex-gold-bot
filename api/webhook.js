
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(200).send("Nova Forex Gold AI Bot is running");
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;

  if (!token) {
    return res.status(500).send("Bot token is not configured");
  }

  const message = req.body?.message;
  const chatId = message?.chat?.id;
  const text = (message?.text || "").trim();

  if (!chatId || !text) {
    return res.status(200).send("OK");
  }

  let reply;

  if (text === "/start") {
    reply =
      "欢迎使用 Nova Forex Gold AI！\n\n" +
      "可用命令：\n" +
      "/analyze - 外汇与黄金分析说明\n" +
      "/risk - 计算交易仓位和风险\n" +
      "/help - 使用说明\n\n" +
      "目前提供交易辅助，不保证盈利。";
  } else if (text === "/help") {
    reply =
      "使用说明：\n" +
      "/analyze EURUSD — 查看分析说明\n" +
      "/analyze XAUUSD — 查看黄金分析说明\n" +
      "/risk — 查看风险计算方法\n\n" +
      "本版本尚未连接实时行情数据。";
  } else if (text.startsWith("/analyze")) {
    reply =
      "行情分析模块已启动。\n" +
      "支持：EUR/USD、USD/JPY、XAU/USD。\n\n" +
      "注意：当前版本尚未接入实时行情，不能据此生成实时买卖信号。";
  } else if (text.startsWith("/risk")) {
    reply =
      "风险计算方法：\n" +
      "单笔风险金额 = 账户余额 × 风险比例。\n\n" +
      "例如：账户 $1,000，风险 1%，单笔最大计划风险为 $10。\n" +
      "实际仓位还需要入场价、止损价和合约规格。";
  } else {
    reply = "暂时不支持此命令。输入 /help 查看使用说明。";
  }

  const response = await fetch(
    `https://api.telegram.org/bot${token}/sendMessage`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: reply
      })
    }
  );

  if (!response.ok) {
    console.error("Telegram sendMessage failed:", await response.text());
  }

  return res.status(200).send("OK");
}
