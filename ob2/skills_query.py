# install -> pip install mysql-connector-python
# install -> pip install fastapi[all]

import mysql.connector
import re
import os

class QueryMysql:
    def __init__(self):
        self.db = mysql.connector.connect(host='localhost', user='jobmatch', password='jobmatch123', database='db_26_1')
        self.mc = self.db.cursor()
        self.check = re.compile('^[0-9][0-9]-[0-9][0-9][0-9][0-9]\.[0-9][0-9]')
        self.query = '''SELECT content_model_reference.element_name , skills.data_value, skills.scale_id, 
        content_model_reference.element_id FROM skills INNER JOIN content_model_reference ON 
        content_model_reference.element_id = skills.element_id WHERE onetsoc_code = %(code)s ORDER BY 
        skills.data_value DESC '''

    def get_job_code(self, user_input):
        self.mc.execute("SELECT onetsoc_code, title FROM occupation_data WHERE title = %(job)s", {'job': user_input})
        jobs = self.mc.fetchall()

        self.mc.execute("SELECT onetsoc_code, alternate_title FROM alternate_titles WHERE alternate_title = %(job)s",
                        {'job': user_input})
        jobs2 = self.mc.fetchall()
        jobs.extend(jobs2)

        if len(jobs) == 0:
            self.mc.execute("SELECT onetsoc_code, title FROM occupation_data WHERE title like %(job)s",
                            {'job': '% ' + user_input + ' %'})
            jobs = self.mc.fetchall()
            self.mc.execute(
                "SELECT onetsoc_code, alternate_title FROM alternate_titles WHERE alternate_title like %(job)s",
                {'job': '% ' + user_input + ' %'})
            jobs2 = self.mc.fetchall()
            jobs.extend(jobs2)

        if len(jobs) == 1:
            return jobs[0][0]
        return jobs

    def get_job_from_code(self, user_input):
        self.mc.execute("SELECT onetsoc_code, title FROM occupation_data WHERE onetsoc_code = %(code)s",
                        {'code': user_input})
        jobs = self.mc.fetchall()

        if len(jobs) == 1:
            return jobs[0][0]

    def get_job(self, user_input):
        self.mc.execute("SELECT onetsoc_code, title FROM occupation_data WHERE onetsoc_code = %(code)s",
                        {'code': user_input})
        jobs = self.mc.fetchall()
        return jobs

    # get skill for a job given
    def new_query(self, user_input):
        res = {}
        user_input_check = self.check.match(user_input)
        if user_input_check is not None:
            user_input_span = user_input_check.span()
        if user_input_check is not None and user_input_span[0] == 0 and user_input_span[1] == 10:
            job_id = self.get_job_from_code(user_input[0:10])
        else:
            job_id = self.get_job_code(user_input)

        if not isinstance(job_id, list):  # is not None:
            self.mc.execute(self.query, {'code': job_id})
            skills = self.mc.fetchall()
            res['skills'] = [s for s in skills if s[2] == 'LV']
            # sorted_list = sorted(skills,key=lambda x: x[0])
        else:
            res['jobs'] = job_id
        return res

    def suggest(self, user_input):
        skills = [(x[3], x[1]) for x in user_input.skills]
        skills = sorted(skills, key=lambda x: x[0])
        jobs = self.get_job_codes()
        diffs = []
        for job in jobs:
            job_skills = self.get_skills(job[0])
            if len(job_skills) == 0:
                diff = 999
                continue
            diff = 0
            for n in range(len(job_skills)):
                # print(skills[n][1], ' - ', float(job_skills[n][1]), ' = ',  abs(skills[n][1]-float(job_skills[n][1])))
                diff += abs(skills[n][1] - float(job_skills[n][1]))

            diffs.append((diff, job))
        diffs = sorted(diffs, key=lambda x: x[0])
        result = {}
        results = []
        for suggest in diffs[:5]:
            results.append([suggest[1][0], suggest[1][1], (round(suggest[0], 2))])
        result['suggested_jobs'] = results
        return result

    def get_skills(self, job_id):
        query = '''SELECT element_id, data_value FROM skills WHERE scale_id='LV' AND onetsoc_code=%(code)s ORDER BY 
                element_id ASC '''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_skills_im(self, job_id):
        query = '''SELECT onetsoc_code,
        skills.data_value,
        content_model_reference.element_name,
        content_model_reference.description 
        FROM skills INNER JOIN content_model_reference 
        ON content_model_reference.element_id = skills.element_id
        WHERE scale_id='IM' AND onetsoc_code=%(code)s 
        ORDER BY 'skills.element_id' ASC'''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_job_codes(self):
        self.mc.execute("SELECT DISTINCT onetsoc_code, title FROM occupation_data")
        return self.mc.fetchall()

    def get_tech_skills(self, job_id):
        query = "SELECT * FROM technology_skills WHERE onetsoc_code=%(code)s"
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_skills_descriptions(self):
        query = '''SELECT content_model_reference.element_name,
        content_model_reference.description
        FROM `skills` INNER JOIN content_model_reference 
        ON skills.element_id=content_model_reference.element_id 
        WHERE `onetsoc_code`= '11-1011.00' AND scale_id='IM' 
        ORDER BY 'skills.element_id' ASC '''
        self.mc.execute(query)
        return self.mc.fetchall()

    def get_knowledge(self, job_id='11-1011.00'):
        query = '''SELECT onetsoc_code,
        data_value,
        content_model_reference.element_name,
        content_model_reference.description 
        FROM knowledge INNER JOIN content_model_reference 
        ON knowledge.element_id=content_model_reference.element_id
        WHERE scale_id="IM" AND onetsoc_code=%(code)s 
        ORDER BY knowledge.element_id ASC '''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_abilities(self, job_id='11-1011.00'):
        query = '''SELECT onetsoc_code,data_value,content_model_reference.element_name, 
        content_model_reference.description FROM abilities INNER JOIN content_model_reference ON 
        abilities.element_id=content_model_reference.element_id WHERE scale_id="IM" AND onetsoc_code=%(code)s ORDER 
        BY abilities.element_id ASC '''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_job_titles(self):
        self.mc.execute("SELECT onetsoc_code, title FROM occupation_data")
        jobs = self.mc.fetchall()
        self.mc.execute("SELECT onetsoc_code, alternate_title FROM alternate_titles")
        jobs2 = self.mc.fetchall()
        jobs.extend(jobs2)
        return jobs

    def get_work_activities(self, job_id='11-1011.00'):
        query = '''SELECT onetsoc_code,data_value,content_model_reference.element_name, 
        content_model_reference.description FROM work_activities INNER JOIN content_model_reference ON 
        work_activities.element_id=content_model_reference.element_id 
        WHERE work_activities.scale_id="IM" AND onetsoc_code=%(code)s 
        ORDER BY work_activities.element_id ASC '''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    # get skill for a job given
    def get_all_skills(self, user_input):
        res = {}
        user_input_check = self.check.match(user_input)
        if user_input_check is not None:
            user_input_span = user_input_check.span()
        if user_input_check is not None and user_input_span[0] == 0 and user_input_span[1] == 10:
            job_id = self.get_job_from_code(user_input[0:10])
        else:
            job_id = self.get_job_code(user_input)

        if not isinstance(job_id, list):  # is not None:
            res['job'] = self.get_job(job_id)
            res['tech_skills'] = self.get_tech_skills(job_id)
            res['skills'] = self.get_skills_im(job_id)
            res['knowledge'] = self.get_knowledge(job_id)
            res['abilities'] = self.get_abilities(job_id)
            res['work_activities'] = self.get_work_activities(job_id)
        else:
            res['jobs'] = job_id
        return res

    def get_tasks(self, job_id='11-1011.00'):
        query = '''SELECT task_statements.onetsoc_code, data_value, task_ratings.task_id, task_statements.task 
                   FROM task_ratings INNER JOIN task_statements ON task_ratings.task_id=task_statements.task_id
                   WHERE scale_id="IM" AND task_statements.onetsoc_code=%(code)s
                   ORDER BY task_statements.onetsoc_code ASC , task_statements.task_id ASC'''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_tools(self, job_id='11-1011.00'):
        query = '''SELECT * FROM tools_used WHERE onetsoc_code=%(code)s'''
        self.mc.execute(query, {'code': job_id})
        return self.mc.fetchall()

    def get_all_tech_skills(self):
        self.mc.execute("SELECT DISTINCT example FROM technology_skills")
        return self.mc.fetchall()

    def get_all_tasks(self):
        self.mc.execute("SELECT DISTINCT task FROM task_statements")
        return self.mc.fetchall()

    def get_all_tools(self):
        self.mc.execute("SELECT DISTINCT example FROM tools_used")
        return self.mc.fetchall()