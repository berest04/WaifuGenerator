from config import API_TOKEN
from aiogram import Bot, Dispatcher, executor, types
import random
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
import transformers
import time
import os

# Создание директории для временных изображений, если она не существует
if not os.path.exists('./tmp_gen'):
    os.makedirs('./tmp_gen')

def dummy(images, **kwargs):
    return images, False

async def generate_image(message_context):
    with autocast("cuda"):
        image = pipe(message_context.text, guidance_scale=6).images[0]
    file_id = random.randint(10000, 10000000)
    image.save(f"./tmp_gen/{file_id}.png")
    return file_id  

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

print("[DEBUG] Loading model")
pipe = StableDiffusionPipeline.from_pretrained(
    'hakurei/waifu-diffusion',
    torch_dtype=torch.float32
).to('cuda')


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


async def send_result_waifu(message: types.Message, waifu):
    with open(f'./tmp_gen/{waifu}.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Generated waifu image')


@dp.message_handler()
async def echo(message: types.Message):
    # Bypass NSFW checker :)
    # Only for work; freelance yepta
    pipe.safety_checker = dummy
    await message.answer("Процесс генерации запущен, ожидайте результата (~20 секунд)")
    res = await generate_image(message)
    with open(f'./tmp_gen/{res}.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Generated waifu image')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
