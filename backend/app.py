import json
import logging
import re

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from books_data import get_summary_by_title


load_dotenv()
logging.basicConfig(level=logging.INFO)

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="books")


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Returnează rezumatul complet pentru un titlu exact de carte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Titlul exact al cărții recomandate",
                    }
                },
                "required": ["title"],
            },
        },
    }
]


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text, 
    )
    return response.data[0].embedding

BAD_WORDS = ["prost", "idiot", "naiba", "dracu", "incapabil", "fuck"]

def contains_offensive_language(text: str) -> bool:
    lower_text = text.lower()
    return any(word in lower_text for word in BAD_WORDS)


def extract_recommended_title(response_text: str) -> str:
    if not response_text:
        return ""

    match = re.search(
        r"Titlu recomandat:\s*(.+?)(?:\n|$)",
        response_text,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip().rstrip(".,")
    return ""


def search_books(query: str, n_results: int = 3) -> dict:
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    logging.info("RAG QUERY: %s", query)
    for i, (_, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        logging.info(
            "RAG RESULT %s | title=%s | distance=%.4f",
            i,
            meta.get("title", "Unknown title"),
            dist,
        )

    return results


def build_rag_context(query: str) -> str:
    results = search_books(query, n_results=3)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    context_parts = []
    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        title = meta.get("title", "Unknown title")
        context_parts.append(
            f"Result #{idx}\n"
            f"Title: {title}\n"
            f"Distance: {dist:.4f}\n"
            f"Summary: {doc}"
        )

    return "\n\n".join(context_parts)


def handle_tool_call(tool_call) -> str:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "get_summary_by_title":
        title = arguments["title"]
        return get_summary_by_title(title)

    return "Tool not found."


def build_visual_hint(title: str, summary: str, response_text: str = "") -> str:
    text = (summary or "").lower()

    # Fantasy / magic school
    if any(term in text for term in ["vrăjitor", "vrajitor", "magie", "magică", "magica", "hogwarts"]):
        return (
            "Create an original cinematic fantasy illustration. "
            "Show three young students exploring a magical castle school for the first time. "
            "Include floating candles, glowing spell books, enchanted staircases, warm torchlight, "
            "a mysterious owl, and a strong sense of friendship, wonder, and adventure. "
            "The scene should feel youthful, magical, emotionally rich, and visually striking. "
            "Do not reference copyrighted names, franchise names, actor likenesses, or exact movie costumes. "
            "No text, no typography, no title, no author name, no book cover layout. "
            "Full scene visible, centered composition, safe margins, no cropped faces, no cropped bodies."
        )

    # Self-improvement / productivity
    if any(term in text for term in ["obiceiuri", "disciplină", "disciplina", "dezvoltare personală", "dezvoltare personala"]):
        return (
            "Create an elegant conceptual editorial illustration about personal growth and habit building. "
            "Show one person improving daily routines through small, consistent actions, with subtle visual metaphors "
            "for progress, discipline, focus, and transformation. "
            "Warm natural light, clean composition, refined details, calm but inspiring mood. "
            "No text, no typography, no title, no author name, no book cover layout."
        )

    # Dystopian / surveillance
    if any(term in text for term in ["supraveghere", "propagandă", "propaganda", "control social", "distopic"]):
        return (
            "Create a dark cinematic dystopian illustration. "
            "Show a solitary figure in a city dominated by surveillance, giant screens, oppressive architecture, "
            "cold light, and subtle psychological tension. "
            "Visually striking, dramatic, atmospheric, and emotionally powerful. "
            "No text, no typography, no title, no author name, no poster layout."
        )

    # Epic fantasy / adventure
    if any(term in text for term in ["inel", "pitici", "dragon", "aventură fantastică", "aventura fantastica"]):
        return (
            "Create an original epic fantasy illustration. "
            "Show a brave young adventurer and loyal companions crossing a dramatic mythical landscape, "
            "with mountains, ancient ruins, warm firelight, danger, wonder, and friendship. "
            "Highly cinematic, rich in detail, emotionally memorable, and visually grand. "
            "No text, no typography, no title, no author name, no book cover layout."
        )

    # War / historical emotional
    if any(term in text for term in ["război", "razboi", "germania nazistă", "germania nazista"]):
        return (
            "Create an emotional cinematic historical illustration. "
            "Show a young reader finding hope in books during a time of war, with dim interiors, soft window light, "
            "muted colors, fragile atmosphere, and emotional depth. "
            "Visually rich, intimate, and moving. "
            "No text, no typography, no title, no author name, no book cover layout."
        )

    # Sci-fi / desert prophecy
    if any(term in text for term in ["arrakis", "planetă", "planeta", "deşert", "desert", "politic", "religios"]):
        return (
            "Create an original epic science-fiction illustration. "
            "Show a lone young hero on a vast desert world with monumental dunes, dramatic sky, distant futuristic structures, "
            "mystical atmosphere, and a feeling of destiny. "
            "Cinematic scale, rich detail, powerful composition. "
            "No text, no typography, no title, no author name, no poster layout."
        )

    # Romantic classic
    if any(term in text for term in ["iubire", "prejudecăți", "prejudecati", "societate rigidă", "societate rigida"]):
        return (
            "Create an elegant cinematic historical romance illustration. "
            "Show two refined characters in a countryside estate setting, with soft golden light, garden atmosphere, "
            "quiet emotional tension, and graceful period details. "
            "Beautiful, warm, refined, and visually rich. "
            "No text, no typography, no title, no author name, no book cover layout."
        )

    # Fallback specific, dar general
    return (
        f"Create a cinematic story-specific illustration inspired by these themes: {summary}. "
        "Show a distinctive setting, strong atmosphere, emotionally meaningful characters, and a visually memorable scene. "
        "Make it feel rich, polished, and story-driven, not generic. "
        "No text, no typography, no title, no author name, no book cover layout."
    )

def ask_smart_librarian(user_input: str) -> dict:
    rag_context = build_rag_context(user_input)

    messages = [
        {
            "role": "system",
            "content": (
                "Ești Smart Librarian, un asistent care recomandă o singură carte pe baza contextului RAG.\n"
                "Reguli:\n"
                "- Răspunde în limba utilizatorului.\n"
                "- Alege o singură carte doar din contextul RAG.\n"
                "- Nu inventa titluri.\n"
                "- Începe răspunsul exact cu: Titlu recomandat: <titlul exact>\n"
                "- După aceea scrie:\n"
                "Motiv: ...\n"
                "Rezumat: ...\n"
                "- Dacă folosești tool-ul, trebuie să trimiți titlul exact din context."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Cererea utilizatorului: {user_input}\n\n"
                f"Context RAG:\n{rag_context}\n\n"
                "Alege cea mai potrivită carte și folosește tool-ul pentru a obține rezumatul complet."
            ),
        },
    ]

    first_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = first_response.choices[0].message

    if assistant_message.tool_calls:
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_result = handle_tool_call(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        final_text = final_response.choices[0].message.content or ""
    else:
        final_text = assistant_message.content or ""

    title = extract_recommended_title(final_text)
    summary = get_summary_by_title(title)
    visual_hint = build_visual_hint(title, summary, final_text)

    return {
        "response": final_text,
        "title": title,
        "visual_hint": visual_hint,
    }


if __name__ == "__main__":
    print("Smart Librarian started. Scrie 'exit' pentru a ieși.\n")

    while True:
        user_input = input("Tu: ")

        if user_input.lower() in ["exit", "quit", "iesire", "pa", "la revedere"]:
            print("La revedere!")
            break

        if contains_offensive_language(user_input):
            print("\nSmart Librarian: Te rog să formulezi întrebarea într-un mod respectuos.\n")
            continue

        result = ask_smart_librarian(user_input)
        print(f"\nSmart Librarian: {result['response']}\n")
        print(f"Titlu detectat: {result['title']}")
        print(f"Visual hint: {result['visual_hint']}\n")