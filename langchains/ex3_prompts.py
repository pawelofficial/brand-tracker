import json 
import openai
openai.api_key=dict(json.load(open('./secrets.json')))['openai']

def ask(s):
    my_prompts = ["Provide answer with minimum words possible for a question.","answer in Polish language"]
    m=[{"role": "system", "content": prompt} for prompt in my_prompts]
    
    MODEL = "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            *m,
            {"role": "user", "content": f"{s}"},
        ],
        temperature=0,
    )
    r=response['choices'][0]['message']['content']
    print(r)
    return r 


ask('My fathers name is John')

ask('what is my fathers name? ')
