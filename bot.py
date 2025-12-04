import json
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8558099756:AAG5w3fMkQxyrA3xK8DpwVAxZEaE7EuRRwU"
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DATA_FILE = "user_data.json"
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except:
    data = {}

questions = [
    "Как часто вы чувствуете эмоциональное истощение от своих повседневных занятий?",
    "Как часто вы чувствуете себя измотанным в конце дня?",
    "Как часто вы устаёте при мысли о предстоящем дне?",
    "Как часто занятия на протяжении всего дня даются вам с большим трудом?",
    "Как часто вы чувствуете выгорание от своих занятий?",
    "Как часто вы теряете интерес к своим занятиям?",
    "Как часто вы становитесь менее энтузиастичным по поводу своих занятий?",
    "Как часто вы становитесь более циничным относительно пользы своих занятий?",
    "Как часто вы сомневаетесь в значимости своих занятий?",
    "Как часто вы чувствуете уверенность в том, что эффективно справляетесь со своими занятиями?"
]

daily_plan = [
    {"title": "Журналирование для саморефлексии",
     "theory": "Эмоциональное выгорание часто возникает из-за накопленного стресса. Регулярное фиксирование мыслей помогает разгрузить разум, выявить триггеры и восстановить контроль над эмоциями.",
     "tasks": ["Запишите 3 мысли о дне в дневнике за 5 минут перед сном.",
               "Отметьте один положительный момент, чтобы сместить фокус с негатива."]},
    {"title": "Физическая активность для энергии",
     "theory": "Короткие упражнения стимулируют эндорфины, улучшают настроение и помогают восстановить жизненную силу.",
     "tasks": ["Сделайте 10-минутную прогулку на свежем воздухе.",
               "Выполните простые растяжки для шеи и плеч, чтобы снять напряжение."]},
    {"title": "Практика сна для восстановления",
     "theory": "Хорошая гигиена сна помогает стабилизировать эмоции и повысить устойчивость к стрессу.",
     "tasks": ["Запишите 3 задачи на завтра за 5 минут перед сном.",
               "Попробуйте прогрессивную мышечную релаксацию на 5 минут в постели."]},
    {"title": "Хобби для радости",
     "theory": "Возвращение к хобби восстанавливает баланс и чувство достижения вне учёбы.",
     "tasks": ["Посвятите 15 минут любимому занятию, как чтение или рисование.",
               "Установите таймер, чтобы не отвлекаться на другие дела."]},
    {"title": "Социальные связи для поддержки",
     "theory": "Регулярные взаимодействия снижают эмоциональное напряжение и дают перспективу.",
     "tasks": ["Позвоните или напишите другу о своём дне на 5 минут.",
               "Поделитесь одной заботой и выслушайте ответ."]},
    {"title": "Установка границ для баланса",
     "theory": "Умение говорить 'нет' сохраняет энергию и предотвращает переутомление.",
     "tasks": ["Откажитесь от одной ненужной задачи сегодня.",
               "Запишите, почему это решение полезно для вас."]},
    {"title": "Дыхательные упражнения для спокойствия",
     "theory": "Дыхательные практики активируют парасимпатическую систему, снижая кортизол.",
     "tasks": ["Сделайте 5 минут глубокого дыхания (4 секунды вдох, 4 выдох).",
               "Повторите во время перерыва в учёбе."]},
    {"title": "Питание для настроения",
     "theory": "Здоровые привычки поддерживают мозг и тело.",
     "tasks": ["Съешьте полезный перекус с орехами или фруктами.",
               "Выпейте стакан воды и отметьте, как это влияет на самочувствие."]},
    {"title": "Благодарность для перспективы",
     "theory": "Практика благодарности перестраивает мышление на позитив.",
     "tasks": ["Запишите 3 вещи, за которые благодарны, за 5 минут.",
               "Поделитесь одной с кем-то близким."]},
    {"title": "Планирование для контроля",
     "theory": "Организация снижает стресс и даёт чувство прогресса.",
     "tasks": ["Составьте список из 3 задач на день и отметьте выполненные.",
               "Используйте Pomodoro: 25 минут работы, 5 минут перерыва."]}
]

user_scores = {}

# ----------------- Кнопки -----------------
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Пройти тест", callback_data="start_test"),
        InlineKeyboardButton(text="Мой профиль", callback_data="profile")
    )
    builder.row(
        InlineKeyboardButton(text="SOS", callback_data="sos")
    )
    return builder.as_markup()

def answer_keyboard(q_index):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Никогда", callback_data=f"{q_index}_0"),
        InlineKeyboardButton(text="Редко", callback_data=f"{q_index}_1"),
        InlineKeyboardButton(text="Иногда", callback_data=f"{q_index}_2")
    )
    builder.row(
        InlineKeyboardButton(text="Часто", callback_data=f"{q_index}_3"),
        InlineKeyboardButton(text="Всегда", callback_data=f"{q_index}_4")
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="prev_question")
    )
    return builder.as_markup()

def done_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Выполнил ✅", callback_data="done_day"))
    return builder.as_markup()

def sos_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад", callback_data="main_back"))
    return builder.as_markup()

# ----------------- Хэндлеры -----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in data:
        data[user_id] = {"days_completed": 0, "daily_done": False, "last_score": 0}
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "sos")
async def sos_handler(callback: types.CallbackQuery):
    text = (
        "Психологическая служба РУТ (МИИТ)\n\n"
        "Как записаться на консультацию?\n"
        "📞 Позвонить: +7 (499) 973-46-00\n"
        "✉ Написать: psysupport@miit.ru\n"
        "🏢 Лично обратиться в Психологическую службу"
    )
    await callback.message.answer(text, reply_markup=sos_back_keyboard())

@dp.callback_query(lambda c: c.data=="main_back")
async def back_from_sos(callback: types.CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    days = data[user_id]["days_completed"]
    last_score = data[user_id]["last_score"]
    # Прогресс-бар
    progress = int((days / 10) * 10)
    bar = "🟩" * progress + "⬜" * (10 - progress)
    text = f"Ваш прогресс:\n{bar} ({days}/10)\nПоследний результат теста: {last_score}"
    await callback.message.answer(text, reply_markup=main_menu())

# ----------------- Тест -----------------
@dp.callback_query(lambda c: c.data == "start_test")
async def start_test(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    user_scores[user_id] = {"answers": {}, "current": 0}
    await send_question(user_id, callback.message)

async def send_question(user_id, message_to_edit=None):
    q_index = user_scores[user_id]["current"]
    if q_index >= len(questions):
        # Конец теста
        score = sum(user_scores[user_id]["answers"].values())
        data[user_id]["last_score"] = score
        # Определяем степень
        if score <= 10:
            level = "Низкая"
            advice = "🌸 Попробуйте немного отдохнуть, сделать чай и улыбнуться!"
            await bot.send_message(user_id, f"Результат теста: {score}\nСтепень выгорания: {level}\n{advice}")
        elif score <= 20:
            level = "Средняя"
            await bot.send_message(user_id, f"Результат теста: {score}\nСтепень выгорания: {level}\nЗапускаем задания для восстановления энергии.")
            data[user_id]["days_completed"] += 1
            await send_day_task(user_id, 1)
        else:
            level = "Высокая"
            await bot.send_message(user_id, f"Результат теста: {score}\nСтепень выгорания: {level}\nЗапускаем задания для восстановления энергии.")
            data[user_id]["days_completed"] += 1
            await send_day_task(user_id, 1)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        del user_scores[user_id]
        return

    text = f"Вопрос {q_index+1}/{len(questions)}:\n{questions[q_index]}"
    if message_to_edit:
        await message_to_edit.edit_text(text, reply_markup=answer_keyboard(q_index))
    else:
        await bot.send_message(user_id, text, reply_markup=answer_keyboard(q_index))

@dp.callback_query(lambda c: c.data[0].isdigit() or c.data=="prev_question")
async def handle_answer(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    q_index = user_scores[user_id]["current"]

    if callback.data == "prev_question" and q_index > 0:
        user_scores[user_id]["current"] -= 1
        await send_question(user_id, callback.message)
        return

    answer = int(callback.data.split("_")[1])
    user_scores[user_id]["answers"][q_index] = answer
    user_scores[user_id]["current"] += 1
    await send_question(user_id, callback.message)

# ----------------- Дневные задания -----------------
async def send_day_task(user_id, day):
    plan = daily_plan[day-1]
    text = (
        f"📅 День {day}: {plan['title']}\n\n"
        f"🧠 Теория:\n{plan['theory']}\n\n"
        f"✅ Задания:\n1️⃣ {plan['tasks'][0]}\n2️⃣ {plan['tasks'][1]}"
    )
    await bot.send_message(user_id, text, reply_markup=done_keyboard())
    data[user_id]["current_day"] = day
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@dp.callback_query(lambda c: c.data=="done_day")
async def done_day(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    day = data[user_id]["current_day"]
    data[user_id]["daily_done"] = True
    await callback.message.answer(f"День {day} отмечен как выполненный ✅ \nСледующее задание придет вам завтра!", reply_markup=main_menu())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ----------------- Авто-отправка заданий -----------------
async def daily_scheduler():
    while True:
        now = datetime.now()
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        for user_id in data:
            if not data[user_id].get("daily_done", False):
                day = data[user_id]["days_completed"] + 1
                if day <= 10:
                    await send_day_task(user_id, day)
                    data[user_id]["daily_done"] = False
        await asyncio.sleep(60)

# ----------------- Запуск -----------------
async def main():
    asyncio.create_task(daily_scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
