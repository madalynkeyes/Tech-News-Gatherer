from pydantic import BaseModel

class Article(BaseModel):
    title: str
    link: str
    published: str
    summary: str
    source: str