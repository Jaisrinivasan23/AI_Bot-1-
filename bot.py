from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)


openai.api_key = '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'



def get_api_res(prompt: str) -> str|None:
    text: str | None = None

    try:
        response: dict = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=[
                {"role": "system", "content": "You are a online home made natural remedies product company"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        choices: dict = response.get('choices')[0]
        text = choices.get('message', {}).get('content')

    except Exception as e:
        print("Error:", e)

    return text

def update_list(message:str, prompt_list: list[str]):
    prompt_list.append(message)

def create_prompt(message:str, prompt_list: list[str]) -> str:
    p_message = f'\nHuman:{message}'
    update_list(p_message, prompt_list)
    prompt = ''.join(prompt_list)
    return prompt

def get_bot_res(message:str, prompt_list: list[str]) -> str:
    prompt = create_prompt(message, prompt_list)
    bot_res = get_api_res(prompt)

    if bot_res:
        update_list(bot_res, prompt_list)
        pos = bot_res.find('\nbot: ')
        bot_res = bot_res[pos + 5:]
    else:
        bot_res = 'Something went wrong'
    return bot_res

def read_prompts_responses_from_file(filename: str) -> dict:
    prompts_responses = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            current_user_query = None
            for line in lines:
                line = line.strip()
                if line:
                    if line.startswith("User Query:"):
                        current_user_query = line[len("User Query:"):].strip()
                    elif line.startswith("Bot Response:"):
                        if current_user_query:
                            prompts_responses[current_user_query] = line[len("Bot Response:"):].strip()
                        current_user_query = None
        return prompts_responses
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_bot_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    response = get_bot_res(user_input, list(prompts_responses.keys()))
    return jsonify({'bot_response': response})

if __name__ == "__main__":
    filename = "AI_Bot\Desc.txt"
    prompts_responses = read_prompts_responses_from_file(filename)
    if not prompts_responses:
        print("Error: No prompts and responses found.")
    else:
        app.run(debug=True)
