import asyncio
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import BOT_TOKEN, API_ID, API_HASH, MONGO_URI, ADMIN_IDS, CHANNEL_IDS

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client['telegram_bot']

TEXTS = {
    "en": {
        "welcome": "Welcome to the bot!",
        "update_channel": "📢 Update Channel",
        "join_community": "👥 Join Community",
        "invite_earn": "🎁 Invite & Earn",
        "my_status": "👤 My Status",
        "tasks": "🎮 Tasks",
        "language": "🌍 Language",
        "buy_premium": "💎 Buy Premium",
    },
    "bn": {
        "welcome": "বট এ স্বাগতম!",
        # Add other translations here
    }
}

async def start_command(client, message):
    user_id = message.from_user.id
    referral = message.text.split("?start=")[-1] if "?start=" in message.text else None
    await db.users.update_one({"user_id": user_id}, {"$setOnInsert": {"points": 0, "referrals": 0, "referred_by": referral}}, upsert=True)
    await message.reply(TEXTS["en"]["welcome"], reply_markup=await main_menu())

async def main_menu():
    return [
        [("📢 Update Channel", "https://t.me/your_channel")],
        [("👥 Join Community", "https://t.me/your_community")],
        [("🎁 Invite & Earn", "/invite")],
        [("👤 My Status", "/status")],
        [("🎮 Tasks", "/tasks")],
        [("🌍 Language", "/language")],
        [("💎 Buy Premium", "/buy")]
    ]

@app.on_message(filters.command("start"))
async def handle_start(client, message):
    await start_command(client, message)

# Referral and point system
@app.on_message(filters.command("invite"))
async def handle_invite(client, message):
    user_id = message.from_user.id
    user = await db.users.find_one({"user_id": user_id})
    if user:
        referral_link = f"https://t.me/your_bot?start={user_id}"
        await message.reply(f"Your referral link: {referral_link}")

# Mini task system
@app.on_message(filters.command("tasks"))
async def handle_tasks(client, message):
    tasks = await db.tasks.find().to_list(length=None)
    task_list = "\n".join([f"{task['task_id']}: {task['type']} - {task['reward']} points" for task in tasks])
    await message.reply(f"Available tasks:\n{task_list}")

# Daily bonus
@app.on_message(filters.command("daily"))
async def handle_daily(client, message):
    user_id = message.from_user.id
    user = await db.users.find_one({"user_id": user_id})
    if user:
        # Logic for daily bonus
        await message.reply("You have claimed your daily bonus!")

# Premium system
@app.on_message(filters.command("buy"))
async def handle_buy(client, message):
    await message.reply("Choose your payment option:\n1. bKash\n2. Nagad\n3. Crypto\n4. Manual")

# Video content system
@app.on_message(filters.command("videos"))
async def handle_videos(client, message):
    videos = await db.videos.find().to_list(length=None)
    video_list = "\n".join([f"{video['video_id']}: {video['category']}" for video in videos])
    await message.reply(f"Available videos:\n{video_list}")

# Language system
@app.on_message(filters.command("language"))
async def handle_language(client, message):
    await message.reply("Choose your language:\n1. English\n2. Bengali")

# Admin commands
@app.on_message(filters.user(ADMIN_IDS) & filters.command("stats"))
async def handle_stats(client, message):
    total_users = await db.users.count_documents({})
    await message.reply(f"Total users: {total_users}")

# Background tasks
async def premium_expiry_checker():
    while True:
        # Logic to check and update premium expiry
        await asyncio.sleep(86400)  # Check daily

if __name__ == "__main__":
    app.start()
    asyncio.create_task(premium_expiry_checker())
    app.idle()
