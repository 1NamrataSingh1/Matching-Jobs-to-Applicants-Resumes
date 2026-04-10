"""
Generate the missing embedding files needed by cv_analyzer.py
Run this from the ob2 directory
"""
import torch
from sentence_transformers import SentenceTransformer
from skills_query import QueryMysql

print("Loading model...")
model = SentenceTransformer('all-mpnet-base-v2', device='cuda' if torch.cuda.is_available() else "cpu")

print("Connecting to database...")
q = QueryMysql()

# ============================================================================
# 1. Generate skill_embeddings.pt (tech skills organized by job code)
# ============================================================================
print("\n[1/4] Generating skill_embeddings.pt...")
job_codes = q.get_job_codes()
skill_embeddings = {}

for i, (job_code, job_title) in enumerate(job_codes):
    if i % 50 == 0:
        print(f"  Processing skills for job {i+1}/{len(job_codes)}: {job_title}")
    
    tech_skills = q.get_tech_skills(job_code)
    if len(tech_skills) > 0:
        skill_names = [x[1] for x in tech_skills]  # x[1] is the skill name
        embeddings = model.encode(skill_names)
        skill_embeddings[job_code] = embeddings

torch.save(skill_embeddings, 'skill_embeddings.pt')
print(f"  ✓ Saved skill_embeddings.pt with {len(skill_embeddings)} job codes")

# ============================================================================
# 2. Generate titles_embeddings.pt (all job titles)
# ============================================================================
print("\n[2/4] Generating titles_embeddings.pt...")
job_titles_data = q.get_job_titles()  # Returns both occupation_data and alternate_titles

titles = [x[1] for x in job_titles_data]
codes = [x[0] for x in job_titles_data]

print(f"  Encoding {len(titles)} job titles...")
emb_titles = model.encode(titles, show_progress_bar=True)

titles_dict = {
    "titles": titles,
    "codes": codes,
    "emb_titles": emb_titles
}

torch.save(titles_dict, 'titles_embeddings.pt')
print(f"  ✓ Saved titles_embeddings.pt with {len(titles)} titles")

# ============================================================================
# 3. Generate task_embeddings.pt (tasks organized by job code)
# ============================================================================
print("\n[3/4] Generating task_embeddings.pt...")
task_embeddings = {}

for i, (job_code, job_title) in enumerate(job_codes):
    if i % 50 == 0:
        print(f"  Processing tasks for job {i+1}/{len(job_codes)}: {job_title}")
    
    tasks = q.get_tasks(job_code)
    if len(tasks) > 0:
        task_texts = [x[3] for x in tasks]  # x[3] is the task description
        embeddings = model.encode(task_texts)
        task_embeddings[job_code] = embeddings

torch.save(task_embeddings, 'task_embeddings.pt')
print(f"  ✓ Saved task_embeddings.pt with {len(task_embeddings)} job codes")

# ============================================================================
# 4. Generate tools_embeddings.pt (tools organized by job code)
# ============================================================================
print("\n[4/4] Generating tools_embeddings.pt...")
tools_embeddings = {}

for i, (job_code, job_title) in enumerate(job_codes):
    if i % 50 == 0:
        print(f"  Processing tools for job {i+1}/{len(job_codes)}: {job_title}")
    
    tools = q.get_tools(job_code)
    if len(tools) > 0:
        tool_names = [x[1] for x in tools]  # x[1] is the tool/example name
        embeddings = model.encode(tool_names)
        tools_embeddings[job_code] = embeddings

torch.save(tools_embeddings, 'tools_embeddings.pt')
print(f"  ✓ Saved tools_embeddings.pt with {len(tools_embeddings)} job codes")

print("\n" + "="*60)
print("✅ ALL DONE! Generated 4 embedding files:")
print("  - skill_embeddings.pt")
print("  - titles_embeddings.pt")
print("  - task_embeddings.pt")
print("  - tools_embeddings.pt")
print("="*60)
print("\nYou can now run cv_get_results() successfully!")