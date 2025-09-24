CORE_SKILLS = {
    "software": [
        "python","java","c++","sql","javascript","typescript","react","node","fastapi","flask",
        "docker","kubernetes","aws","gcp","azure","terraform","linux","git","ci","cd"
    ],
    "data": [
        "pandas","numpy","scikit-learn","tensorflow","pytorch","nlp","etl","airflow","dbt","spark"
    ]
}

ALL_SKILLS = sorted({s.lower() for v in CORE_SKILLS.values() for s in v})
