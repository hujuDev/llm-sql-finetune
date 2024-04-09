import nltk
import argparse
import subprocess
import os
import threading
import sys
import itertools
import re

try:
    # Check if the 'punkt' tokenizer models are already installed
    nltk.data.find('tokenizers/punkt')
except LookupError:
    # If not found, download the 'punkt' tokenizer models
    nltk.download('punkt')

script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the spinner function
def spinner(stop_event):
    """Displays 'Evaluating' and a spinning indicator for progress."""
    sys.stdout.write('Evaluating ')
    sys.stdout.flush()
    for cursor in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        # Use \r to return the cursor to the start of the line, then write the status message and spinner
        sys.stdout.write(f'\rEvaluating {cursor}')
        sys.stdout.flush()
        stop_event.wait(0.1)
    # Clear the line after finishing
    sys.stdout.write('\r' + ' ' * (len('Evaluating ') + 1) + '\r')
    sys.stdout.flush()

def run_script(script_path, args=[]):
    """Function to run a Python script with arguments using subprocess, displaying output in real-time and saving it to a dynamically named file based on the prediction file name in args."""

    # Extract the prediction file name from args
    pred_file_name = None
    if "--pred" in args:
        pred_index = args.index("--pred") + 1  # Get the index of the value following "--pred"
        if pred_index < len(args):
            pred_file_name = os.path.basename(args[pred_index])

    output_file_name = f"evaluation_{pred_file_name}"
    output_file_path = os.path.join(script_dir, "../evaluation/results", output_file_name)

    # Prepare the spinner
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))

    with open(output_file_path, "w") as output_file:  # Open file for output
        try:
            spinner_thread.start()  # Start the spinner
            # Start the subprocess and direct stdout and stderr to the same pipe
            result = subprocess.run(["python", script_path] + args, check=True, text=True, capture_output=True)
            output_file.write(result.stdout)
            print("\n")
            print_from_header(result.stdout)
            print(f"\nEvaluation results successfully saved in {output_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Script {script_path} failed with error: {e}")
            print(f"Error output: {e.stderr}")
        finally:
            stop_event.set()  # Stop the spinner
            spinner_thread.join()

def print_from_header(output_content):
    # Compile a regex pattern that allows for variable whitespace (spaces and tabs) before and between the words
    pattern = re.compile(r"^\s*(easy)\s+(medium)\s+(hard)\s+(extra)\s+(all)\s*$", re.IGNORECASE)

    # Split the output content into lines for processing
    lines = output_content.splitlines()

    # Find the index of the header line using the regex pattern
    header_index = next((i for i, line in enumerate(lines) if pattern.search(line)), None)

    if header_index is not None:
        # Print from the header line onwards
        for line in lines[header_index:]:
            print(line)

if __name__ == "__main__":

    # Determine the absolute path to the directory containing this script

    # Setup argument parser
    parser = argparse.ArgumentParser(description="Run scripts with given arguments")
    parser.add_argument('--gold', default=os.path.join(script_dir, '../evaluation/gold/dev_gold.txt'), help='Gold standard file')
    parser.add_argument('--pred', default=os.path.join(script_dir, '../evaluation/predictions/predicted_all_default.txt'), help='Predictions file')
    parser.add_argument('--db', default=os.path.join(script_dir, '../data/datasets/spider/database/'), help='Path to database')
    parser.add_argument('--table', default=os.path.join(script_dir, '../data/datasets/spider/tables.json'), help='Path to table JSON')

    args = parser.parse_args()

    script_args = [
        "--gold", args.gold,
        "--pred", args.pred,
        "--etype", 'all',
        "--db", args.db,
        "--table", args.table,
    ]

    script = os.path.join(script_dir, "../repos/test-suite-sql-eval/evaluation.py")

    # Run script with the arguments
    run_script(script, script_args)

