import ollama

ollama.pull('llama3.2:1b-instruct-q4_K_M')
response = ollama.chat(model='llama3.2:1b-instruct-q4_K_M', messages=[
  {
    'role': 'user',
    'content': 'in 100 words, who was Aaron Swartz?',
  },
])
print(response)
