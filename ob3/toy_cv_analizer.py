import csv
import json

import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from skills_query import QueryMysql

settings = {"model": "all-mpnet-base-v2", "skills": "skill_embeddings.pt", "jobs": "titles_embeddings.pt",
            "tasks": "task_embeddings.pt", "tools": "tools_embeddings.pt"}

model = SentenceTransformer(settings["model"], device='cuda' if torch.cuda.is_available() else "cpu")


def get_st_scores(sentences, db_q=QueryMysql(), jobs=[]):
    knowledge_names = db_q.get_knowledge()

    knowledge_names = [x[2] for x in knowledge_names]

    embeddings = model.encode(knowledge_names)
    emb_sentences = model.encode(sentences)
    # print(db_entities_list)
    scores = cos_sim(emb_sentences, embeddings)
    print(scores.detach().cpu().numpy().T)
    maximus = torch.max(scores, 1)
    print(maximus)
    m = [float(x) for x in maximus.values]
    ind = [int(x) for x in maximus.indices]
    # a = [sentences[x] for x in ind]

    job_codes = db_q.get_job_codes() if len(jobs) == 0 else jobs
    scores = []
    for job_code in job_codes:
        skills = db_q.get_knowledge(job_code[0])
        score = 0
        tot_score = 0
        print([float(x[1]) for x in skills])
        for skill in skills:
            tot_score += float(skill[1])

        for i, index in enumerate(ind):
            score += float(skills[index][1]) if m[i] > 0.65 else 0

        points = 0 if tot_score == 0 or score == 0 else float(score / tot_score) + 0.5 * float(score)
        scores.append((points, float(score), float(tot_score), job_code[0], job_code[1]))

    return scores


a = get_st_scores(["computers", "training", "maths", "english", "sales", "administrator", "engineer"],
                  jobs=[["15-1251.00", "Java Programmer"]])
print(a)
