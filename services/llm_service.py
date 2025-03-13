import json
from icecream import ic
from openai import AsyncOpenAI
from config.config import Config
from pathlib import Path
from services.promt import promt
from utils.JsonDataBase import JSONDatabase


from langsmith.wrappers import wrap_openai
from langsmith import traceable


BASE_DIR = Path(__file__).resolve().parent.parent
talk_id_json = f"{BASE_DIR}/config/thread_id.json"

tools = [
    {
        "type": "file_search",
        "file_search": {
            "max_num_results": 3,
            "ranking_options": {
                "score_threshold": 0.6
            }
        }
    },
    {

        "type": "function",
        "function": {
            "name": "demo_lesson_info",
            "description": "Используй когда рекомендуешь курс",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]


def handle_tool_call(tool_name, tool_args):
    if tool_name == "demo_lesson_info":
        BASE_DIR = Path(__file__).resolve().parent.parent  # Поднимаемся на уровень выше
        timetable_path = BASE_DIR / "utils/timetable.txt"

        with open(timetable_path, "r", encoding="UTF-8") as file:
            return file.read()



db = JSONDatabase(talk_id_json)

@traceable
async def thread(message_text: str, chat_id: str) -> list[str | dict]:
    try:
            client = wrap_openai(AsyncOpenAI(api_key=Config.OPENAI_API_KEY, default_headers={"OpenAI-Beta": "assistants=v2"}))

            thread_id = await db.get(chat_id) if await db.exists(chat_id) else None
            if not thread_id:
                thread = await client.beta.threads.create()
                thread_id = thread.id
                await db.add(chat_id, thread_id)

            await client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_text
            )

            run = await client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                model="gpt-4o",
                assistant_id=Config.ASSIST_ID,
                temperature=0.1,
                instructions=promt,
                tools = tools
            )

            if run.status == 'requires_action' and hasattr(run, 'required_action'):
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    ic(tool_name, tool_args)

                    result = handle_tool_call(tool_name, tool_args)
                    print(result)

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })

                run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            if run.status == "completed":
                messages = await client.beta.threads.messages.list(thread_id=thread_id)
                messages_json = json.loads(messages.model_dump_json())
                response = messages_json["data"][0]["content"][0]["text"]["value"]
                return [response, messages_json]

            return ["Model run not completed"]


    except Exception as e:

        return [str(e), {}]