import argparse
import json
from llmtuner import ChatModel
from tqdm import tqdm
import os

# Determine the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
checkpoint_root_dir = os.path.join(script_dir, "../checkpoints")
evaluation_dir = os.path.join(script_dir, "../evaluation")
data_input_dir = os.path.join(script_dir, "../data/datasets_json")

# Setup argument parser
parser = argparse.ArgumentParser(description="Generate responses for a JSON input file using ChatModel")
parser.add_argument("--model_name_or_path", type=str, default="codellama/CodeLlama-7b-hf", help="Path or name of the model")
parser.add_argument("--checkpoint_name", type=str, default="default", help="Name of the adapter")
parser.add_argument("--input_file_name", type=str, default="spider_dev.json", help="Name to the input JSON file")
parser.add_argument("--num_entries", type=int, default=5, help="Optional: Number of entries to process (if None, all entries will be processed)")
args = parser.parse_args()

checkpoint_dir = os.path.join(checkpoint_root_dir, args.checkpoint_name)
data_input_file = os.path.join(data_input_dir, args.input_file_name)

# Initialize ChatModel with command-line arguments
chat_model = ChatModel(dict(
    model_name_or_path=args.model_name_or_path,
    adapter_name_or_path=checkpoint_dir,
    finetuning_type="lora",
    template="default",
))

# Load the JSON input file
with open(data_input_file, "r") as file:
    test_dataset = json.load(file)

# If --num_entries is provided, limit the dataset to that number of entries
if args.num_entries is not None and args.num_entries < len(test_dataset):
    test_dataset = test_dataset[:args.num_entries]
else:
    args.num_entries = "all"

# Initialize a list to collect the outputs
outputs = []

# Process each entry in the test dataset
for entry in tqdm(test_dataset, desc="Generating predictions"):
    input = entry["Input"]
    # Generate response for the question
    messages = [{"role": "user", "content": input}]
    response = ""
    for new_text in chat_model.stream_chat(messages):
        response += new_text
    # Append the response to outputs
    outputs.append(response)

predicted_file_path = os.path.join(evaluation_dir, "predictions", "predicted_" + str(args.num_entries) + "_" + args.checkpoint_name + ".txt")

# Write the outputs to predicted.txt
with open(predicted_file_path, "w") as file:
    for output in outputs:
        file.write(output + "\n")
