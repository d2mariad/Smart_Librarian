from dotenv import load_dotenv
import chromadb
from openai import OpenAI

from books_data import books

load_dotenv()

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def build_db(force_rebuild: bool = True):
    if force_rebuild:
        try:
            chroma_client.delete_collection(name="books")
            print("Old collection deleted.")
        except Exception:
            pass

    collection = chroma_client.get_or_create_collection(name="books")

    for i, book in enumerate(books):
        text_for_embedding = f"Title: {book['title']}\nSummary: {book['summary']}"
        embedding = get_embedding(text_for_embedding)

        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[book["summary"]],
            metadatas=[{"title": book["title"]}]
        )

    print("Vector DB built successfully!")


if __name__ == "__main__":
    build_db(force_rebuild=True)