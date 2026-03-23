import json
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

resume = cv.get(categories[11])[2] + " Reading comprehension, Active Listening, Mathematics, Critical Thinking"
print(resume)

# exit()

threshold = 34.62
predicted_category = cv_analyzer.cv_get_results(resume, missing=False)[0]

results = cv_analyzer.cv_get_results(resume, jobs=[categories[3]], missing=True)
score = results[0][0]
result = {"cv_category": categories[11],
          "predicted_category": predicted_category[4],
          "predicted_category_o-net_job_code": predicted_category[3],
          "predicted_category_score": predicted_category[0:3],
          "requested_category": categories[3],
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

print(result)
with open('test_missing_qualities7.json', "w", encoding="utf-8") as text_file:
    print(json.dumps(result), file=text_file)
