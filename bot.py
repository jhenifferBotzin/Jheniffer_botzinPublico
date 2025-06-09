import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Variáveis de ambiente e constantes
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5979445322
VIP_LINK = "https://t.me/+hOo4AdIjlk84OGMx"
PREVIAS_LINK = "https://t.me/+MyWIyKLMCFswOTE5"
PIX_KEY = "325296af-f058-436a-b433-835e49ea7305"

# Banco de dados simples na memória
pendentes = {}

# Logging
logging.basicConfig(level=logging.INFO)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Plano Vitalício – R$25", callback_data="plano_vitalicio")],
        [InlineKeyboardButton("📆 Plano Mensal – R$10", callback_data="plano_mensal")],
        [InlineKeyboardButton("👀 Ver grupo de prévias grátis", url=PREVIAS_LINK)],
    ]
    texto = (
        "👋 Bem-vindo!\n\n"
        "Você está prestes a entrar no *melhor canal VIP do Telegram* com:\n"
        "🔞 Incesto, coroas, novinhas e muito mais.\n"
        "✅ Conteúdo real, sem enrolação, sem mimimi!\n\n"
        "*Planos disponíveis:*\n"
        "💎 Vitalício: R$25\n"
        "📆 Mensal: R$10\n\n"
        "Veja as prévias grátis no botão abaixo!"
    )
    await update.message.reply_text(texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

# Callback dos planos
async def plano_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plano = "Vitalício" if "vitalicio" in query.data else "Mensal"
    valor = "25" if "vitalicio" in query.data else "10"
    user_id = query.from_user.id
    pendentes[user_id] = {"nome": query.from_user.full_name, "plano": plano}
    await query.answer()
    await query.message.reply_text(
        f"✅ Escolhido: Plano {plano}\n\n"
        f"💰 Valor: R$ {valor}\n"
        f"🔑 Chave Pix: {PIX_KEY}\n\n"
        "📸 *Envie o comprovante aqui mesmo pra prosseguir.*",
        parse_mode=ParseMode.MARKDOWN
    )
    # Notifica admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"👤 *{query.from_user.full_name}* quer o plano *{plano}*\n\nID: {user_id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Aprovar", callback_data=f"aprovar_{user_id}")],
            [InlineKeyboardButton("❌ Negado", callback_data=f"negar_{user_id}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# Aprovação ou negação
async def aprovar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return await query.message.reply_text("❌ Apenas o admin pode usar esse botão.")

    uid = int(query.data.split("_")[1])
    if uid in pendentes:
        del pendentes[uid]

    if "aprovar" in query.data:
        await context.bot.send_message(uid, f"✅ *Aprovado!* Seja bem-vindo ao VIP:\n{VIP_LINK}", parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text(f"✅ Aprovado e link enviado para {uid}.")
    elif "negar" in query.data:
        await context.bot.send_message(
            uid,
            "❌ *Seu acesso foi negado.*\n\n"
            "Verificamos que ainda não recebemos o pagamento.\n"
            "Por favor, envie o *comprovante do Pix* aqui para ser liberado.",
            parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text(f"❌ Negado o acesso de {uid}.")

# Listar pendentes
async def pendentes_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return await update.message.reply_text("❌ Você não tem permissão para isso.")

    if not pendentes:
        return await update.message.reply_text("✅ Não há usuários pendentes no momento.")

    msg = "📋 *Usuários pendentes de aprovação:*\n\n"
    for uid, data in pendentes.items():
        nome = data.get("nome", "Desconhecido")
        plano = data.get("plano", "Não definido")
        msg += f"👤 {nome} (ID: {uid}) - Plano: {plano}\n"

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(plano_callback, pattern="^plano_"))
    app.add_handler(CallbackQueryHandler(aprovar_callback, pattern="^(aprovar|negar)_"))
    app.add_handler(CommandHandler("pendentes", pendentes_list))
    print("✅ BOT ONLINE (polling)")
    app.run_polling()

if __name__ == "__main__":
    main()
