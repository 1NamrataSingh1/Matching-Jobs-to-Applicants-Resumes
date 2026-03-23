import json
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

settings = {"model": "all-mpnet-base-v2", "skills": "skill_embeddings.pt", "jobs": "titles_embeddings.pt",
            "tasks": "task_embeddings.pt", "tools": "tools_embeddings.pt"}


def get_st_job_titles(jobs):
    model = SentenceTransformer(settings["model"], device='cuda' if torch.cuda.is_available() else "cpu")
    onet_jobs = torch.load(settings["jobs"])

    titles = onet_jobs.get("titles")
    codes = onet_jobs.get("codes")
    embeddings = model.encode(jobs)
    emb_sentences = onet_jobs.get("emb_titles")
    scores = cos_sim(embeddings, emb_sentences)
    print(scores.size())
    maximus = torch.max(scores, 1)
    print(maximus.values.size())
    print(maximus.indices)
    indices = [int(x) for x in maximus.indices]
    obt_titles = [titles[x] for x in indices]
    obt_codes = [codes[x] for x in indices]
    results = {}
    for i in range(len(jobs)):
        results[jobs[i]] = [obt_titles[i], obt_codes[i]]
    with open('jobs_titles.json', "w", encoding="utf-8") as text_file:
        print(json.dumps(results), file=text_file)
    return results


def get_matching_job_titles(jobs_titles, jobs):
    model = SentenceTransformer(settings["model"], device='cuda' if torch.cuda.is_available() else "cpu")
    titles = [x for x in jobs_titles]
    onet_titles = [jobs_titles[x][0] for x in jobs_titles]
    codes = [jobs_titles[x][1] for x in jobs_titles]
    embeddings = model.encode(jobs)
    emb_sentences = model.encode(titles)
    scores = cos_sim(embeddings, emb_sentences)
    print(scores.size())
    maximus = torch.max(scores, 1)
    print(maximus.values.size())
    print(maximus.indices)
    indices = [int(x) for x in maximus.indices]
    obt_titles = [titles[x] for x in indices]
    obt_onet_titles = [onet_titles[x] for x in indices]
    obt_codes = [codes[x] for x in indices]
    results = {}
    for i in range(len(jobs)):
        results[jobs[i]] = {"post_category": obt_titles[i], "onet_job": obt_onet_titles[i], "onet_code": obt_codes[i]}
    with open('jobs_matching_titles.json', "w", encoding="utf-8") as text_file:
        print(json.dumps(results), file=text_file)
    return results


def read_data():
    categories = []
    cat = {}
    with open("job_posts.json", encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        for job in data:
            category = job.get("category")
            # print(category)
            if category is not None and category not in categories:
                categories.append(category)
                cat[category] = 0
            if category is not None:
                #print(category)
                cat[category] += 1

    print(categories)
    print(len(categories))
    print(len(data))
    cats = [x for x in cat if cat[x] >= 5]
    onet_categories = get_st_job_titles(cats)
    print(onet_categories)
    # print(cats)
    # with open('job_posts_categories.json', "w", encoding="utf-8") as text_file:
    #     print(json.dumps(cat), file=text_file)


def mach_job_titles():
    jobs = ["Data Science", "Human Resources", "Advocate", "Mechanical Engineer", "Sales",
            "Health and fitness", "Pharmacists", "Java Developer", "Business Analyst", "SAP Developer",
            "Automation Testing", "Electrical Engineering", "Python Developer", "DevOps Engineer",
            "Network Security Engineer", "Database", "Hadoop", "ETL Developer", "DotNet Developer", "Testing"]
    data_file = open("jobs_titles.json", encoding='utf-8')
    data = json.loads(data_file.read())
    data_file.close()
    print(data)
    matching_jobs = get_matching_job_titles(data, jobs)
    print(matching_jobs)


def get_job_posts(job_category):
    import random
    data_file = open("job_posts.json", encoding='utf-8')
    data = json.loads(data_file.read())
    data_file.close()
    proper_class = []
    others = []
    for job in data:
        category = job.get("category")
        if category is not None and category == job_category:
            proper_class.append(job)
        else:
            others.append(job)
    index = []

    n0 = proper_class[random.randrange(len(proper_class) - 1)]

    for i in range(9):
        n = random.randrange(len(others) - 1)
        while n in index:
            n = random.randrange(len(others) - 1)
        index.append(n)
    n1 = [others[x] for x in index]
    n1.append(n0)
    return n1


def get_toy_test():
    wanted_categories = ["Computer and Information Research Scientists", "Lawyers", "Mechanical Engineers"]
    for i, name in enumerate(wanted_categories):
        print(i, name)
        job_posts = get_job_posts(name)
        filename = "job_posts_sample" + str(i) + ".json"
        with open(filename, "w", encoding="utf-8") as text_file:
            print(json.dumps(job_posts), file=text_file)


def get_test_data():
    import random
    data_file = open("job_posts.json", encoding='utf-8')
    data = json.loads(data_file.read())
    data_file.close()

    data_file = open("jobs_matching_titles.json", encoding='utf-8')
    cats = json.loads(data_file.read())
    data_file.close()
    test_data = []
    propers = []

    for cat in cats:
        proper_class = []
        others = []
        for job in data:
            category = job.get("category")

            if category is not None and category == cats[cat]["post_category"]:
                proper_class.append(job)
            elif category is not None:
                others.append(job)
        if len(proper_class) < 6:
            propers.append(proper_class)
            data = others
        else:
            n0 = []
            for j in range(5):
                n = random.randrange(len(proper_class) - 1)
                n0.append(proper_class.pop(n))
            others.extend(proper_class)
            data = others
            propers.append(n0)

    for k, cat in enumerate(cats):
        print(cats[cat]["post_category"])
        proper_class = []
        others = []
        for job in data:
            category = job.get("category")
            if category is not None and category == cats[cat]["post_category"]:
                proper_class.append(job)
            elif category is not None:
                others.append(job)

        for j in range(5):
            n1 = []
            others_categories = []
            for i in range(9):
                n = random.randrange(len(others) - 1)
                while others[n].get("category") in others_categories:
                    n = random.randrange(len(others) - 1)
                others_categories.append(others[n].get("category"))
                n1.append(others.pop(n))
            n1.append(propers[k][j])
            test_data.append(n1)

        others.extend(proper_class)
        data = others

    filename = "five_unique_resumes.json"
    data_file = open(filename, encoding='utf-8')
    resumes = json.loads(data_file.read())
    data_file.close()

    i = 0
    test_data_complete = []
    for cat in resumes:
        res = resumes[cat]
        for r in res:
            jobs = test_data[i]
            i += 1
            test = {"resume": r, "resume_category": cat, "job_posts": jobs}
            test_data_complete.append(test)

    with open("test_data.json", "w", encoding="utf-8") as text_file:
        print(json.dumps(test_data_complete), file=text_file)


def add_information():
    filename = "test_data.json"
    data_file = open(filename, encoding='utf-8')
    data = json.loads(data_file.read())
    data_file.close()
    for i, res in enumerate(data):
        print(i)
        cat = []
        for post in res["job_posts"]:
            if post["category"] not in cat:
                cat.append(post["category"])
        res["post_categories"] = cat

    with open("test_data.json", "w", encoding="utf-8") as text_file:
        print(json.dumps(data), file=text_file)


def main():
    pass

    read_data()
    # mach_job_titles()
    # get_toy_test()
    # get_test_data()
    # add_information()


if __name__ == '__main__':
    main()
