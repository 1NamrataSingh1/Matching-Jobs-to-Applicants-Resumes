# Comparing Resume-to-Job Matching Methods

A comparative evaluation of three NLP-based approaches for matching unstructured resume text to standardized O\*NET occupations.

**Author:** Namrata Singh — Penn State University  
**Parent Paper:** [A Novel Approach for Job Matching and Skill Recommendation Using Transformers and the O\*NET Database](https://doi.org/10.1016/j.bdr.2025.100509) (Alonso et al., 2025)

---

## What This Project Does

This project takes resume text as input and predicts which O\*NET occupation it best matches. It runs **three different methods** on the same task and compares their accuracy, semantic understanding, and speed:

| Method | Type | What It Does |
|--------|------|--------------|
| **Cosine Similarity** | Rule-based baseline | Compares resume text directly against job title names |
| **TF-IDF + Logistic Regression** | Traditional ML | Classifies resumes using bag-of-words features |
| **Transformer Semantic Matching** | Deep learning | Compares resume text against 7 O\*NET entity types using sentence-transformers (parent paper method) |

### Results Summary

| Method | Top-1 Exact | Top-5 Exact | Top-1 Family | Top-5 Family | Latency |
|--------|-------------|-------------|--------------|--------------|---------|
| Cosine Similarity | **19.0%** | **39.0%** | 40.0% | 70.5% | 4.2s |
| TF-IDF + Log. Reg. | 8.6% | 20.0% | 34.3% | 71.4% | **0.014s** |
| Transformer + O\*NET | 7.6% | 26.7% | **63.8%** | **81.0%** | 49.3s |

*105 resumes across 21 categories, evaluated against 1,016 O\*NET occupations.*

---

## Prerequisites

- **Python 3.9+** (tested on 3.11.7)
- **MySQL 8.0+** installed and running
- **~2 GB disk space** for the O\*NET database and embedding files
- **macOS, Linux, or WSL** (not tested on native Windows)

---

## Setup

### 1. Create a virtual environment

```bash
cd using-transformers-and-o-net-to-match-jobs-to-applicants-resumes-main
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install torch torchvision torchaudio
pip install sentence-transformers
pip install textblob
pip install mysql-connector-python
pip install scikit-learn
pip install matplotlib numpy
python -m textblob.download_corpora
```

### 3. Download and import the O\*NET database

1. Go to [https://www.onetcenter.org/database.html#all-files](https://www.onetcenter.org/database.html#all-files)
2. Download the **MySQL** version of the database
3. Import it into MySQL:

```bash
mysql -u root -p -e "CREATE DATABASE db_26_1;"
mysql -u root -p db_26_1 < /path/to/onet_database.sql
```

4. Create the application user:

```bash
mysql -u root -p -e "CREATE USER 'jobmatch'@'localhost' IDENTIFIED BY 'jobmatch123';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON db_26_1.* TO 'jobmatch'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"
```

> **Note:** If your MySQL credentials differ, edit `ob2/skills_query.py` line 8 to match your setup.

### 4. Verify database connection

```bash
cd ob2
python -c "from skills_query import QueryMysql; q = QueryMysql(); print(f'Connected: {len(q.get_job_codes())} jobs')"
```

You should see: `Connected: 1016 jobs`

---

## Running the Project

### Option A: Run everything at once

```bash
python ob2/run_project.py
```

This will automatically:
1. Generate embedding files (if missing)
2. Prepare test data with ground truth labels
3. Train the TF-IDF model
4. Evaluate all 3 methods
5. Generate visualizations

### Option B: Run each step manually

```bash
cd ob2

# Step 1: Generate embeddings (~5-10 minutes first time)
python generate_embeddings.py

# Step 2: Prepare labeled test data
python prepare_test_data.py

# Step 3: Train TF-IDF model
python tfidf_baseline.py

# Step 4: Run evaluation on all methods
python evaluate.py

# Step 5 (optional): Generate charts
python visualize_results.py
```

### Quick test (5 resumes only)

```bash
python ob2/evaluate.py --fast
```

---

## Project Structure

```
├── ob2/                           # Main project code
│   ├── cv_analyzer.py             # Transformer semantic matching (parent paper method)
│   ├── skills_query.py            # MySQL/O*NET database interface
│   ├── baseline_wrappers.py       # Cosine similarity baseline
│   ├── tfidf_baseline.py          # TF-IDF + logistic regression baseline
│   ├── evaluate.py                # Evaluation framework (runs all 3 methods)
│   ├── prepare_test_data.py       # Creates labeled test data from resumes
│   ├── generate_embeddings.py     # Generates sentence-transformer embedding files
│   ├── run_project.py             # Master pipeline script
│   ├── visualize_results.py       # Generates comparison charts
│   ├── five_unique_resumes.json   # Source resume data (5 per category, 21 categories)
│   ├── test_data_with_labels.json # Labeled test set (generated)
│   ├── train_data.json            # TF-IDF training data (generated)
│   ├── tfidf_model.pkl            # Trained TF-IDF model (generated)
│   ├── evaluation_results.json    # Full evaluation results (generated)
│   ├── skill_embeddings.pt        # Tech skills embeddings by job (generated)
│   ├── titles_embeddings.pt       # All job title embeddings (generated)
│   ├── task_embeddings.pt         # Task embeddings by job (generated)
│   └── tools_embeddings.pt        # Tools embeddings by job (generated)
├── splits/                        # Train/test/validation splits
│   ├── train.csv
│   ├── test.csv
│   ├── val_unseen.csv
│   └── split_metadata.json
├── export_splits.py               # Script that created the splits
└── README.md
```

---

## How Each Method Works

### Method 1: Cosine Similarity Baseline

Encodes all 1,016 O\*NET job titles and the resume text using `all-mpnet-base-v2`, then returns the jobs with the highest cosine similarity. No O\*NET entity scoring involved — purely surface-level textual resemblance.

### Method 2: TF-IDF + Logistic Regression

Represents resumes as TF-IDF feature vectors (unigrams + bigrams, 5,000 features) and trains a logistic regression classifier to predict the O\*NET occupation code. Outputs class probabilities, enabling ranked top-k predictions.

### Method 3: Transformer Semantic Matching

Reproduces the parent paper's approach:
1. Parses resume text into nouns, noun phrases, and sentences using TextBlob
2. Encodes text with `all-mpnet-base-v2` sentence-transformer
3. Computes cosine similarity against O\*NET entities for each of the 1,016 jobs across 7 categories (skills, knowledge, abilities, work activities, tasks, tools, technology skills)
4. If similarity exceeds threshold (0.65), adds the entity's importance score to the job's total
5. Returns top 5 jobs ranked by aggregated score

---

## Evaluation Metrics

- **Top-1 Exact:** correct O\*NET code is the #1 prediction
- **Top-5 Exact:** correct O\*NET code appears in the top 5
- **Top-1 Family:** #1 prediction shares the same 2-digit SOC group (e.g., all `15-xxxx` = computer occupations)
- **Top-5 Family:** correct SOC family appears in the top 5
- **Latency:** average time per resume prediction

Family-level metrics matter because O\*NET has 1,016 highly specific occupations — predicting "Software Developers" when the answer is "Computer Programmers" is a miss on exact match but correct at the family level.

---

## Troubleshooting

**"No test data source found"**  
Make sure `five_unique_resumes.json` exists in `ob2/`. The scripts auto-detect the `ob2/` directory, but if you're running from an unexpected location, `cd ob2` first.

**MySQL connection refused**  
Make sure MySQL is running (`mysql.server start` on macOS or `sudo systemctl start mysql` on Linux) and the `jobmatch` user exists with access to `db_26_1`.

**"LogisticRegression got an unexpected keyword argument 'multi_class'"**  
Your scikit-learn version is 1.7+. The `tfidf_baseline.py` in this repo already has this fixed.

**Embedding generation is slow**  
First run of `generate_embeddings.py` takes 5-10 minutes because it encodes skills/tasks/tools for all 1,016 jobs. Subsequent runs skip this step since the `.pt` files already exist.

---

## References

1. R. Alonso, D. Dessí, A. Meloni, and D. Reforgiato Recupero, "A novel approach for job matching and skill recommendation using transformers and the O\*NET database," *Big Data Research*, vol. 39, 2025.
2. A. Akkasi, "Job description parsing with explainable transformer based ensemble models to extract the technical and non-technical skills," *Natural Language Processing Journal*, vol. 9, 2024.
3. J. Rosenberger et al., "CareerBERT: Matching resumes to ESCO jobs in a shared embedding space for generic job recommendations," *Expert Systems With Applications*, vol. 275, 2025.
4. G. Tzimas et al., "From data to insight: Transforming online job postings into labor-market intelligence," *Information*, vol. 15, no. 8, 2024.
5. M. Zhang et al., "SKILLSPAN: Hard and soft skill extraction from English job postings," in *Proc. NAACL-HLT*, 2022.

---

## License

The O\*NET database is available under a [Creative Commons license](https://www.onetcenter.org/license_db.html). The original starter code is from the [HRI Lab, University of Cagliari](https://gitlab.com/hri_lab1/using-transformers-and-o-net-to-match-jobs-to-applicants-resumes).
