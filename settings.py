import os


class Settings:
    project_name = "Db lab 3"
    description = "Project for db lab 3"
    version = "1.0.0"
    docs_url = "/docs"
    host = "0.0.0.0"
    port = 8000
    database_class = None


settings = Settings()

if "PROJECT_NAME" in os.environ:
    settings.project_name = os.environ["PROJECT_NAME"]

if "API_VERSION" in os.environ:
    settings.version = os.environ["API_VERSION"]

if "API_DESCRIPTION" in os.environ:
    settings.description = os.environ["API_DESCRIPTION"]

if "OPENAPI_URL" in os.environ:
    settings.openapi_url = os.environ["OPENAPI_URL"]

if "DOCS_URL" in os.environ:
    settings.docs_url = os.environ["DOCS_URL"]

if "API_HOST" in os.environ:
    settings.host = os.environ["API_HOST"]

if "API_PORT" in os.environ:
    settings.port = int(os.environ["API_PORT"])

if "API_CORS_ORIGINS" in os.environ:
    settings.origins = os.environ["API_CORS_ORIGINS"].split(",")

if "DATABASE_CLASS" in os.environ:
    settings.database_class = os.environ["DATABASE_CLASS"]
