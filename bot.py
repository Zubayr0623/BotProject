import asyncio
import re
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "8753255522:AAFF44KSdLD365yw3PU-bcTB6gJWKvINZ-M"

# ADMIN ID
ADMIN_ID = 1388906583

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# DATABASE
# =========================

# TESTLAR
tests = {}

# O'QUVCHILAR
students = {}

# NATIJALAR
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

            "/addtest TEST_ID BOSHLANISH TUGASH JAVOBLAR\n\n"

            "📍 Misol:\n\n"

            "/addtest 331 "
            "18.05.2026-20:00 "
            "19.05.2026-20:00 "
            "1A 2B 3C 4D 5A\n\n"

            "♾ Vaqtsiz test:\n\n"

            "/addtest 332 0 0 1A 2B 3C\n\n"

            "📊 Natijalarni ko'rish:\n"
            "/results"
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
# MAIN HANDLER
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
        # TEST QO'SHISH
        # =========================

        if text.startswith("/addtest"):

            parts = text.split()

            if len(parts) < 5:

                await message.answer(
                    "❌ Format noto'g'ri.\n\n"

                    "📌 To'g'ri format:\n\n"

                    "/addtest 331 "
                    "18.05.2026-20:00 "
                    "19.05.2026-20:00 "
                    "1A 2B 3C"
                )

                return

            test_id = parts[1]

            start_text = parts[2]

            end_text = parts[3]

            # =========================
            # VAQT
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
                        "❌ Sana formatida xato.\n\n"

                        "📌 Format:\n"
                        "18.05.2026-20:00"
                    )

                    return

            # =========================
            # JAVOBLAR
            # =========================

            answers = {}

            try:

                for item in parts[4:]:

                    number = int(item[:-1])

                    answer = item[-1].upper()

                    answers[number] = answer

            except:

                await message.answer(
                    "❌ Javob formatida xato."
                )

                return

            # =========================
            # TEST SAQLASH
            # =========================

            tests[test_id] = {

                "answers": answers,

                "start_time": start_time,

                "end_time": end_time
            }

            # vaqt matni
            if start_time is None:

                time_text = "♾ Cheklanmagan"

            else:

                time_text = (
                    f"🟢 {start_text}\n"
                    f"🔴 {end_text}"
                )

            await message.answer(
                f"✅ Test saqlandi\n\n"

                f"🆔 Test ID: {test_id}\n\n"

                f"{time_text}\n\n"

                f"📚 Savollar soni: {len(answers)}"
            )

            return

        # =========================
        # NATIJALAR
        # =========================

        if text == "/results":

            if not results:

                await message.answer(
                    "📭 Hali natijalar yo'q."
                )

                return

            response = "📊 O'quvchilar natijalari\n\n"

            for i, result in enumerate(results, start=1):

                response += (

                    f"{i}. 👤 {result['name']}\n"

                    f"🆔 Test: {result['test_id']}\n"

                    f"✅ {result['correct']}/{result['total']}\n"

                    f"❌ Xato savollar: "
                    f"{result['wrong_questions']}\n"

                    f"📈 {result['percent']:.0f}%\n"

                    f"🕒 {result['time']}\n\n"
                )

            await message.answer(response)

            return

        return

    # =========================
    # USER NAME SAVE
    # =========================

    if user_id in students and students[user_id].get("waiting_name"):

        students[user_id]["name"] = text

        students[user_id]["waiting_name"] = False

        await message.answer(
            "✅ Ism saqlandi.\n\n"

            "📌 Test javoblarini yuboring.\n\n"

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
            "❌ Format noto'g'ri.\n\n"

            "📌 Misol:\n"
            "331+1a2b3c4d5a"
        )

        return

    # =========================
    # AJRATISH
    # =========================

    test_id, answers_text = text.split("+", 1)

    # test mavjudmi
    if test_id not in tests:

        await message.answer(
            "❌ Test ID topilmadi."
        )

        return

    test_data = tests[test_id]

    start_time = test_data["start_time"]

    end_time = test_data["end_time"]

    now = datetime.now()

    # =========================
    # VAQT TEKSHIRISH
    # =========================

    if start_time is not None:

        # hali boshlanmagan
        if now < start_time:

            await message.answer(
                "⏳ Test hali boshlanmagan."
            )

            return

        # tugagan
        if now > end_time:

            await message.answer(
                "⛔ Test vaqti tugagan."
            )

            return

    # =========================
    # JAVOBLARNI O'QISH
    # =========================

    pattern = r'(\d+)([a-z])'

    matches = re.findall(pattern, answers_text)

    if not matches:

        await message.answer(
            "❌ Javob formatida xato."
        )

        return

    student_answers = {}

    for number, answer in matches:

        student_answers[int(number)] = answer.upper()

    # =========================
    # TEKSHIRISH
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
    # NATIJA SAQLASH
    # =========================

    results.append({

        "name": student_name,

        "test_id": test_id,

        "correct": correct,

        "total": total,

        "wrong_questions": wrong_questions,

        "percent": percent,

        "time": datetime.now().strftime("%d.%m.%Y %H:%M")
    })

    # =========================
    # USER RESULT
    # =========================

    await message.answer(
        f"👤 {student_name}\n\n"

        f"🆔 Test ID: {test_id}\n\n"

        f"✅ To'g'ri: {correct}\n"

        f"❌ Noto'g'ri: {wrong_count}\n"

        f"📈 Natija: {percent:.0f}%\n\n"

        f"❗ Xato savollar: {wrong_questions}"
    )

# =========================
# RUN
# =========================

async def main():

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())