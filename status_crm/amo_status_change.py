import re
import aiohttp
from config.config import Config
from status_crm.update_lead_status import update_lead_status

async def change_status(lead_id: str, response_text: str) -> None:
    url = f"{Config.BASE_URL_LEAD}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:

        new_child_name = re.search(r"Имя ребёнка\s*:\s*([^|\n]+)", response_text)
        new_child_age = re.search(r"Возраст ребёнка\s*:\s*([^|\n]+)", response_text)
        new_course = re.search(r"Курс\s*:\s*([^|\n]+)", response_text)
        new_phone = re.search(r"Номер телефона\s*:\s*([^|\n]+)", response_text)
        new_parent_name = re.search(r"Имя родителя\s*:\s*([^|\n]+)", response_text)
        new_meeting_type = re.search(r"Тип встречи\s*:\s*([^|\n]+)", response_text)
        match_status = re.search(r'\b\d{8}\b', response_text)

        if not all([new_child_name, new_child_age, new_course, new_phone, new_parent_name, new_meeting_type, match_status]):
            raise ValueError("Missing required data in response text.")


        new_child_name = new_child_name.group(1).strip()
        new_child_age = new_child_age.group(1).strip()
        new_course = new_course.group(1).strip()
        new_phone = new_phone.group(1).strip()
        new_parent_name = new_parent_name.group(1).strip()
        new_meeting_type = new_meeting_type.group(1).strip()
        new_status_id = int(match_status.group(0))


        data = {
            'custom_fields_values': [
                {'field_id': 804272, 'values': [{'value': new_child_name}]},
                {'field_id': 804274, 'values': [{'value': new_child_age}]},
                {'field_id': 1028998, 'values': [{'value': new_course}]},
                {'field_id': 805068, 'values': [{'value': new_phone}]},
                {'field_id': 1029000, 'values': [{'value': new_parent_name}]},
                {'field_id': 1029002, 'values': [{'value': new_meeting_type}]}
            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

        await update_lead_status(lead_id, new_status_id)
    except Exception as e:
        print(f"Error in change_status: ")