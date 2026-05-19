books = [
    {
        "title": "1984",
        "summary": "O societate distopică în care statul controlează totul prin supraveghere și propagandă. Winston Smith încearcă să descopere adevărul și să lupte pentru libertate. Temele principale sunt controlul social, manipularea informației și libertatea individuală."
    },
    {
        "title": "The Hobbit",
        "summary": "Bilbo Baggins pornește într-o aventură fantastică alături de pitici pentru a recupera o comoară de la dragonul Smaug. Poveste despre curaj, prietenie și descoperirea de sine."
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "summary": "Un băiat descoperă că este vrăjitor și intră într-o lume magică. La Hogwarts învață despre prietenie, curaj și lupta dintre bine și rău."
    },
    {
        "title": "The Lord of the Rings",
        "summary": "Frodo trebuie să distrugă un inel malefic pentru a salva lumea. O poveste epică despre prietenie, sacrificiu și lupta dintre bine și rău."
    },
    {
        "title": "To Kill a Mockingbird",
        "summary": "Un roman despre justiție și rasism în sudul SUA, văzut prin ochii unei fetițe. Explorează empatia, moralitatea și inegalitatea socială."
    },
    {
        "title": "Pride and Prejudice",
        "summary": "O poveste romantică despre Elizabeth Bennet și Mr. Darcy, despre iubire, prejudecăți și evoluție personală într-o societate rigidă."
    },
    {
        "title": "The Book Thief",
        "summary": "În Germania nazistă, o fată găsește refugiu în cărți. Poveste emoționantă despre pierdere, război și puterea cuvintelor."
    },
    {
        "title": "The Alchemist",
        "summary": "Un păstor pornește într-o călătorie pentru a-și urma visul. Poveste despre destin, sensul vieții și curajul de a-ți urma drumul."
    },
    {
        "title": "Dune",
        "summary": "Pe planeta Arrakis, Paul Atreides este prins într-un conflict politic și religios. Temele sunt puterea, supraviețuirea și destinul."
    },
    {
        "title": "The Little Prince",
        "summary": "Un prinț mic explorează universul și sensul vieții. O poveste profundă despre inocență, iubire și relațiile umane."
    },
    {
        "title": "Brave New World",
        "summary": "O societate futuristă controlată prin plăcere și condiționare psihologică. Temele includ controlul social, libertatea și identitatea."
    },
    {
        "title": "Fahrenheit 451",
        "summary": "Într-o lume în care cărțile sunt interzise, pompierii le ard. Poveste despre cenzură, cunoaștere și libertatea gândirii."
    },
    {
        "title": "The Catcher in the Rye",
        "summary": "Un adolescent rătăcit caută sens și autenticitate. Temele sunt alienarea, identitatea și maturizarea."
    },
    {
        "title": "The Great Gatsby",
        "summary": "O poveste despre visul american, iubire și iluzie. Explorează bogăția, superficialitatea și dorința."
    },
    {
        "title": "Sapiens",
        "summary": "O explorare a istoriei umanității, de la origini până în prezent. Temele includ evoluția, cultura și societatea."
    },
    {
        "title": "Atomic Habits",
        "summary": "O carte despre construirea obiceiurilor bune și eliminarea celor rele. Focus pe dezvoltare personală și disciplină."
    },
    {
        "title": "Man's Search for Meaning",
        "summary": "Experiențele unui psihiatru în lagărele naziste. O reflecție profundă despre sensul vieții și reziliență."
    },
    {
        "title": "The Silent Patient",
        "summary": "Un thriller psihologic despre o femeie care încetează să mai vorbească după o crimă. Mister și psihologie profundă."
    },
    {
        "title": "It Ends With Us",
        "summary": "O poveste emoțională despre iubire și relații toxice. Explorează alegeri dificile și puterea de a merge mai departe."
    },
    {
        "title": "The Midnight Library",
        "summary": "O femeie descoperă o bibliotecă între viață și moarte unde poate trăi vieți alternative. Temele sunt regretul și sensul vieții."
    },
]

book_summaries_dict = {book["title"]: book["summary"] for book in books}


def get_summary_by_title(title: str) -> str:
    return book_summaries_dict.get(title.strip(), "Summary not found for this title.")