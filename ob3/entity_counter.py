import json
import matplotlib.pyplot as plt

from skills_query import QueryMysql

q = QueryMysql()


def calculate():
    job_codes = q.get_job_codes()

    scores = []
    tech_skills = {}
    skills = {}
    knowledge = {}
    abilities = {}
    work_activities = {}
    tasks = {}
    tools_used = {}

    for job in job_codes:
        result = q.get_all_skills(job[0])
        ts = len(result.get("tech_skills"))
        sk = len(result.get("skills"))
        kn = len(result.get("knowledge"))
        ab = len(result.get("abilities"))
        wa = len(result.get("work_activities"))
        ta = len(result.get("tasks"))
        to = len(result.get("tools_used"))

        if tech_skills.get(ts) is None:
            tech_skills[ts] = 1
        else:
            tech_skills[ts] += 1

        if skills.get(sk) is None:
            skills[sk] = 1
        else:
            skills[sk] += 1

        if knowledge.get(kn) is None:
            knowledge[kn] = 1
        else:
            knowledge[kn] += 1

        if abilities.get(ab) is None:
            abilities[ab] = 1
        else:
            abilities[ab] += 1

        if work_activities.get(wa) is None:
            work_activities[wa] = 1
        else:
            work_activities[wa] += 1

        if tasks.get(ta) is None:
            tasks[ta] = 1
        else:
            tasks[ta] += 1

        if tools_used.get(to) is None:
            tools_used[to] = 1
        else:
            tools_used[to] += 1

    # tech_skills_frequency = [[x, tech_skills.get(x)] for x in tech_skills]
    # tech_skills_frequency = sorted(tech_skills_frequency, key=lambda x: x[1], reverse=True)
    #
    # skills_frequency = [[x, skills.get(x)] for x in skills]
    # skills_frequency = sorted(skills_frequency, key=lambda x: x[1], reverse=True)
    #
    # knowledge_frequency = [[x, knowledge.get(x)] for x in knowledge]
    # knowledge_frequency = sorted(knowledge_frequency, key=lambda x: x[1], reverse=True)
    #
    # abilities_frequency = [[x, abilities.get(x)] for x in abilities]
    # abilities_frequency = sorted(abilities_frequency, key=lambda x: x[1], reverse=True)
    #
    # work_activities_frequency = [[x, work_activities.get(x)] for x in work_activities]
    # work_activities_frequency = sorted(work_activities_frequency, key=lambda x: x[1], reverse=True)
    #
    # tasks_frequency = [[x, tasks.get(x)] for x in tasks]
    # tasks_frequency = sorted(tasks_frequency, key=lambda x: x[1], reverse=True)
    #
    # tools_used_frequency = [[x, tools_used.get(x)] for x in tools_used]
    # tools_used_frequency = sorted(tools_used_frequency, key=lambda x: x[1], reverse=True)

    tech_skills_frequency = extract(tech_skills)
    skills_frequency = extract(skills)
    knowledge_frequency = extract(knowledge)
    abilities_frequency = extract(abilities)
    work_activities_frequency = extract(work_activities)
    tasks_frequency = extract(tasks)
    tools_used_frequency = extract(tools_used)

    print("tech_skills", tech_skills_frequency)
    print()
    print("tools_used", tools_used_frequency)
    print()
    print("tasks", tasks_frequency)

    data = {"tech_skills": tech_skills_frequency, "skills": skills_frequency, "knowledge": knowledge_frequency,
            "abilities": abilities_frequency, "work_activities": work_activities_frequency,
            "tasks": tasks_frequency, "tools_used": tools_used_frequency
            }

    with open('entity_statistics2.json', "w", encoding="utf-8") as text_file:
        print(json.dumps(data), file=text_file)


def extract(data):
    result = []
    for i in range(426):
        freq = data.get(i)
        if freq is None:
            freq = 0
        result.append(freq)
    return result


def plot():
    with open("entity_statistics2.json", encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
    print(data)
    tech_skills = data.get("tech_skills")
    plt.plot(range(426)[1:100], tech_skills[1:100])
    plt.show()


def calculate2():
    job_codes = q.get_job_codes()

    scores = []
    tech_skills = {}
    skills = {}
    knowledge = {}
    abilities = {}
    work_activities = {}
    tasks = {}
    tools_used = {}

    for job in job_codes:
        result = q.get_all_skills(job[0])
        ts = result.get("tech_skills")
        sk = result.get("skills")
        kn = result.get("knowledge")
        ab = result.get("abilities")
        wa = result.get("work_activities")
        ta = result.get("tasks")
        to = result.get("tools_used")

        # for e in ts:
        #     key = int(e[2])
        #     key2 = e[1]
        #     if tech_skills.get(key) is None:
        #         tech_skills[key] = 1
        #     else:
        #         tech_skills[key] += 1

        for e in ta:
            # print(e)
            key = int(e[2])
            key2 = e[3]
            if tasks.get(key2) is None:
                tasks[key2] = 1
            else:
                tasks[key2] += 1

        # for e in to:
        #     # print(e)
        #     # key = int(e[2])
        #     key2 = e[1]
        #     if tools_used.get(key2) is None:
        #         tools_used[key2] = 1
        #     else:
        #         tools_used[key2] += 1

    # print(len(tech_skills))
    # tech_skills_frequency = [[x, tech_skills.get(x)] for x in tech_skills]
    # tech_skills_frequency = sorted(tech_skills_frequency, key=lambda x: x[1], reverse=True)
    # print(tech_skills_frequency[:50])

    print(len(tasks))
    tasks_frequency = [[x, tasks.get(x)] for x in tasks]
    tasks_frequency = sorted(tasks_frequency, key=lambda x: x[1], reverse=True)
    print(tasks_frequency[:50])

    # print(len(tools_used))
    # tools_used_frequency = [[x, tools_used.get(x)] for x in tools_used]
    # tools_used_frequency = sorted(tools_used_frequency, key=lambda x: x[1], reverse=True)
    # print(tools_used_frequency[:50])


def estrai_dati(dizionario, elementi, chiave):
    for e in elementi:
        key = e[chiave]
        if dizionario.get(key) is None:
            dizionario[key] = [float(e[1])]
        else:
            dizionario[key].append(float(e[1]))


def calcola_media(dizionario):
    medio = ""
    for key in dizionario:
        valore_medio = sum(dizionario.get(key)) / len(dizionario.get(key))
        medio += key + "\t" + str(valore_medio) + "\n"
    print(medio)


def media():
    job_codes = q.get_job_codes()

    skills = {}
    knowledge = {}
    abilities = {}
    work_activities = {}

    for job in job_codes:
        result = q.get_all_skills(job[0])
        sk = result.get("skills")
        kn = result.get("knowledge")
        ab = result.get("abilities")
        wa = result.get("work_activities")

        estrai_dati(skills, sk, 2)
        estrai_dati(knowledge, kn, 2)
        estrai_dati(abilities, ab, 2)
        estrai_dati(work_activities, wa, 2)

    calcola_media(skills)
    calcola_media(knowledge)
    calcola_media(abilities)
    calcola_media(work_activities)


# calculate()
# plot()
calculate2()
# media()
