import openai
import time, os

HOST = '127.0.0.1'
PORT = 8000

PROTOCOL = 'http'
BASE_URL = f"{PROTOCOL}://{HOST}:{PORT}/v1/"

client = openai.OpenAI(
    api_key='EMPTY',
    base_url=BASE_URL,
)

MODEL = 'cognitivecomputations/Qwen3-30B-A3B-AWQ'

promt = '''напиши короткий пост про космос'''

if __name__ == '__main__':
    timer = time.time()

    print("Задавай вопрос:")

    chat_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": input()}
        ],
        temperature=0,
    )
    print(chat_response)
    print('=' * 120)
    print(chat_response.choices[0].message.content)

    