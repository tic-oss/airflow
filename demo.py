import openai
import time
def summarize_code(file_path):
    openai.api_key = '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'
    with open(file_path, 'r') as file:
        code = file.read()
    if len(code.split()) > 4097:
        code = ' '.join(code.split()[:4097])
    prompt = f"what is the topic of the text: {code}"
    try:
        response = openai.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=2000,  # Further reduced max_tokens value
            temperature=0.7,
            n=1,
            timeout=10,
        )
        if response and response.choices:
            return response.choices[0].text.strip()
    except openai.RateLimitError as e:
        print(f"Rate limit exceeded. Waiting for {e.retry_after} seconds.")
        time.sleep(e.retry_after)
        return summarize_code(file_path)
    return "Error: Unable to generate a summary."
file_path = '/home/harika/wikidata/content.txt'
summary = summarize_code(file_path)
print(summary)