from django.core.management import BaseCommand
from aiogram import executor, types
from bot_file.loader import db


async def on_startup(_):
    print("Bot has been successfully launched!")


# Запуск бота, обязательно management -> commands -> название -> создание класса Command(BaseCommand)
class Command(BaseCommand):

    def handle(self, *args, **options):

        @db.message_handler(commands=None, regexp=None)
        async def unknown_text(message: types.Message):
            await message.answer("Простите, но я не понимаю вас ☹️\n\n"
                                 "Попробуйте использовать команду Помощь ⭐️",
                                 )

        executor.start_polling(db, skip_updates=True, on_startup=on_startup)