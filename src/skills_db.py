"""Skill taxonomy, prerequisites and learning resources.

SKILLS maps  category -> canonical skill -> list of aliases.
Aliases that start with a capital letter *and* belong to a skill listed in
CASE_SENSITIVE are ambiguous English words (e.g. "React", "Excel", "Spark")
and are only matched with their exact capitalisation.
"""
from urllib.parse import quote_plus

SKILLS = {
    "Programming Languages": {
        "Python": ["python", "python3"],
        "Java": ["java"],
        "JavaScript": ["javascript", "js", "ecmascript", "es6"],
        "TypeScript": ["typescript"],
        "C++": ["c++"],
        "C#": ["c#"],
        "Go": ["golang"],
        "Rust": ["Rust"],
        "R": ["r programming", "rstudio", "r language"],
        "Scala": ["scala"],
        "Kotlin": ["kotlin"],
        "Swift": ["Swift"],
        "PHP": ["php"],
        "Ruby": ["Ruby"],
        "Bash/Shell": ["bash", "shell scripting", "shell script", "zsh"],
        "MATLAB": ["matlab"],
    },
    "Data & Databases": {
        "SQL": ["sql", "t-sql", "pl/sql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo db"],
        "NoSQL": ["nosql"],
        "Redis": ["redis"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
        "Snowflake": ["snowflake"],
        "BigQuery": ["bigquery"],
        "Apache Spark": ["apache spark", "pyspark", "Spark"],
        "Apache Kafka": ["kafka"],
        "Airflow": ["airflow"],
        "dbt": ["dbt"],
        "ETL": ["etl", "elt", "data pipelines", "data pipeline"],
        "Data Warehousing": ["data warehouse", "data warehousing"],
        "Hadoop": ["hadoop", "hdfs", "mapreduce"],
    },
    "Data Science & ML": {
        "Machine Learning": ["machine learning", "ml models", "predictive modeling", "predictive modelling"],
        "Deep Learning": ["deep learning", "neural networks", "neural network"],
        "NLP": ["nlp", "natural language processing", "text mining"],
        "Computer Vision": ["computer vision", "image recognition", "object detection"],
        "LLMs": ["llm", "llms", "large language models", "large language model", "generative ai", "genai"],
        "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
        "Prompt Engineering": ["prompt engineering"],
        "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
        "TensorFlow": ["tensorflow"],
        "PyTorch": ["pytorch"],
        "Keras": ["keras"],
        "Hugging Face": ["hugging face", "huggingface", "transformers library"],
        "XGBoost": ["xgboost", "lightgbm", "gradient boosting"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Statistics": ["statistics", "statistical analysis", "statistical modeling", "hypothesis testing"],
        "A/B Testing": ["a/b testing", "ab testing", "experimentation"],
        "Time Series": ["time series", "time-series", "forecasting"],
        "Feature Engineering": ["feature engineering"],
        "MLOps": ["mlops", "model deployment", "model serving", "mlflow"],
        "Data Visualization": ["data visualization", "data visualisation", "matplotlib", "seaborn", "plotly"],
        "Tableau": ["tableau"],
        "Power BI": ["power bi", "powerbi"],
        "Excel": ["Excel", "Microsoft Excel", "excel spreadsheets"],
    },
    "Web & Backend": {
        "React": ["React", "React.js", "reactjs"],
        "Angular": ["angular"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "HTML/CSS": ["html", "css", "html5", "css3"],
        "Django": ["django"],
        "Flask": ["Flask"],
        "FastAPI": ["fastapi"],
        "Spring Boot": ["spring boot", "springboot", "spring framework"],
        ".NET": [".net", "dotnet", "asp.net"],
        "REST APIs": ["rest api", "rest apis", "restful", "restful apis"],
        "GraphQL": ["graphql"],
        "Microservices": ["microservices", "microservice"],
        "Streamlit": ["streamlit"],
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "Azure": ["azure"],
        "GCP": ["gcp", "google cloud"],
        "Docker": ["docker", "containerization", "containers"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Terraform": ["terraform", "infrastructure as code", "iac"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous delivery",
                  "continuous deployment", "jenkins", "github actions", "gitlab ci"],
        "Linux": ["linux", "unix"],
        "Git": ["git", "github", "gitlab", "version control", "bitbucket"],
        "Monitoring": ["prometheus", "grafana", "datadog", "observability"],
    },
    "Engineering Practices": {
        "Data Structures & Algorithms": ["data structures", "algorithms", "dsa"],
        "System Design": ["system design", "distributed systems", "software architecture"],
        "OOP": ["object-oriented", "object oriented", "oop"],
        "Testing": ["unit testing", "unit tests", "pytest", "test automation", "tdd",
                    "integration testing", "junit"],
        "Agile/Scrum": ["agile", "scrum", "kanban", "sprint planning"],
        "Security": ["cybersecurity", "application security", "owasp", "encryption"],
        "API Design": ["api design", "api development"],
    },
    "Soft Skills": {
        "Communication": ["communication", "communicate", "presentation skills", "storytelling"],
        "Leadership": ["leadership", "led a team", "team lead", "mentoring", "mentored"],
        "Collaboration": ["collaboration", "collaborate", "cross-functional", "teamwork"],
        "Problem Solving": ["problem solving", "problem-solving", "analytical thinking", "critical thinking"],
        "Project Management": ["project management", "stakeholder management",
                               "product management", "roadmap planning"],
    },
}

# Skills whose capitalised aliases must match case-sensitively.
CASE_SENSITIVE = {"Rust", "Swift", "Ruby", "Flask", "React", "Excel", "Apache Spark"}

# Skills that should be learned first (prerequisite graph used by the roadmap)
PREREQUISITES = {
    "Pandas": ["Python"], "NumPy": ["Python"], "scikit-learn": ["Python", "Statistics"],
    "Machine Learning": ["Python", "Statistics"], "Deep Learning": ["Machine Learning"],
    "TensorFlow": ["Deep Learning"], "PyTorch": ["Deep Learning"], "Keras": ["Deep Learning"],
    "NLP": ["Machine Learning"], "Computer Vision": ["Deep Learning"],
    "LLMs": ["NLP"], "RAG": ["LLMs"], "Hugging Face": ["Deep Learning"],
    "Prompt Engineering": ["LLMs"], "XGBoost": ["Machine Learning"],
    "MLOps": ["Machine Learning", "Docker"], "Feature Engineering": ["Pandas"],
    "Time Series": ["Statistics"], "A/B Testing": ["Statistics"],
    "Apache Spark": ["Python", "SQL"], "Airflow": ["Python"], "dbt": ["SQL"],
    "Kubernetes": ["Docker"], "Terraform": ["Linux"], "CI/CD": ["Git"],
    "Django": ["Python"], "Flask": ["Python"], "FastAPI": ["Python", "REST APIs"],
    "Streamlit": ["Python"], "React": ["JavaScript", "HTML/CSS"], "Angular": ["TypeScript"],
    "Vue.js": ["JavaScript"], "Node.js": ["JavaScript"], "TypeScript": ["JavaScript"],
    "GraphQL": ["REST APIs"], "Microservices": ["REST APIs", "Docker"],
    "Snowflake": ["SQL"], "BigQuery": ["SQL"], "Data Warehousing": ["SQL"],
    "System Design": ["Data Structures & Algorithms"],
}

# Estimated hours to reach working proficiency
CATEGORY_HOURS = {
    "Programming Languages": 60, "Data & Databases": 25, "Data Science & ML": 25,
    "Web & Backend": 30, "Cloud & DevOps": 25, "Engineering Practices": 20, "Soft Skills": 10,
}
HOURS_OVERRIDE = {
    "Python": 60, "SQL": 25, "Git": 8, "Docker": 15, "Pandas": 15, "NumPy": 8,
    "Machine Learning": 50, "Deep Learning": 50, "LLMs": 25, "RAG": 15, "Statistics": 30, "NLP": 30,
    "Kubernetes": 25, "AWS": 30, "Azure": 30, "GCP": 30, "PyTorch": 25, "TensorFlow": 25, "MLOps": 25, "HTML/CSS": 20, "Excel": 12,
    "Tableau": 15, "Power BI": 15, "Streamlit": 8, "Prompt Engineering": 8,
}

# Curated official resources: skill -> list of (title, url)
RESOURCES = {
    "Python": [("Official Python Tutorial", "https://docs.python.org/3/tutorial/"),
               ("Automate the Boring Stuff (free book)", "https://automatetheboringstuff.com/")],
    "SQL": [("SQLBolt interactive lessons", "https://sqlbolt.com/"),
            ("Mode SQL Tutorial", "https://mode.com/sql-tutorial/")],
    "Pandas": [("pandas: 10 minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html")],
    "NumPy": [("NumPy: Absolute Beginners Guide", "https://numpy.org/doc/stable/user/absolute_beginners.html")],
    "scikit-learn": [("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html")],
    "Machine Learning": [("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course"),
                         ("Kaggle Learn: Intro to ML", "https://www.kaggle.com/learn/intro-to-machine-learning")],
    "Deep Learning": [("fast.ai Practical Deep Learning", "https://course.fast.ai/")],
    "PyTorch": [("PyTorch Tutorials", "https://pytorch.org/tutorials/")],
    "TensorFlow": [("TensorFlow Tutorials", "https://www.tensorflow.org/tutorials")],
    "Hugging Face": [("Hugging Face Learn", "https://huggingface.co/learn")],
    "NLP": [("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course")],
    "Docker": [("Docker Get Started", "https://docs.docker.com/get-started/")],
    "Kubernetes": [("Kubernetes Basics Tutorial", "https://kubernetes.io/docs/tutorials/kubernetes-basics/")],
    "Git": [("Pro Git Book (free)", "https://git-scm.com/book/en/v2")],
    "AWS": [("AWS Skill Builder", "https://skillbuilder.aws/")],
    "Azure": [("Microsoft Learn: Azure", "https://learn.microsoft.com/en-us/training/azure/")],
    "GCP": [("Google Cloud Skills Boost", "https://www.cloudskillsboost.google/")],
    "Terraform": [("HashiCorp Terraform Tutorials", "https://developer.hashicorp.com/terraform/tutorials")],
    "React": [("React Learn", "https://react.dev/learn")],
    "TypeScript": [("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html")],
    "JavaScript": [("javascript.info", "https://javascript.info/")],
    "Django": [("Django Official Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/")],
    "Flask": [("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/")],
    "FastAPI": [("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/")],
    "Streamlit": [("Streamlit Docs: Get Started", "https://docs.streamlit.io/get-started")],
    "Apache Spark": [("Spark Quick Start", "https://spark.apache.org/docs/latest/quick-start.html")],
    "Airflow": [("Airflow Tutorials", "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html")],
    "dbt": [("dbt Fundamentals (free)", "https://learn.getdbt.com/")],
    "Statistics": [("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability")],
    "Tableau": [("Tableau Free Training Videos", "https://www.tableau.com/learn/training")],
    "Power BI": [("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi")],
    "MLOps": [("MLflow Documentation", "https://mlflow.org/docs/latest/index.html")],
    "Linux": [("Linux Journey", "https://linuxjourney.com/")],
    "Data Structures & Algorithms": [("NeetCode Roadmap", "https://neetcode.io/roadmap")],
    "System Design": [("System Design Primer", "https://github.com/donnemartin/system-design-primer")],
    "Testing": [("pytest Getting Started", "https://docs.pytest.org/en/stable/getting-started.html")],
    "CI/CD": [("GitHub Actions Docs", "https://docs.github.com/en/actions")],
    "HTML/CSS": [("MDN Learn Web Development", "https://developer.mozilla.org/en-US/docs/Learn_web_development")],
    "Node.js": [("Node.js Learn", "https://nodejs.org/en/learn")],
    "LLMs": [("Hugging Face LLM Course", "https://huggingface.co/learn/llm-course")],
}

SKILL_CATEGORY = {s: c for c, d in SKILLS.items() for s in d}


def hours_for(skill: str) -> int:
    return HOURS_OVERRIDE.get(skill, CATEGORY_HOURS.get(SKILL_CATEGORY.get(skill, ""), 20))


def resources_for(skill: str):
    """Curated links if available, otherwise always-valid search links."""
    curated = RESOURCES.get(skill)
    if curated:
        return curated
    return [
        (f"YouTube: {skill} tutorials",
         f"https://www.youtube.com/results?search_query={quote_plus(skill + ' tutorial for beginners')}"),
        (f"Search: {skill} free course",
         f"https://www.google.com/search?q={quote_plus(skill + ' free course')}"),
    ]
