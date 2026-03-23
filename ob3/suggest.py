import json
from skills_query import QueryMysql
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

settings = {"model": "all-mpnet-base-v2"}
model = SentenceTransformer(settings["model"], device='cuda' if torch.cuda.is_available() else "cpu")


def get_course(sentences):
    course_embeddings = torch.load('course_embeddings.pt', weights_only=False)
    embeddings = course_embeddings["embeddings"]
    courses = course_embeddings["data"]
    emb_sentences = model.encode(sentences)
    st_scores = cos_sim(embeddings, emb_sentences)
    maximus = torch.max(st_scores, 1)
    m = [float(x) for x in maximus.values]
    scores = []
    for i in range(len(courses)):
        if m[i] > 0.5:
            scores.append([m[i], courses[i][2], courses[i][1]])
    score_tot = sorted(scores, key=lambda x: x[0], reverse=True)
    return score_tot[:5]


def save_courses(q):
    job_codes = q.get_job_codes()
    with open("suggested_courses.json", encoding='utf-8') as data_file:
        courses = json.loads(data_file.read())

    position = [1, 2, 2, 2, 2, 3, 1]
    for job_code in job_codes:
        res = db_q.get_all_skills(job_code[0])
        entities = [res['tech_skills'], res['skills'], res['knowledge'], res['abilities'], res['work_activities'],
                    res['tasks'], res['tools_used']]
        for i, entity in enumerate(entities):
            pos = position[i]
            for element in entity:
                name = element[pos]
                if name not in courses:
                    courses[name] = get_course(name)

    print(courses)
    with open('suggested_courses.json', "w", encoding="utf-8") as text_file:
        print(json.dumps(courses), file=text_file)


if __name__ == "__main__":
    db_q = QueryMysql()
    save_courses(db_q)