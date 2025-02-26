import torch
from transformers import pipeline, AutoModelForCausalLM, BitsAndBytesConfig
from dotenv import load_dotenv
from huggingface_hub import login
import os

load_dotenv()

login(token=os.getenv("HUG_TOKEN"))

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    llm_int8_threshold=6.0  # Optional: adjust the outlier threshold if needed.
)

# Use the QLoRA quantized model from Hugging Face Hub:
model_id = "meta-llama/Llama-3.2-1B-Instruct"

model = AutoModelForCausalLM.from_pretrained(model_id,
                                             quantization_config=quant_config,
                                             device_map="auto",
                                             torch_dtype=torch.bfloat16)

# Set up the text-generation pipeline.
# Using bfloat16 (or float16 if bfloat16 isn’t supported) and auto device mapping.
generator = pipeline(
    "text-generation",
    model=model
)

# Define a conversational prompt.
prompt = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Can you explain how QLoRA works?"}
]

# Generate a response.
output = generator(prompt, max_new_tokens=100)
print(output[0]["generated_text"])

