import time
import openai
from loguru import logger
from app.config import Settings

settings = Settings()

assistant_id = settings.ASSISTANT_ID


def create_thread():
    try:
        thread = openai.beta.threads.create()
        logger.info(f"Создан новый поток: {thread.id}")
        return thread
    except Exception as e:
        logger.error(f"Ошибка при создании потока: {e}")
        return None


async def create_run(user_input, thread_id, user_id):
    logger.info(f"""Запуск нового рана для пользователя {
        user_id} в потоке {thread_id}""")
    try:
        # Добавляем сообщение пользователя в поток
        openai.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_input)

        # Запускаем ассистента
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            max_prompt_tokens=5000,
            max_completion_tokens=10000,
        )

        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id)

            if run_status.status == "completed":
                # Сохраняем токены и другие данные
                # run_data = json.loads(run_status.json())
                # prompt_tokens = run_data.get("usage", {}).get("prompt_tokens")
                # completion_tokens = run_data.get(
                #    "usage", {}).get("completion_tokens")
                # total_tokens = run_data.get("usage", {}).get("total_tokens")
                # model = run_data.get("model")

                # Получение последнего сообщения от ассистента
                messages = openai.beta.threads.messages.list(
                    thread_id=thread_id)
                if messages.data:
                    response = messages.data[0].content[0].text.value
                else:
                    response = "Ошибка получения ответа от помощника."
                break

            elif run_status.status == "requires_action":
                logger.warning("Run requires action. Processing...")
                # (Обработка действия, если требуется)

            elif run_status.status == "incomplete":
                logger.info("Run is incomplete. Retrying...")
            else:
                logger.error(f"Неизвестный статус рана: {run_status.status}")

            time.sleep(1)  # Ожидание перед следующим запросом статуса

        return response

    except Exception as e:
        logger.error(f"Ошибка при запуске рана: {e}")
        return "Произошла ошибка при обработке вашего запроса."
