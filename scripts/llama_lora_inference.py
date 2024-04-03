import argparse
from llmtuner import ChatModel
import os

# Determine the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
checkpoint_root_dir = os.path.join(script_dir, "../checkpoints")

# Setup argument parser
parser = argparse.ArgumentParser(description="Run Chat Model with specified model and adapter")
parser.add_argument("--model_name_or_path", type=str, default="codellama/CodeLlama-7b-hf", help="Path or name of the model")
parser.add_argument("--checkpoint_name", type=str, default="default", help="Path or name of the adapter")
args = parser.parse_args()

checkpoint_dir = os.path.join(checkpoint_root_dir, args.checkpoint_name)

# Initialize ChatModel with command-line arguments
chat_model = ChatModel(dict(
    model_name_or_path=args.model_name_or_path,
    adapter_name_or_path=checkpoint_dir,
    finetuning_type="lora",
    template="default",
))

messages = []

while True:
    query = input("\nUser: ")
    if query.strip().lower() == "exit":
        break
    if query.strip().lower() == "clear":
        messages = []
        continue

    messages.append({"role": "user", "content": query})
    print("Assistant: ", end="", flush=True)
    response = ""
    for new_text in chat_model.stream_chat(messages):
        print(new_text, end="", flush=True)
        response += new_text
    print()
    messages.append({"role": "assistant", "content": response})
