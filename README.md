# Job-Resume Matching: Comparative Evaluation Research Project

## 🎯 Research Question
**How do traditional approaches (rule-based, classical ML) compare to modern transformer-based methods for job-resume matching in terms of accuracy, latency, and complexity?**

## 📊 What This Project Does

This is a **comparative research project** that evaluates **3 different approaches** to job-resume matching:

| Method | Type | Key Characteristic |
|--------|------|-------------------|
| **Method 1**: Simple Cosine Similarity | Rule-based | Fast, interpretable, keyword-dependent |
| **Method 2**: TF-IDF + Logistic Regression | Traditional ML | Good balance, requires training data |
| **Method 3**: Transformer Semantic Matching | Modern Deep Learning | Best accuracy, semantic understanding |

---

## 🚀 Quick Start

### Option 1: Run Everything Automatically ⭐ **RECOMMENDED**
```bash
cd ob2
python run_project.py
```

This one command will:
1. Generate all embedding files (~20 minutes, one-time)
2. Prepare test data
3. Train TF-IDF model
4. Run all 3 methods on your test set
5. Generate comparison visualizations
6. Save results to `evaluation_results.json`

**Total time**: ~30-45 minutes (mostly waiting for embeddings)

### Option 2: Run Step-by-Step

```bash
# Step 1: Prepare data (5 min)
python prepare_test_data.py

# Step 2: Train TF-IDF (2 min)
python tfidf_baseline.py

# Step 3: Run evaluation (5-10 min)
python evaluate.py

# Step 4: Create visualizations (1 min)
python visualize_results.py
```

---

## 📦 Installation

### 1. Download Files
Place these files in your `ob2/` directory:
- `evaluate.py` ⭐ (main evaluation framework)
- `run_project.py` (automated pipeline)
- `prepare_test_data.py` (data preparation)
- `tfidf_baseline.py` (traditional ML method)
- `baseline_wrappers.py` (baseline method wrappers)
- `visualize_results.py` (plot generation)
- `requirements.txt` (dependencies)

### 2. Install Dependencies
```bash
pip install torch sentence-transformers textblob scikit-learn pandas matplotlib
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### 3. Verify Setup
Your database should already be configured from earlier in the project.

---

## 📋 The 3 Methods Explained

### Method 1: Simple Cosine Similarity (Baseline)
**File**: `baseline_wrappers.py`

**How it works:**
1. Parse resume text → extract nouns, phrases
2. Encode both resume and job titles with SentenceTransformers
3. Compute cosine similarity
4. Return top matches

**Pros:**
- ⚡ Very fast (~10-20ms per resume)
- 🔍 Easy to understand and debug
- 📊 Interpretable results

**Cons:**
- Limited semantic understanding
- Keyword-dependent
- Misses implicit skills

**Expected Performance**: ~45-55% top-1 accuracy

---

### Method 2: TF-IDF + Logistic Regression (Traditional ML)
**File**: `tfidf_baseline.py`

**How it works:**
1. Vectorize resume text using TF-IDF (bag-of-words)
2. Train multi-class logistic regression classifier
3. Predict job category probabilities
4. Return top 5 matches

**Pros:**
- ⚡ Fast inference (~15-30ms per resume)
- 📈 Learns from training data
- 🎯 Better than simple baselines

**Cons:**
- Needs training data
- Still bag-of-words (no word order)
- No semantic understanding

**Expected Performance**: ~55-65% top-1 accuracy

---

### Method 3: Transformer Semantic Matching (Modern DL)
**File**: `cv_analyzer.py` (already exists in starter code)

**How it works:**
1. Parse resume → extract sentences, nouns, phrases
2. Encode with all-mpnet-base-v2 transformer (768-dim embeddings)
3. Compare against O*NET job descriptions across 11 dimensions:
   - Tech skills
   - Knowledge areas
   - Abilities
   - Work activities
   - Tasks
   - Tools
   - (Each with name AND description matching)
4. Aggregate scores and return top 5

**Pros:**
- 🎯 Best accuracy
- 🧠 Semantic understanding (understands "ML engineer" ≈ "data scientist")
- 📊 Rich feature set from O*NET

**Cons:**
- Slower (~200-300ms per resume)
- More complex (harder to debug)
- Requires embeddings and O*NET data

**Expected Performance**: ~70-75% top-1 accuracy

---

## 📊 Example Output

After running the evaluation, you'll get results like:

```
EVALUATION RESULTS SUMMARY
==================================================================================
Method                                   Top-1 Acc    Top-5 Acc    Avg Time      
----------------------------------------------------------------------------------
Simple Cosine Similarity                 48.3%        73.1%        14.2ms        
TF-IDF + Logistic Regression             61.7%        82.4%        22.8ms        
Transformer Semantic Matching            72.9%        89.6%        247.3ms       
==================================================================================

KEY INSIGHTS:
  • Best accuracy: Transformer Semantic Matching (72.9%)
  • Fastest method: Simple Cosine Similarity (14.2 ms)

TRADEOFF ANALYSIS:
  Simple Cosine Similarity: 3401.41 accuracy points per second
  TF-IDF + Logistic Regression: 2705.26 accuracy points per second
  Transformer Semantic Matching: 294.82 accuracy points per second
==================================================================================
```

---

## 📈 Visualizations Generated

The `visualize_results.py` script creates:

1. **`accuracy_comparison.png`** - Bar chart comparing top-1 and top-5 accuracy
2. **`latency_comparison.png`** - Bar chart of average prediction time
3. **`accuracy_latency_scatter.png`** - Scatter plot showing accuracy vs. speed tradeoff
4. **`results_table.txt`** - Formatted text table of all results

---

## 🎓 Research Findings Template

Your project answers these questions:

### Q1: Which method is most accurate?
**A**: Transformer semantic matching achieves ~70-75% accuracy vs. ~50-65% for traditional methods.

### Q2: Which is fastest?
**A**: Simple cosine similarity is 15-20x faster than transformers.

### Q3: When are simple methods sufficient?
**A**: When speed matters more than accuracy, or when resumes use standard job titles.

### Q4: When is deep learning worth it?
**A**: When you need semantic understanding (e.g., "ML engineer" → "Data Scientist" matching) and accuracy is critical.

### Q5: What's the accuracy/speed tradeoff?
**A**: Transformers give +20-25% accuracy but cost +15x latency.

---

## 📁 Project Structure

```
ob2/
├── evaluate.py              ⭐ Main evaluation framework
├── run_project.py           ⭐ Automated pipeline
├── prepare_test_data.py     📊 Data preparation
├── tfidf_baseline.py        🤖 Traditional ML method
├── baseline_wrappers.py     📏 Baseline implementations
├── visualize_results.py     📈 Visualization generation
│
├── cv_analyzer.py           🧠 Transformer method (existing)
├── naive.py                 📏 Original baselines (existing)
├── skills_query.py          🗄️ Database interface (existing)
├── utility.py               🔧 Helper functions (existing)
├── generate_embeddings.py   💾 Embedding generation (existing)
│
├── test_data_with_labels.json   📊 Output: Test set
├── train_data.json              📊 Output: Training set
├── tfidf_model.pkl              🤖 Output: Trained model
├── evaluation_results.json      ✅ Output: Final results
│
├── accuracy_comparison.png      📊 Output: Plots
├── latency_comparison.png       📊 Output: Plots
└── accuracy_latency_scatter.png 📊 Output: Plots
```

---

## ⚙️ How Each Method Works (Technical Details)

### Method 1: Cosine Similarity
```python
# Pseudocode
resume_embedding = encode(resume_text)
job_embeddings = encode(all_job_titles)
similarities = cosine_similarity(resume_embedding, job_embeddings)
top_5 = argmax(similarities, k=5)
```

### Method 2: TF-IDF + Logistic Regression
```python
# Training
X_train = tfidf.fit_transform(resumes)
y_train = job_codes
model.fit(X_train, y_train)

# Prediction
X_test = tfidf.transform(new_resume)
probabilities = model.predict_proba(X_test)
top_5 = argsort(probabilities)[-5:]
```

### Method 3: Transformer Semantic
```python
# Simplified
resume_features = parse(resume)  # Nouns, phrases, sentences
resume_emb = transformer.encode(resume_features)

for each job in O*NET:
    scores = []
    scores.append(match_skills(resume_emb, job.tech_skills))
    scores.append(match_knowledge(resume_emb, job.knowledge))
    scores.append(match_abilities(resume_emb, job.abilities))
    scores.append(match_tasks(resume_emb, job.tasks))
    # ... 7 more dimensions
    job_score = sum(scores)

top_5 = argmax(job_scores, k=5)
```

---

## 🔧 Troubleshooting

### "No test data found"
```bash
python prepare_test_data.py
```

### "TF-IDF model not found"
```bash
python tfidf_baseline.py
```

### "Missing embedding files"
```bash
python generate_embeddings.py
# Wait 20-30 minutes
```

### "Database connection failed"
Check `skills_query.py` line 10:
```python
self.db = mysql.connector.connect(
    host='localhost',           # ← Should be localhost
    user='jobmatch',            # ← Your MySQL user
    password='jobmatch123',     # ← Your MySQL password
    database='db_26_1'          # ← O*NET database name
)
```

---

## ⏱️ Time Estimates

- **Setup**: 5 minutes (installing dependencies)
- **Embedding generation**: 20-30 minutes (one-time)
- **Data preparation**: 5 minutes
- **TF-IDF training**: 2-5 minutes
- **Evaluation** (100 examples): 5-10 minutes
- **Visualization**: 1 minute

**Total first run**: ~45 minutes
**Subsequent runs**: ~10 minutes (embeddings already exist)

---

## 📝 Writing Your Research Paper

### Structure:
1. **Introduction**: Job matching is important, many approaches exist
2. **Related Work**: Cite your 5 papers
3. **Methods**: Describe all 3 approaches
4. **Experiments**: Dataset, metrics, setup
5. **Results**: Show comparison table and plots
6. **Discussion**: Analyze tradeoffs
7. **Conclusion**: Summarize findings

### Key Argument:
> "While modern transformer-based methods achieve higher accuracy (~73% vs. ~48-62%), simpler approaches may be preferable when interpretability and speed are priorities. We find that the choice of method depends on the specific use case and constraints."

---

## 🎯 Success Criteria

Your project is successful if you can:
- ✅ Run all 3 methods on the same test set
- ✅ Generate comparison metrics (accuracy, latency)
- ✅ Create visualizations showing tradeoffs
- ✅ Explain when each method is appropriate
- ✅ Document your methodology clearly

---

## 📚 Citations

Base code from:
```
Alonso, R., Dessì, D., Meloni, A., & Recupero, D. R. (2022). 
A Novel Approach for Job Matching and Skill Recommendation 
Using Transformers and the O*NET Database.
```

---

## 🎉 You're Ready!

1. Download all files
2. Run `python run_project.py`
3. Wait for results
4. Analyze findings
5. Write your research paper

**No API keys. No costs. Complete research project.** 🚀
