import asyncio
import logging
from aiogram.methods import DeleteWebhook
from aiogram import Bot, Dispatcher, types, html
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import StatesGroup, State
from config import API_TOKEN, OPEN_WEATHER_TOKEH, code_to_smail
from keyboards import start_kb, wether_kb
from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from util import check_format, get_adrr, format_msg, get_weaher, wind_direction

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=API_TOKEN)

# Диспетчер
dp = Dispatcher()


class Coordinates(StatesGroup):
    latitude = State()
    longitude = State()

place_coord = {}


@dp.message(Command("start"))
async def start(message):
    await message.answer(f"Привет, {html.bold(html.quote(message.from_user.first_name))}",
                         parse_mode=ParseMode.HTML, reply_markup=start_kb)


# Машина состояний - ввод координат с клавиатуры - НАЧАЛО
@dp.message(F.text == "Введите координаты")
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(text="Введите широту:")
    await state.set_state(Coordinates.latitude)


@dp.message(Coordinates.latitude)
async def set_latitude(message: Message, state: FSMContext):
    try:
        msg = format_msg(message.text)
        check = check_format(msg)
        if check and (-90 < float(msg) < 90):
            await state.update_data(latitude=msg)
            await message.answer(text="Введите долготу:")
            await state.set_state(Coordinates.longitude)
        else:
            raise ValueError
    except ValueError as err:
        await message.reply(text='Ввод некорректный,\nШирота должна быть между -90 и 90!!!')
        await message.answer(text="Введите широту:")
        await state.set_state(Coordinates.latitude)


@dp.message(Coordinates.longitude)
async def set_longitude(message: Message, state: FSMContext):
    try:
        msg = format_msg(message.text)
        check = check_format(msg)
        if check:
            await state.update_data(longitude=msg)
            data = await state.get_data()
            lati = data.get('latitude')
            longi = data.get("longitude")
            place_coord['latitude'] = lati
            place_coord['longitude'] = longi
            await message.answer(text=f'Широта: {lati} , \nДолгота: {longi}')
            print(",".join(reversed(get_adrr([lati, longi]).split(","))))
            location = ",".join(reversed(get_adrr([lati, longi]).split(",")))
            await message.answer(text=location, reply_markup=wether_kb)
            await state.clear()
        else:
            raise ValueError
    except ValueError as err:
        print(err)
        await message.reply(text='Ввод некорректный!!!')
        await message.answer(text="Введите долготу:")
        await state.set_state(Coordinates.longitude)


@dp.message(F.location)
async def cmd_food(message: Message):
    lati = message.location.latitude
    longi = message.location.longitude
    place_coord['latitude'] = lati
    place_coord['longitude'] = longi
    location = ",".join(reversed(get_adrr([lati, longi]).split(",")))
    await message.answer(text=location)
    await message.answer(text=f'Широта:{lati} \nДолгота:{longi}', reply_markup=wether_kb)
    print(lati, longi)

# Запуск процесса поллинга новых апдейтов


@dp.callback_query(F.data == "get_wether_now")
async def get_weather_now(callback: types.CallbackQuery):
    lati = place_coord['latitude']
    longi = place_coord['longitude']
    await callback.answer(f'ш: {lati} д: {longi}')
    try:
        result = get_weaher(lati, longi, OPEN_WEATHER_TOKEH)
        temper = float(result['main']['temp'])   #- 273.15
        pressure = result['main']['pressure']
        humidity = result['main']['humidity']
        wind_speed = result['wind']['speed']
        wind_gust = result['wind']['gust']
        wind_deg = wind_direction(result['wind']['deg'])
        weather_main = result['weather'][0]['main']
        weather_description = result['weather'][0]['description']
        if weather_main in code_to_smail:
            code_smail = code_to_smail[weather_main]
        else:
            code_smail = 'Неопределено'

        await callback.message.answer(text=
                                      f'<em>Состояние: </em> <b>{code_smail}</b>\n'
                                      f'<em>Температура:</em> <b>{temper:.1f} °C</b>\n'
                                      f'<em>Влажность:</em> <b>{humidity}</b> %\n'
                                      f'<em>Атм.давление:</em> <b>{pressure}</b> гПа ({pressure * 0.75} мм.р.ст)\n'
                                      f'<em>Скорость ветра:</em> <b>{wind_speed}</b> м/с\n'
                                      f'<em><u>порывы до {wind_gust} м/с</u></em>\n'
                                      f'<em>Ветер </em> <b>{wind_deg}</b>', parse_mode='html')
        await callback.answer()
    except Exception as err:
        print(err)


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
