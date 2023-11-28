# to check if python code works fine

import openai

def summarize_code(code):
    openai.api_key = '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'  
    prompt = f"Summarize the following code snippet: "+code
    
    response = openai.completions.create(
        model='text-davinci-003',  
        prompt=prompt,
        max_tokens=100, 
        temperature=0.7, 
        n=1,  
        timeout=10,  
    )
    # response = openai.completions.create(
    # model="text-davinci-003",  # Specify the GPT-3.5 model name
    # prompt="Summarize this code:",
    # stream=open("/home/harika/wikidata/Kerala/content.txt", "r")
    # )

    if response and response.choices:
        # return response['choices'][0]['text'].strip()
        return response.choices[0].text.strip()
    
    return response

code = '''
def multiply(a, b):
    return a * b

result = multiply(5, 3)
print(result)
'''

summary = summarize_code(code)
print(summary)
