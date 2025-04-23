import os
from aiogram import Bot, Dispatcher, executor, types
import random
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

# Создание директории для временных изображений, если она не существует
if not os.path.exists('./tmp_gen'):
    os.makedirs('./tmp_gen')

# Замена safety_checker на дефолтный (могут быть ошибки по NSFW контенту)
def dummy(images, **kwargs):
    return images, False

# Генерация изображения
async def generate_image(message_context):
    with autocast("cuda"):
        image = pipe(message_context.text, guidance_scale=6).images[0]
    file_id = random.randint(10000, 10000000)
    image.save(f"./tmp_gen/{file_id}.png")
    return file_id  

# Подключаемся к Telegram Bot API с использованием переменной окружения
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Загрузка модели для генерации изображений
print("[DEBUG] Loading model")
pipe = StableDiffusionPipeline.from_pretrained(
    'hakurei/waifu-diffusion',
    torch_dtype=torch.float32
).to('cuda')

# Обработчики команд
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    with open('./images/2.png', 'rb') as photo:
        await message.answer_photo(photo, caption="Используйте команду /waifu, чтобы сгенерировать картинку")

@dp.message_handler(commands=['waifu'])
async def waifu(message: types.Message):
    with open('./images/1.png', 'rb') as photo:
        await message.answer_photo(photo, caption="Напишите любой текст (на английском, указывая параметры через запятую.\nНапример: looking at viewer, masterpiece, best quality, bright hair, blue eyes, outdoors\nМетодичка по параметрам: /prompts")

@dp.message_handler(commands=['prompts'])
async def waifu(message: types.Message):
    with open('./images/0.png', 'rb') as photo:
        await message.answer_photo(photo, caption=
'''
Рекомендуем всегда использовать
masterpiece
high quality
''')

# Отправка сгенерированного изображения
async def send_result_waifu(message: types.Message, waifu):
    with open(f'./tmp_gen/{waifu}.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Generated waifu image')

@dp.message_handler()
async def echo(message: types.Message):
    # Отключение safety_checker (чтобы не было NSFW предупреждений)
    pipe.safety_checker = dummy
    await message.answer("Процесс генерации запущен, ожидайте результата (~20 секунд)")
    res = await generate_image(message)
    with open(f'./tmp_gen/{res}.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Generated waifu image')

# Запуск б
