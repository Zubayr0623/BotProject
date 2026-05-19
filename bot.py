import asyncio
import logging
import os
import re
from datetime import datetime

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application
)

from dotenv import load_dotenv

# =========================
# ENV
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

# =========================
# WEBHOOK
# =========================

WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")

WEBHOOK_PATH = "/webhook"

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEB_SERVER_HOST = "0.0.0.0"

WEB_SERVER_PORT = int(os.getenv("PORT", 10000))

# =========================
# BOT
# =========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

# =========================
# DATABASE
# =========================

tests = {}

students = {}

results = []

# =========================
# START
# =========================

@dp.message(Command("start"))
async def start_handler(message: Message):

    user_id = message.from_user.id

    # ADMIN
    if user_id == ADMIN_ID:

        await message.answer(
            "👨‍💼 Admin panel\n\n"

            "📌 Test qo'shish:\n\n"

            "/addtest TEST_ID "
            "BOSHLANISH "
            "TUGASH "
            "JAVOBLAR\n\n"

            "📍 Misol:\n\n"

            "/addtest 331 "
            "18.05.2026-20:00 "
            "19.05.2026-20:00 "
            "1A 2B 3C 4D 5A\n\n"

            "♾ Vaqtsiz test:\n\n"

            "/addtest 332 0 0 1A 2B 3C\n\n"

            "📊 Natijalar:\n"
            "/results\n\n"

            "📊 Bitta test:\n"
            "/results 331"
        )

    # USER
    else:

        students[user_id] = {
            "waiting_name": True
        }

        await message.answer(
            "👤 Ism familiyangizni kiriting:"
        )

# =========================
# MAIN
# =========================

@dp.message()
async def main_handler(message: Message):

    user_id = message.from_user.id

    text = message.text.strip()

    # =========================
    # ADMIN
    # =========================

    if user_id == ADMIN_ID:

        # =========================
        # ADD TEST
        # =========================

        if text.startswith("/addtest"):

            parts = text.split()

            if len(parts) < 5:

                await message.answer(
                    "❌ Format xato."
                )

                return

            test_id = parts[1]

            start_text = parts[2]

            end_text = parts[3]

            # =========================
            # TIME
            # =========================

            if start_text == "0" and end_text == "0":

                start_time = None
                end_time = None

            else:

                try:

                    start_time = datetime.strptime(
                        start_text,
                        "%d.%m.%Y-%H:%M"
                    )

                    end_time = datetime.strptime(
                        end_text,
                        "%d.%m.%Y-%H:%M"
                    )

                except:

                    await message.answer(
                        "❌ Sana format xato.\n\n"
                        "18.05.2026-20:00"
                    )

                    return

            # =========================
            # ANSWERS
            # =========================

            answers = {}

            try:

                for item in parts[4:]:

                    number = int(item[:-1])

                    answer = item[-1].upper()

                    answers[number] = answer

            except:

                await message.answer(
                    "❌ Javoblar xato."
                )

                return

            # =========================
            # SAVE
            # =========================

            tests[test_id] = {

                "answers": answers,

                "start_time": start_time,

                "end_time": end_time
            }

            if start_time is None:

                time_text = "♾ Cheklanmagan"

            else:

                time_text = (
                    f"🟢 {start_text}\n"
                    f"🔴 {end_text}"
                )

            await message.answer(
                f"✅ Test saqlandi\n\n"

                f"🆔 ID: {test_id}\n"

                f"{time_text}\n\n"

                f"📚 Savollar: {len(answers)}"
            )

            return

        # =========================
        # RESULTS
        # =========================

        if text.startswith("/results"):

            parts = text.split()

            # ALL RESULTS
            if len(parts) == 1:

                if not results:

                    await message.answer(
                        "📭 Natijalar yo'q."
                    )

                    return

                response = "📊 Barcha natijalar\n\n"

                for i, result in enumerate(results, 1):

                    response += (

                        f"{i}. 👤 {result['name']}\n"

                        f"🆔 Test: "
                        f"{result['test_id']}\n"

                        f"✅ {result['correct']}/"
                        f"{result['total']}\n"

                        f"❌ Xato: "
                        f"{result['wrong_questions']}\n"

                        f"📈 "
                        f"{result['percent']:.0f}%\n"

                        f"🕒 {result['time']}\n\n"
                    )

                await message.answer(response)

                return

            # ONE TEST RESULTS
            if len(parts) == 2:

                test_id = parts[1]

                filtered = [

                    r for r in results
                    if r["test_id"] == test_id
                ]

                if not filtered:

                    await message.answer(
                        "📭 Natija topilmadi."
                    )

                    return

                response = (
                    f"📊 {test_id} TEST NATIJALARI\n\n"
                )

                for i, result in enumerate(filtered, 1):

                    response += (

                        f"{i}. 👤 {result['name']}\n"

                        f"✅ {result['correct']}/"
                        f"{result['total']}\n"

                        f"❌ Xato: "
                        f"{result['wrong_questions']}\n"

                        f"📈 "
                        f"{result['percent']:.0f}%\n"

                        f"🕒 {result['time']}\n\n"
                    )

                await message.answer(response)

                return

        return

    # =========================
    # NAME SAVE
    # =========================

    if user_id in students and students[user_id].get(
        "waiting_name"
    ):

        students[user_id]["name"] = text

        students[user_id]["waiting_name"] = False

        await message.answer(
            "✅ Ism saqlandi.\n\n"

            "📌 Test yuboring.\n\n"

            "Misol:\n"
            "331+1a2b3c4d5a"
        )

        return

    # =========================
    # FORMAT
    # =========================

    text = text.lower()

    if "+" not in text:

        await message.answer(
            "❌ Format xato.\n\n"
            "Misol:\n"
            "331+1a2b3c4d5a"
        )

        return

    # =========================
    # SPLIT
    # =========================

    test_id, answers_text = text.split("+", 1)

    # TEST EXISTS
    if test_id not in tests:

        await message.answer(
            "❌ Test topilmadi."
        )

        return

    test_data = tests[test_id]

    start_time = test_data["start_time"]

    end_time = test_data["end_time"]

    now = datetime.now()

    # =========================
    # TIME CHECK
    # =========================

    if start_time is not None:

        if now < start_time:

            await message.answer(
                "⏳ Test boshlanmagan."
            )

            return

        if now > end_time:

            await message.answer(
                "⛔ Test tugagan."
            )

            return

    # =========================
    # ANSWERS READ
    # =========================

    pattern = r'(\d+)([a-z])'

    matches = re.findall(pattern, answers_text)

    if not matches:

        await message.answer(
            "❌ Javob xato."
        )

        return

    student_answers = {}

    for number, answer in matches:

        student_answers[int(number)] = answer.upper()

    # =========================
    # CHECK
    # =========================

    correct_answers = test_data["answers"]

    correct = 0

    wrong_questions = []

    for q_num, true_answer in correct_answers.items():

        if student_answers.get(q_num) == true_answer:

            correct += 1

        else:

            wrong_questions.append(q_num)

    total = len(correct_answers)

    wrong_count = total - correct

    percent = correct / total * 100

    student_name = students[user_id]["name"]

    # =========================
    # SAVE RESULT
    # =========================

    results.append({

        "name": student_name,

        "test_id": test_id,

        "correct": correct,

        "total": total,

        "wrong_questions": wrong_questions,

        "percent": percent,

        "time": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )
    })

    # =========================
    # RESULT
    # =========================

    await message.answer(
        f"👤 {student_name}\n\n"

        f"🆔 Test: {test_id}\n\n"

        f"✅ To'g'ri: {correct}\n"

        f"❌ Noto'g'ri: {wrong_count}\n"

        f"📈 Natija: {percent:.0f}%\n\n"

        f"❗ Xato savollar:\n"
        f"{wrong_questions}"
    )

# =========================
# STARTUP
# =========================

async def on_startup(bot: Bot):

    await bot.set_webhook(WEBHOOK_URL)

    print("✅ Webhook o'rnatildi")

# =========================
# SHUTDOWN
# =========================

async def on_shutdown(bot: Bot):

    await bot.delete_webhook()

# =========================
# MAIN
# =========================

def main():

    dp.startup.register(on_startup)

    dp.shutdown.register(on_shutdown)

    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(
        app,
        host=WEB_SERVER_HOST,
        port=WEB_SERVER_PORT
    )

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    main()