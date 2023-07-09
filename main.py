import os

import openai

openai.api_key = os.environ.get("OPEN_AI_API_TOKEN")


def generate_text(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message


def run_code_frm_AI(AI_message, retry_times=0):
    if input(AI_message + "\n" + "input \"Y\" to allow\n") == "Y":
        try:
            exec(AI_message)
        except Exception as e:
            if retry_times > 0:
                send_error_and_retry(e)

                if type(retry_times) is int:
                    retry_times -= 1


def send_error_and_retry(error_message):
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=str(error_message),
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
        # function_parameters=functions
    )

    run_code_frm_AI(completions.choices[0].text)


functions = {
    "name": "run_python_code",
    "description": "runs python code with exec function",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Uses exec() to run python code",
            },
        },
        "required": ["code"],
    },
    "return_type": {"type": "null"},
}

model_engine = 'text-davinci-002'
prompt = input("Prompt: \n")
completions = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
    # function_parameters=functions
)

message = completions.choices[0].text
run_code_frm_AI(message, retry_times=2)
