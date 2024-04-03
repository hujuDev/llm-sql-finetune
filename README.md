# Finetuning LLM for Text2SQL with llmtuner and Spider Dataset

## Overview

This project focuses on finetuning a large language model (LLM) for Text2SQL tasks, utilizing the versatile `llmtuner` package and the comprehensive Spider dataset. Specifically, we finetune the CodeLlama-7b model using LoRA to enhance its capabilities for generating SQL queries from natural language descriptions. The project includes scripts for data preparation, model finetuning, inference, and prediction generation in the format required by the Spider evaluation metrics.

## Getting Started

### Prerequisites

- Python 3.8+
- Conda (or micromamba) for environment management
- Access to a GPU with at least 40GB VRAM (finetuning tasks)

### Installation

1. Clone this repository to your local machine.
2. Create a virtual environment and activate it using conda (or micromamba)
   ```bash
   conda create -n llm-sql-finetune
   conda activate llm-sql-finetune
   ```
3. Navigate to the project directory and install the required dependencies:
   ```bash
   cd llm-sql-finetune
   pip install -r requirements.txt
   ```
4. Download the Spider dataset and the CodeLlama-7b model from Hugging Face:
   - Spider dataset: `hujudev/spider-text-2-sql-train`
   - Model: `codellama/CodeLlama-7b-hf`
5. (Optional) Download the pre-trained checkpoints if available.

### Configuration

Configurations for the dataset and finetuning process are specified in JSON files:
- Dataset configuration: `data/dataset_info.json`
- Finetuning configuration: `scripts/configs.json`

Example configurations are provided within these files. You can modify these configurations according to the `llmtuner` specifications to suit your specific needs.

### Usage

#### llama_lora_finetune.py

Use this script for finetuning the LLM model with the LoRA method. You can start the finetuning process by running:

```bash
python scripts/llama_lora_finetune.py
```

#### llama_lora_inference.py

This script is responsible for performing inference using the finetuned LLM model. Execute the script with the following command:

```bash
python scripts/llama_lora_inference.py
```

#### llama_lora_prediction_generator.py

To generate predictions in the format required for the Spider evaluation, use this script:

```bash
python scripts/llama_lora_prediction_generator.py
```

#### spider_training_input_generator.py

For preparing the input data from the Spider dataset for training, run this script:

```bash
python scripts/spider_training_input_generator.py
```

Make sure you have followed all the setup instructions and activated the correct Python environment before executing these scripts.

## License

This project is licensed under the TODO License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spider Dataset](https://yale-lily.github.io/spider)
- [CodeLlama-7b-hf Model](https://huggingface.co/codellama/CodeLlama-7b-hf)
- [llmtuner/LLaMA-Factory GitHub Repo](https://github.com/hiyouga/LLaMA-Factory)

For more details on the `llmtuner` package and the Spider dataset, please refer to their official documentation and repositories.