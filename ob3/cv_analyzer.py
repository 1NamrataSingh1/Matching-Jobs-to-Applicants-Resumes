# import csv
# import json
import json

import torch
from textblob import Blobber
from textblob import Word
from textblob.taggers import NLTKTagger
from skills_query import QueryMysql

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

settings = {"model": "all-mpnet-base-v2", "skills": "skill_embeddings.pt", "jobs": "titles_embeddings.pt",
            "tasks": "task_embeddings.pt", "tools": "tools_embeddings.pt"}

# settings = {"model": "all-MiniLM-L6-v2", "skills": "skill_embeddings-2.pt", "jobs": "titles_embeddings-2.pt",
# "tasks": "task_embeddings-2.pt", "tools": "tools_embeddings-2.pt"}

model = SentenceTransformer(settings["model"], device='cuda' if torch.cuda.is_available() else "cpu")


class Parser:
    def __init__(self):
        self.tb = Blobber(pos_tagger=NLTKTagger())

    def get_data(self, sentence):
        data = {}
        nouns = []
        nouns_phrases = []
        numbers = []
        result = self.tb(sentence)
        data['sentences'] = [str(x) for x in result.sentences]

        for sentence in result.sentences:
            nouns_phrases.extend(list(sentence.noun_phrases))

            for tag in sentence.tags:
                if tag[1].startswith('N'):
                    w = Word(tag[0]).lemmatize()
                    nouns.append(str(w))
                if tag[1].startswith('CD'):
                    w = Word(tag[0]).lemmatize()
                    numbers.append(str(w))

        data['nouns'] = nouns
        data['numbers'] = numbers
        data['nouns phrases'] = nouns_phrases
        return data


def get_score(db_q, emb_sentences, jobs):
    skill_embeddings = torch.load(settings["skills"])
    job_codes = db_q.get_job_codes() if len(jobs) == 0 else jobs
    scores = []

    for job_code in job_codes:
        tech_skills = db_q.get_tech_skills(job_code[0])
        skills_names = [x[1] for x in tech_skills]
        embeddings = skill_embeddings.get(job_code[0])
        if embeddings is None:
            scores.append((0, 0, 0, job_code[0], job_code[1], []))
            continue
        st_scores = cos_sim(embeddings, emb_sentences)
        maximus = torch.max(st_scores, 1)
        m = [float(x) for x in maximus.values]
        # ind = [int(x) for x in maximus.indices]
        # a = [sentences[x] for x in ind]

        score = 0
        tot_score = 0

        for skill in tech_skills:
            if skill[3] == 'Y':
                tot_score += 1
            else:
                tot_score += 0.75
        missing = []
        matched = []
        for i in range(len(skills_names)):
            if m[i] > 0.65:
                matched.append([1 if tech_skills[i][3] == 'Y' else 0.75, skills_names[i]])
                if tech_skills[i][3] == 'Y':
                    score += 1
                else:
                    score += 0.75
            else:
                missing.append([1 if tech_skills[i][3] == 'Y' else 0.75, skills_names[i]])

        missing = sorted(missing, key=lambda x: x[0], reverse=True)
        matched = sorted(matched, key=lambda x: x[0], reverse=True)
        points = 0 if tot_score == 0 or score == 0 else float(score / tot_score) + 0.5 * float(score)
        scores.append([points, float(score), float(tot_score), job_code[0], job_code[1], missing, matched])

    return scores


def get_st_scores(emb_sentences, emb_sentences2, db_entities_list, db_entities_list2, db_q, query_function, jobs):
    embeddings = model.encode(db_entities_list)
    embeddings2 = model.encode(db_entities_list2)
    # print(db_entities_list)
    scores = cos_sim(embeddings, emb_sentences)
    scores2 = cos_sim(embeddings2, emb_sentences2)
    maximus = torch.max(scores, 1)
    maximus2 = torch.max(scores2, 1)

    m = [float(x) for x in maximus.values]
    m2 = [float(x) for x in maximus2.values]
    # ind = [int(x) for x in maximus.indices]
    # a = [sentences[x] for x in ind]

    job_codes = db_q.get_job_codes() if len(jobs) == 0 else jobs
    scores = []
    for job_code in job_codes:

        skills = query_function(job_code[0])
        score = 0
        tot_score = 0

        missing = []
        matched = []
        for i, skill in enumerate(skills):
            tot_score += float(skill[1])
            score += float(skill[1]) if m[i] > 0.65 or m2[i] > 0.65 else 0
            if m[i] <= 0.65 and m2[i] <= 0.65:
                missing.append([float(skills[i][1]), skills[i][2], skills[i][3]])
            else:
                matched.append([float(skill[1]), skills[i][2]])
        missing = sorted(missing, key=lambda x: x[0], reverse=True)
        matched = sorted(matched, key=lambda x: x[0], reverse=True)
        points = 0 if tot_score == 0 or score == 0 else float(score / tot_score) + 0.5 * float(score)
        scores.append([points, float(score), float(tot_score), job_code[0], job_code[1], missing, matched])

    return scores


def get_task_scores(db_q, cv_data, jobs):
    task_embeddings = torch.load(settings["tasks"])
    job_codes = db_q.get_job_codes() if len(jobs) == 0 else jobs
    scores = []
    sentences = cv_data['nouns phrases'] + cv_data["sentences"]  # + cv_data['nouns']

    emb_sentences = model.encode(sentences)

    for job_code in job_codes:
        tasks = db_q.get_tasks(job_code[0])
        embeddings = task_embeddings.get(job_code[0])
        if embeddings is None:
            scores.append((0, 0, 0, job_code[0], job_code[1], []))
            continue
        st_scores = cos_sim(embeddings, emb_sentences)
        maximus = torch.max(st_scores, 1)
        m = [float(x) for x in maximus.values]
        score = 0
        tot_score = 0
        missing = []
        matched = []
        for i, task in enumerate(tasks):
            tot_score += float(task[1])
            score += float(task[1]) if m[i] > 0.65 else 0
            if m[i] <= 0.65:
                missing.append([float(task[1]), tasks[i][3]])
            else:
                matched.append([float(task[1]), tasks[i][3]])
        missing = sorted(missing, key=lambda x: x[0], reverse=True)
        matched = sorted(matched, key=lambda x: x[0], reverse=True)
        points = 0 if tot_score == 0 or score == 0 else float(score / tot_score) + 0.5 * float(score)
        scores.append([points, float(score), float(tot_score), job_code[0], job_code[1], missing, matched])
    return scores


def get_tools_scores(db_q, cv_data, jobs):
    tools_embeddings = torch.load(settings["tools"])
    job_codes = db_q.get_job_codes() if len(jobs) == 0 else jobs
    scores = []
    sentences = cv_data['nouns phrases'] + cv_data['nouns'] + cv_data["sentences"]

    emb_sentences = model.encode(sentences)

    for job_code in job_codes:
        tools = db_q.get_tools(job_code[0])
        tool_names = [x[1] for x in tools]
        embeddings = tools_embeddings.get(job_code[0])
        if embeddings is None:
            scores.append((0, 0, 0, job_code[0], job_code[1], []))
            continue
        st_scores = cos_sim(embeddings, emb_sentences)
        maximus = torch.max(st_scores, 1)
        m = [float(x) for x in maximus.values]
        # ind = [int(x) for x in maximus.indices]
        # a = [sentences[x] for x in ind]

        score = 0
        tot_score = 0

        missing = []
        matched = []
        for i in range(len(tool_names)):
            tot_score += 1
            if m[i] > 0.65:
                matched.append([1, tool_names[i]])
                score += 1
            else:
                missing.append([1, tool_names[i]])

        points = 0 if tot_score == 0 or score == 0 else float(score / tot_score) + 0.5 * float(score)
        scores.append([points, float(score), float(tot_score), job_code[0], job_code[1], missing, matched])

    return scores


def cv_get_results(resume, q=QueryMysql(), p=Parser(), jobs=None, missing=False):
    if jobs is None or len(jobs) == 0:
        jobs = []
    else:
        jobs = get_st_job_titles(jobs)
        jobs = jobs["codes"]

    skills_names = q.get_skills_descriptions()
    skills_names2 = [x[1] for x in skills_names]
    skills_names = [x[0] for x in skills_names]

    knowledge_names = q.get_knowledge()
    knowledge_names2 = [x[3] for x in knowledge_names]
    knowledge_names = [x[2] for x in knowledge_names]

    abilities_names = q.get_abilities()
    abilities_names2 = [x[3] for x in abilities_names]
    abilities_names = [x[2] for x in abilities_names]

    work_activities = q.get_work_activities()
    work_activities_names = [x[2] for x in work_activities]
    work_activities_names2 = [x[3] for x in work_activities]

    cv_data = p.get_data(resume)

    data_to_send = model.encode(cv_data['nouns phrases'] + cv_data['nouns'])
    data_to_send2 = model.encode(cv_data['sentences'])

    score1 = get_score(q, data_to_send, jobs)

    score2 = get_st_scores(data_to_send, data_to_send2, skills_names, skills_names2, q, q.get_skills_im, jobs)

    score3 = get_st_scores(data_to_send, data_to_send2, knowledge_names, knowledge_names2, q, q.get_knowledge, jobs)

    score4 = get_st_scores(data_to_send, data_to_send2, abilities_names, abilities_names2, q, q.get_abilities, jobs)

    score5 = get_st_scores(data_to_send, data_to_send2, work_activities_names, work_activities_names2, q,
                           q.get_work_activities, jobs)

    score6 = get_task_scores(q, cv_data, jobs)

    score7 = get_tools_scores(q, cv_data, jobs)

    score_tot = []

    for j in range(len(score1)):
        s = [
            score1[j][0] + score2[j][0] + score3[j][0] + score4[j][0] + score5[j][0] + score6[j][0] + score7[j][0],
            score1[j][1] + score2[j][1] + score3[j][1] + score4[j][1] + score5[j][1] + score6[j][1] + score7[j][1],
            score1[j][2] + score2[j][2] + score3[j][2] + score4[j][2] + score5[j][2] + score6[j][2] + score7[j][2],
            score1[j][3],
            score1[j][4]
        ]
        if missing:
            max_scores = {
                "tech_skills_max_score": score1[j][2],
                "skills_max_score": score2[j][2],
                "knowledge_max_score": score3[j][2],
                "abilities_max_score": score4[j][2],
                "work_activities_max_score": score5[j][2],
                "tasks_max_score": score6[j][2],
                "tools_max_score": score7[j][2]
            }
            s.append(max_scores)

            missing_elements = {
                "missing_elements":
                    {
                        "tech_skills": score1[j][5],
                        "skills": score2[j][5],
                        "knowledge": score3[j][5],
                        "abilities": score4[j][5],
                        "work_activities": score5[j][5],
                        "tasks": score6[j][5],
                        "tools": score7[j][5]
                    }
            }
            s.append(missing_elements)

            matched_elements = {
                "matched_elements":
                    {
                        "tech_skills": score1[j][6],
                        "skills": score2[j][6],
                        "knowledge": score3[j][6],
                        "abilities": score4[j][6],
                        "work_activities": score5[j][6],
                        "tasks": score6[j][6],
                        "tools": score7[j][6]
                    }
            }
            s.append(matched_elements)

        score_tot.append(s)

    score_tot = sorted(score_tot, key=lambda x: x[0], reverse=True)
    return score_tot[:5]


def get_st_job_titles(jobs):
    if len(jobs) == 0:
        return []

    jobs_titles = torch.load(settings["jobs"])
    titles = jobs_titles["titles"]
    codes = jobs_titles["codes"]
    emb_sentences = jobs_titles["emb_titles"]
    embeddings = model.encode(jobs)
    scores = cos_sim(embeddings, emb_sentences)
    maximus = torch.max(scores, 1)
    indices = [int(x) for x in maximus.indices]
    obt_titles = [titles[x] for x in indices]
    obt_codes = [codes[x] for x in indices]
    codes = [[codes[x], titles[x]] for x in indices]
    results = {}
    for i in range(len(jobs)):
        results[jobs[i]] = [obt_titles[i], obt_codes[i]]
    results["codes"] = codes
    return results


def suggest(resume, job):
    courses = load_courses()
    threshold = 34.62
    predicted_category = cv_get_results(resume, missing=False)[0]

    results = cv_get_results(resume, jobs=[job], missing=True)
    score = results[0][0]
    result = {
        "best_job": predicted_category[4],
        "best_job_o-net_id": predicted_category[3],
        "best_job_score": predicted_category[0:3],
        "requested_job": job,
        "o-net_job_code": results[0][3],
        "o-net_category": results[0][4],
        "resume_score": score,
        "minimum_score_for_eligibility": threshold,
        "outcome": score - threshold,
        "max_scores": results[0][5],
        "missing_elements": results[0][6].get("missing_elements"),
        "matched_elements": results[0][7].get("matched_elements"),
    }
    if score < threshold:
        missing_elements = result.get("missing_elements")
        max_scores = result.get("max_scores")
        for key in missing_elements:
            me = []
            for e in missing_elements.get(key):
                gain = e[0] / max_scores.get(key + "_max_score") + 0.5 * e[0]
                element = {
                    "element_value": e[0],
                    "element_name": e[1]
                }
                if len(e) > 2:
                    element["element_description"] = e[2]
                element["additional_score"] = gain
                me.append(element)
            missing_elements[key] = me

        for key in missing_elements:
            elements = [x.get("element_name") for x in missing_elements.get(key)]
            for i, element in enumerate(elements):
                missing_elements[key][i]["udemy courses"] = courses.get(element)  # get_course(element)
    return result


def get_course(sentences):
    course_embeddings = torch.load('course_embeddings.pt')
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


def load_courses():
    with open("suggested_courses.json", encoding='utf-8') as data_file:
        courses = json.loads(data_file.read())
    return courses

