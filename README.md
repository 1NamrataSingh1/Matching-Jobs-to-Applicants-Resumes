# Using Transformers and O-NET to Match Jobs to Applicants Resumes 

This repository contains the source code and the annotation files to reproduce the work described in:

```
Rubén Alonso, Danilo Dessì, Antonello Meloni, Diego Reforgiato Recupero. (2022). A Novel Approach for 
Job Matching and Skill Recommendation Using Transformers and the O*NET Database. UNDER REVIEW
```

This is a work from the [Human Robot Interaction Laboratory](http://hri.unica.it) founded by the University of Cagliari and [R2M Solution](https://www.r2msolution.com/).

## Content of the repository

- *ob1/* contains the source code for reproduce the scenario 1 work

- *ob2/* contains the source code for reproduce the scenario 2 work

- *ob3/* contains the source code for reproduce the scenario 3 work

- *annotations_scenario_1/* contains the annotations for the first scenario where the task of matching a resume with the O\*NET categories is performed. The annotations are provided for our proposed approach (see key *predicted_job* in the json files), and the two baselines (keys *naive_alg1_jobs* and *naive_alg2_jobs*).

- *annotations_scenario_2/* contains the annotations for the second scenario where resumes and job descriptions are matched. The annotations are provided for our approach (see key *predicted_categories_for_curriculum-post_association* in the json) and for the two baselines (see *baseline1* and *baseline2*).

For all the annotations, the user of this repository can find *annotation1* that assesses the first predicted job, and *annotation2* that assesses the five predictions for a resume.

## How to use

### Prerequisites:

1) MySQL

2) Python 3


### Installation:

1) Download O*NET Database from https://www.onetcenter.org/database.html#all-files and import it.

2) Install Python MySQL connector: 
    ```pip install mysql-connector-python```

3) Install Torch:

    for GPU -> ```pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113 ```

    for CPU -> ```pip install torch torchvision torchaudio```

4) Install Sentence Transformers:

    ```pip install sentence-transformers```

5) Install TextBlob:
    
    ```pip install textblob```

    ```python -m textblob.download_corpora```

6) Install Fast API 

    ```pip install "fastapi[all]"```

### Run the program

- Go to the ob1 folder.

Run ```utility.py``` script to save the embeddings used by main script.

To run ```cv_result_analyzer.py``` and get the job matching results you need to write the parameters to connect to the database on
line 6 of the script: 

```host = {"ip": "ip number", "user": "username", "password": "password", "database": "database name"}```


- Go to ob2 folder.

Run the ```eval_step_2*.py``` scripts to get the json files used for the annotations.


- Go to ob3 folder.

Run ```uvicorn main:app --host 0.0.0.0 --port 80``` and in a browser open ```http://localhost/docs```


## Contacts

If you have any questions about our work please contact *antonello.meloni@unica.it* .

## Acknowledgements

This research was partially funded by the [H2020 project STAR](https://star-ai.eu/) - Novel AI technology for dynamic and unpredictable manufacturing environments (grant number 956573).








