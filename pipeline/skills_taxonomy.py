# Curated IT skills taxonomy
# Grouped by category for later use in gap analysis and filtering

SKILLS = {
    "languages": [
        "python", "javascript", "typescript", "java", "kotlin", "swift",
        "c++", "c#", "go", "rust", "ruby", "php", "scala", "r", "bash",
        "sql", "html", "css", "dart", "matlab"
    ],
    "frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi", "spring",
        "node.js", "express", "next.js", "nuxt", "laravel", "rails",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "ansible", "jenkins", "github actions", "ci/cd", "linux",
        "nginx", "redis", "kafka", "rabbitmq"
    ],
    "data": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "data engineering", "etl", "spark", "hadoop", "airflow",
        "tableau", "power bi", "looker", "dbt", "snowflake", "postgresql",
        "mysql", "mongodb", "elasticsearch", "sqlite"
    ],
    "practices": [
        "rest api", "graphql", "microservices", "agile", "scrum",
        "git", "tdd", "devops", "mlops", "api design"
    ]
}

# Flat list for matching
ALL_SKILLS = [skill for group in SKILLS.values() for skill in group]