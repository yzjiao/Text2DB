# Text2DB

Official repository for the paper [**TEXT2DB: Integration-Aware Information Extraction with Large Language Model Agents**](https://aclanthology.org/2024.findings-acl.12.pdf) by Yizhu Jiao, Sha Li, Sizhe Zhou, Heng Ji, and Jiawei Han (ACL 2024 Findings).

This repository implements an automated system for database population that extracts structured information from text documents according to user instructions and populates databases accordingly.

## 🌟 Dataset

The dataset consists of database population tasks across three categories:
- **Data Infilling (di)**: Filling missing values in existing database rows
- **Row Population (rp)**: Adding new rows to database tables
- **Column Addition (ca)**: Adding new columns with values to existing tables

### Dataset Structure

The dataset folder contains multiple samples, each in a separate directory named `{source}_{id}_{task_type}`:
- `bird_39_rp`, `bird_40_di`, `wiki_0_di`, etc.
- **Source**: `bird` (from BIRD dataset) or `wiki` (from Wikipedia)
- **Task type**: `di` (data infilling), `rp` (row population), `ca` (column addition)

Each sample directory contains:
- **`data.json`**: Task metadata including instruction, source text, domain, and difficulty
- **`input.sqlite`**: Initial database state before population
- **`output.sqlite`**: Ground truth database after population (used for evaluation)

### Dataset Example

**Folder:** `wiki_0_di/`

**`data.json`:**
```json
{
  "instruction": "I am maintaining a database of the largest earthquakes by year. Given the latest document of the peru earthquake, please update the numbers of deaths and injuries in this disaster.",
  "db_name": "earthquake",
  "task_type": "data imputation",
  "source": "https://en.wikipedia.org/wiki/2019_Peru_earthquake",
  "text": "An earthquake measuring Mw 8.0 struck Peru...",
  "domain": "events",
  "difficulty": "medium",
  "db_source": "wiki"
}
```

**`input.sqlite`:** Contains the earthquake database with missing death/injury counts

**`output.sqlite`:** Contains the completed database with updated values extracted from the text


## 🚀 Setup and Running

### Prerequisites
- Python 3.7+
- OpenAI API key (for GPT-4/GPT-3.5)
- One CUDA-compatible GPU (for GENRE entity linking)

### Installation
1. 
   ```bash
   git clone https://github.com/yzjiao/Text2DB.git
   cd Text2DB
   ```

2. **Download the dataset:**
   - Download the dataset folder from [Google Drive](https://drive.google.com/drive/folders/13f3dkqTffrYI_ro4DpgE6Jk0-QYqjGMP?usp=sharing)
   - Place the `dataset` folder under the Text2DB directory
   - The Google Drive also contains pre-computed model outputs for reference

3. **Setup the GENRE entity linking tool:**
   ```bash
   git clone https://github.com/facebookresearch/GENRE.git
   cd GENRE
   # Follow GENRE installation instructions
   pip install python>=3.7
   pip install pytorch>=1.6
   pip install fairseq>=0.10
   pip install transformers>=4.2 

   
   # Download the required pre-trained model
   mkdir models
   cd models
   wget http://dl.fbaipublicfiles.com/GENRE/fairseq_e2e_entity_linking_aidayago.tar.gz
   tar -zxvf fairseq_e2e_entity_linking_aidayago.tar.gz
   cd ../..
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Running the Model

To run the model and evaluation:

```bash
python main.py --data_root ./dataset \
               --output_root ./output \
               --gpt_version gpt-4 \
```

**Arguments:**
- `--data_root`: Path to the dataset folder (default: `./dataset`)
- `--output_root`: Path to save model outputs (default: `./output`)
- `--gpt_version`: GPT model version to use (default: `gpt-4`)

The model outputs will be saved under `./output/` with the following structure:
```
./output/
  ├── {sample_name}/
  │   ├── output.sqlite  # Populated database
  │   └── codes.json     # Generated code versions
```


## 📊 Evaluation

The evaluation compares the model's output database with the ground truth database using Macro-averaged F1. The evaluation is included in the main python file.



## 📚 Citation

If you find this repository helpful, please cite our paper:

```bibtex
@inproceedings{jiao-etal-2024-text2db,
    title = "{T}ext2{DB}: Integration-Aware Information Extraction with Large Language Model Agents",
    author = "Jiao, Yizhu  and
      Li, Sha  and
      Zhou, Sizhe  and
      Ji, Heng  and
      Han, Jiawei",
    editor = "Ku, Lun-Wei  and
      Martins, Andre  and
      Srikumar, Vivek",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2024",
    month = aug,
    year = "2024",
    address = "Bangkok, Thailand",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-acl.12/",
    doi = "10.18653/v1/2024.findings-acl.12",
    pages = "185--205",
}
```

