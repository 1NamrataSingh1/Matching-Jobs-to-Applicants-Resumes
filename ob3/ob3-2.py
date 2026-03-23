import json

import numpy

import cv_analyzer

file = open("five_unique_resumes.json", encoding='utf-8')
cv = json.loads(file.read())
file.close()
categories = [x for x in cv]
print(categories)

cats = ['Data Science', 'Human Resources', 'Advocate', 'Mechanical Engineer', 'Sales', 'Health and fitness',
        'Pharmacists', 'Java Developer', 'Business Analyst', 'SAP Developer', 'Automation Testing',
        'Electrical Engineering', 'Python Developer', 'DevOps Engineer', 'Network Security Engineer', 'Database',
        'Hadoop', 'ETL Developer', 'DotNet Developer', 'Testing']
results = []
values = []
for cat in cats:
    resumes = cv.get(cat)
    for resume in resumes:
        result = cv_analyzer.cv_get_results(resume)
        print(result)
        results.append(result[0])
        values.append(result[0][0])

arr = numpy.array(values)
print(arr.mean())

# resume = cv.get(categories[7])[3]
# print(resume)
# result = {"cv_category": categories[7], "cv_category_score": cv_analyzer.cv_get_results(resume, jobs=[categories[7]]),
#           "requested_category": cats[12], "score": cv_analyzer.cv_get_results(resume, jobs=[categories[12]])}
# print(result)
with open('data_for_average.json', "w", encoding="utf-8") as text_file:
    print(json.dumps(results), file=text_file)

