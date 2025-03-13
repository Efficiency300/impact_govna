import json
import re
from icecream import ic


async def get_converse(chat_history: json) -> str:
    try:
        conversation = []
        user_pattern = re.compile(r"User:\s*(.*)")
        max_messages = 2  # Лимит на количество сообщений

        for i, message in enumerate(chat_history.get('data', [])):
            role = message.get('role')
            content = message.get('content', [{}])[0].get('text', {}).get('value', "").strip()

            if not content:  # Пропускаем пустой контент
                continue

            if role == 'user':
                # Обработка сообщений пользователя
                match = user_pattern.match(f"User: {content}")
                user_content = match.group(1) if match else content
                conversation.append(f"клиент: {user_content} сообщение")
            elif role == 'assistant':
                # Обработка сообщений ассистента
                conversation.append(f"ассистент: {content}")

            if i + 1 == max_messages:  # Ограничиваем обработку
                break

        result = "\n".join(conversation)
        ic(result)
        return result

    except (json.JSONDecodeError, KeyError) as e:
        ic(f"Ошибка обработки данных: {e}")
        return f"Ошибка: {e}"
    except Exception as e:
        ic(f"Непредвиденная ошибка: {e}")
        return f"Ошибка при обработке текста сообщения: {e}"
