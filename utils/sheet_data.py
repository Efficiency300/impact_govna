from pathlib import Path
import gspread
from icecream import ic

# Базовая конфигурация
BASE_DIR = Path(__file__).resolve().parent
SERVICE_ACCOUNT_PATH = BASE_DIR / "Service_Account.json"
SHEET_NAME = "Impact"
WORKSHEET_NAME = "Лист1"

DAYS_OF_WEEK = {
    "Понедельник": "Monday",
    "Вторник": "Tuesday",
    "Среда": "Wednesday",
    "Четверг": "Thursday",
    "Пятница": "Friday",
    "Суббота": "Saturday",
    "Воскресенье": "Sunday",
}


def get_google_sheet():
    try:
        ic(f"Попытка аутентификации с файлом: {SERVICE_ACCOUNT_PATH}")
        gc = gspread.service_account(filename=str(SERVICE_ACCOUNT_PATH))
        sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        ic("Подключение к таблице успешно")
        return sheet.get_all_values()
    except Exception as e:
        ic(f"Ошибка подключения: {e}")
        exit(1)


def get_weekday(row):
    for rus_day, eng_day in DAYS_OF_WEEK.items():
        if rus_day in row:
            return eng_day
    return None


def parse_courses(courses_text):
    courses = []
    course_lines = [line.strip() for line in courses_text.split('\n') if line.strip()]
    for line in course_lines:
        line = line.lstrip('-').strip()
        if not line:
            continue
        elif '(' in line and ')' in line:
            name = line.split('(')[0].strip()
            dates = line[line.find('(') + 1:line.find(')')].strip()
            courses.append({"name": name, "dates": dates})
        else:
            courses.append({"name": line, "dates": ""})
    return courses


def try_convert_to_int(value):
    if value is None:
        return None
    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return value


def parse_cell_data(cell_value, day):
    if not cell_value.strip():
        return None

    lines = [line.strip() for line in cell_value.split('\n') if line.strip()]
    result = {
        "day": day,
        "courses": [],
        "section": None,
        "working_hours": None,
        "age_group": None,
        "group_code": None,
        "start_date": None,
        "teacher": None,
        "room": None,
        "students": 0,
    }

    current_section = None
    courses_block = []

    try:
        for line in lines:
            if line.lower().startswith("section:"):
                result["section"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("working_hours:") or line.lower().startswith("working hours:"):
                result["working_hours"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("age_group:") or line.lower().startswith("age group:"):
                result["age_group"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("group_code:") or line.lower().startswith("group code:"):
                result["group_code"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("courses:"):
                current_section = "courses"
            elif line.lower().startswith("start_date:") or line.lower().startswith("start date:"):
                result["start_date"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("teacher:"):
                result["teacher"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("room:"):
                result["room"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("students:"):
                students_value = line.split(":", 1)[1].strip()
                result["students"] = try_convert_to_int(students_value)
            elif current_section == "courses" and line:
                courses_block.append(line)

        if courses_block:
            result["courses"] = parse_courses("\n".join(courses_block))

        return result if all(
            result[field] for field in ["section", "working_hours", "age_group", "group_code"]) else None
    except Exception as e:
        ic(f"Ошибка парсинга ячейки: {e}, данные: {lines}")
        return None


def fetch_timetable_data(data):
    timetable = []
    current_day = None
    for row_idx, row in enumerate(data):
        day = get_weekday(row)
        if day:
            current_day = day
        if row_idx == 0:
            continue
        for cell in row[1:]:
            parsed_data = parse_cell_data(cell, current_day)
            if parsed_data:
                timetable.append(parsed_data)
    return timetable


def save_to_text_file(data, filename="timetable.txt"):
    output_path = BASE_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(f'    "День": "{entry["day"]}",\n')
            f.write(f'    "Название курса": "{entry["section"]}",\n')
            f.write(f'    "Время учебы": "{entry["working_hours"]}",\n')
            f.write(f'    "Количество учеников в группе": {entry["students"]}\n')
            f.write("\n" + "-" * 50 + "\n\n")
    ic(f"Данные сохранены в {output_path}")


def main():
    data = get_google_sheet()
    result = fetch_timetable_data(data)
    if result:
        save_to_text_file(result)
    else:
        ic("Не удалось извлечь данные")

if __name__ == "__main__":
    main()


