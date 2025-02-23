import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
from huggingface_hub import login
import os

load_dotenv()

login(token=os.getenv("HUG_TOKEN"))

checkpoint = "HuggingFaceTB/SmolLM-135M"
device = "cpu" # for GPU usage or "cpu" for CPU usage
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
# for multiple GPUs install accelerate and do `model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")`
model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.bfloat16).to(device)
inputs = tokenizer.encode("def print_hello_world():", return_tensors="pt",).to(device)

outputs = model.generate(inputs,
                         attention_mask=torch.ones_like(inputs),
                         pad_token_id=tokenizer.pad_token_type_id)

print(tokenizer.decode(outputs[0]))


login(token=os.getenv("HUG_TOKEN"))

# model_id = "meta-llama/Llama-3.2-1B-Instruct"
# pipe = pipeline(
#     "text-generation",
#     model=model_id,
#     torch_dtype=torch.bfloat16,
#     device_map="auto",
# )
# messages = [
#     {"role": "system", "content": "You are a sentence extractor. Given a text in Markdown format, you return a Python list of all the sentences in the text."},
#     {"role": "user", "content": posts[0][2]},
# ]
# outputs = pipe(
#     messages,
#     max_new_tokens=256,
# )
# print(outputs[0]["generated_text"][-1])
