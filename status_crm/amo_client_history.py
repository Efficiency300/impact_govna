from config.config import Config
import aiohttp
from aiohttp import ClientTimeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_client_history(lead_id: str) -> str:
    url = f'{Config.BASE_URL_LEAD}/{lead_id}'
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        timeout = ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                lead_data = await response.json()

        custom_fields = lead_data.get('custom_fields_values', [])
        if not isinstance(custom_fields, list):
            custom_fields = []


        async def get_field_value(field_name):
            return next(
                (
                    field['values'][0]['value']
                    for field in custom_fields
                    if field.get('field_name') == field_name and field.get('values')
                ),
                None
            )

        # Extract field values
        child_name = await get_field_value("Имя ребенка")
        child_age = await get_field_value("Возраст")
        course_name = await get_field_value("Какой курс ИИ")
        number_phone = await get_field_value("Номер контракта")
        parent_name = await get_field_value("Имя родителя ИИ")
        meeting_type = await get_field_value("Тип встречи ИИ")

        # Formulate result string
        return (
            f'Имя: {child_name or "не указано"}\n'
            f'Возраст: {child_age or "не указано"}\n'
            f'Курс: {course_name or "не указано"}\n'
            f'Номер: {number_phone or "не указано"}\n'
            f'Имя родителя: {parent_name or "не указано"}\n'
            f'Тип встречи: {meeting_type or "не указано"}\n'
        )

    except aiohttp.ClientResponseError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
        return "Ошибка HTTP при получении данных."
    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}', exc_info=True)
        return "Произошла ошибка при обработке данных."







async def get_client_data(lead_id: str) -> dict:
    url = f'{Config.BASE_URL_LEAD}/{lead_id}'
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        timeout = ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                lead_data = await response.json()

        custom_fields = lead_data.get('custom_fields_values', [])
        if not isinstance(custom_fields, list):
            custom_fields = []


        async def get_field_value(field_name):
            return next(
                (
                    field['values'][0]['value']
                    for field in custom_fields
                    if field.get('field_name') == field_name and field.get('values')
                ),
                None
            )

        # Extract field values

        child_age = await get_field_value("Возраст")
        course_name = await get_field_value("Какой курс ИИ")
        number_phone = await get_field_value("Номер контракта")
        parent_name = await get_field_value("Имя родителя ИИ")
        meeting_type = await get_field_value("Тип встречи ИИ")
        message = "возраст :" + child_age + "\n" + "название курса :" + course_name + "\n" + "тип встречи :"  + meeting_type

        # Formulate result string
        return {
            'name': f'{parent_name or "не указано"}',
            'phone': f'{number_phone or "не указано"}',
            'note': f'{message or "не указано"}',

        }


    except aiohttp.ClientResponseError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
        return "Ошибка HTTP при получении данных."
    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}', exc_info=True)
        return "Произошла ошибка при обработке данных."
