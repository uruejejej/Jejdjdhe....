from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
import random

# ====== معلومات تسجيل الدخول للبوت ======
api_id = 26143445
api_hash = '1c22d45b404d1fc7853d2a2f456cbc3b'
bot_token = '7677482621:AAHwL3NPPlkNVFIbyGnSTpJYzq01mB_NMV4'

# ====== إعداد البوت ======
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# ====== تحميل ملف الردود ======
def load_replies(filename='text.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

vocabulary = load_replies()
used_replies = []
sending = {}

# ====== الصلاحيات ======
leader_id = [1264205748, 6378014896, 45269800, 5825190558, 5919774819]
admin_id = [6854132155]
allowed_users = leader_id + admin_id

def is_allowed(user_id):
    return user_id in allowed_users

def is_owner(user_id):
    return user_id in leader_id

# ====== أمر بدء ======
@client.on(events.NewMessage(pattern=r'(?i)^بدء(?:\s+(.*))?'))
async def handle_reply_command(event):
    global sending
    sender_id = event.sender_id
    chat_id = event.chat_id

    if not is_allowed(sender_id):
        await event.respond("ليس لديك صلاحية لاستخدام هذا الأمر.")
        return

    args = event.pattern_match.group(1)
    if args and args.strip().lower() == "توقف":
        sending[chat_id] = False
        await event.respond("تم إيقاف الإرسال بنجاح.")
        return

    mentioned_user = None
    count = 20  # عدد افتراضي
    parts = args.split() if args else []

    if parts:
        if parts[0].startswith('@'):
            mentioned_user = parts[0][1:]
            if len(parts) > 1 and parts[1].isdigit():
                count = min(int(parts[1]), 50)
        elif parts[0].isdigit():
            count = min(int(parts[0]), 50)

    original_msg = None
    if event.is_reply:
        original_msg = await event.get_reply_message()
        if not mentioned_user and original_msg.sender:
            if original_msg.sender.username:
                mentioned_user = original_msg.sender.username
            else:
                mentioned_user = str(original_msg.sender.id)

    if not mentioned_user:
        await event.respond("يرجى تحديد المستخدم المطلوب عبر المنشن أو الرد.")
        return

    try:
        if mentioned_user.isdigit():
            target_user_id = int(mentioned_user)
        else:
            target_entity = await client.get_entity(mentioned_user)
            target_user_id = target_entity.id

        me = await client.get_me()
        if target_user_id == me.id:
            await event.respond("لا يمكنني الرد على نفسي.")
            return

        if target_user_id in leader_id:
            await event.respond("لا يمكنك استخدام هذا الأمر على الزعيم.")
            return

    except Exception:
        await event.respond("تعذر تحديد المستخدم.")
        return

    if not vocabulary:
        await event.respond("ملف الردود فارغ.")
        return

    sending[chat_id] = True
    sent_messages = []

    for i in range(count):
        if not sending.get(chat_id, True):
            await event.respond("تم إيقاف الإرسال.")
            break

        if len(used_replies) == len(vocabulary):
            used_replies.clear()

        available_replies = list(set(vocabulary) - set(used_replies))
        chosen_reply = random.choice(available_replies)
        used_replies.append(chosen_reply)

        mention_text = f"@{mentioned_user}" if not mentioned_user.isdigit() else f"[المستخدم](tg://user?id={mentioned_user})"
        msg = f"{mention_text} {chosen_reply}"

        try:
            sent_msg = await client.send_message(
                chat_id,
                msg,
                reply_to=original_msg.id if original_msg else None,
                parse_mode='md')
            sent_messages.append(sent_msg.id)
        except:
            continue

        await asyncio.sleep(1)  # تأخير 1 ثانية بين كل رسالة

        # حذف الرسائل بعد تجميع 150 رسالة
        if len(sent_messages) >= 150:
            try:
                await client.delete_messages(chat_id, sent_messages)
            except:
                pass
            sent_messages = []

    # حذف أي رسائل متبقية بعد الانتهاء
    if sent_messages:
        try:
            await client.delete_messages(chat_id, sent_messages)
        except:
            pass

# ====== أمر الإيقاف اليدوي ======
@client.on(events.NewMessage(pattern=r'(?i)^(ايقاف|وقف|stop)$'))
async def stop_sending_command(event):
    sender_id = event.sender_id
    chat_id = event.chat_id
    if not is_allowed(sender_id):
        await event.respond("لا تملك صلاحية استخدام هذا الأمر.")
        return
    sending[chat_id] = False
    await event.respond("تم إيقاف الإرسال.")

# ====== أمر "لاتفتحخ" ======
@client.on(events.NewMessage(pattern=r'^لاتفتحخ$'))
async def dont_open(event):
    sender_id = event.sender_id
    if not is_allowed(sender_id):
        await event.respond("لا تملك صلاحية استخدام هذا الأمر.")
        return
    await event.respond("تم إصدار التحذير بعدم المتابعة.")

# ====== أمر "ايزن" بدون وسائط وبدون إيموجيات ======
@client.on(events.NewMessage(pattern=r'^ايزن$'))
async def yagami_reply(event):
    sender_id = event.sender_id

    responses = {
        1264205748: "مرحبًا سيدي أكاي الأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا ",
        6378014896: "مرحبًا سيدي فينيكس الأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا",
        45269800: "مرحبًا سيدي لاست الأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا",
        5825190558: "مرحبًا سيدي اوبيتو الأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا",
5325538278: "مرحبًا سيدي شوتو الأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا",
5919774819: "مرحبًا شين لأرواح قد تجمّعت والعالم ينحني تحت حكمك كل شيء يسير وفق إرادتك العليا"
    }

    response = responses.get(sender_id)

    if response:
        await event.respond(response)
    else:
        await event.respond("أنت لست من الزعماء ولا يحق لك استخدام هذا الأمر.")

# ====== أمر "معلومات" المستخدم ======
@client.on(events.NewMessage(pattern=r'^معلومات$'))
async def user_info(event):
    try:
        if event.is_reply:
            replied_msg = await event.get_reply_message()
            user = await client.get_entity(replied_msg.sender_id)
        else:
            user = await client.get_entity(event.sender_id)

        user_id = user.id
        first_name = user.first_name or "لا يوجد"
        last_name = user.last_name or ""
        username = f"@{user.username}" if user.username else "لا يوجد"
        full_name = f"{first_name} {last_name}".strip()

        user_info = await client.get_input_entity(user)
        user_full = await client(GetFullUserRequest(user_info))
        created_date = user_full.user.date

        await event.respond(
            f"""معلومات المستخدم:
الاسم: {full_name}
المعرف: `{user_id}`
اليوزر: {username}
تاريخ الإنشاء: `{created_date.strftime('%Y-%m-%d %H:%M:%S')}`""",
            parse_mode='md'
        )

    except Exception:
        await event.respond("تعذر جلب المعلومات. قد يكون المستخدم محظورًا أو غير معروف.")

# ====== تشغيل البوت ======
print("البوت يعمل بنجاح.")
client.run_until_disconnected()