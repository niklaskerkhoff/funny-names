import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from langchain_openai import ChatOpenAI

app = FastAPI()


@app.get("/api/funny-name", response_class=PlainTextResponse)
def read_greeting():
    return handle_funny_name()


@app.get("/", response_class=HTMLResponse)
def read_index():
    file_path = Path("src/static/index.html")
    if not file_path.exists():
        return HTMLResponse(content="Not Found", status_code=404)

    html_content = file_path.read_text(encoding='utf-8')
    return HTMLResponse(content=html_content)


def handle_funny_name():
    funny_name = get_funny_name()
    updated_used(funny_name)
    return funny_name


def get_funny_name():
    model_name = 'gpt-4o-mini'
    model = ChatOpenAI(model=model_name)

    template_file_path = 'src/static/template.txt'
    used_words_file_path = 'data/used-words.txt'
    used_funny_names_file_path = 'data/used-words.txt'

    with open(template_file_path, 'r') as file:
        template = file.read()

    ensure_file_exists(used_words_file_path)
    with open(used_words_file_path, 'r') as file:
        used_words = file.read()

    ensure_file_exists(used_funny_names_file_path)
    with open(used_funny_names_file_path, 'r') as file:
        used_funny_names = file.read()

    prompt = template + ' ' + used_words

    while True:
        funny_name = model.invoke(prompt).content
        if funny_name not in used_funny_names:
            break

    print('Result by {}: {}', model_name, funny_name)

    return funny_name


def updated_used(funny_name):
    result_words = funny_name.split(' ')
    used = result_words[0] + ', ' + result_words[1] + ', '

    with open('data/used-funny-names.txt', 'a') as file:
        file.write('\n' + funny_name)

    with open('data/used-words.txt', 'a') as file:
        file.write(used)


def ensure_file_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')


if __name__ == "__main__":
    host = os.getenv('HOST', '127.0.0.1')
    uvicorn.run(app, host=host, port=8000)
