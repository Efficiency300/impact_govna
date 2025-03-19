import re
import asyncio

class MarkdownProcessor:
    @staticmethod
    async def strip_markdown(text):
        if not text:
            return text

        # Удаление заголовков (например, ### Заголовок)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Удаление жирного текста (**текст**)
        text = re.sub(r'(\*\*)(.*?)\1', r'\2', text)

        # Удаление курсива (*текст*)
        text = re.sub(r'(\*)(.*?)\1', r'\2', text)

        # Удаление списков (- или *)
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)

        # Обработка ссылок [текст](URL) с поддержкой вложенных скобок
        text = re.sub(
            r'\[([^\]]+)\]\(((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*)\)',
            r'\1 (\2)',
            text
        )

        # Удаление строк таблиц
        text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)

        # Удаление разделительных линий таблицы (--- | --- | ---)
        text = re.sub(r'^\s*\|?(\s*-+\s*\|)+\s*$', '', text, flags=re.MULTILINE)

        # Удаление изображений ![alt](URL)
        text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)

        # Удаление горизонтальных линий
        text = re.sub(r'^---$', '', text, flags=re.MULTILINE)

        # Удаление обратных кавычек (для кода)
        text = re.sub(r'`', '', text)

        # Удаление лишних пустых строк
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()