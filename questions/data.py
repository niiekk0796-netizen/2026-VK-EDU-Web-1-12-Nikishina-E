from datetime import date, timedelta


POPULAR_TAGS = ["django","python","html","css","bootstrap","javascript","git","docker"]
BEST_MEMBERS = ["Mr. Freeman","Dr. House","Bender","Queen Victoria","V. Pupkin"]
QUESTION_EXAMPLES = [
    ("How do I paginate a Django queryset?", "I need to split the questions into pages. How do I handle invalid page numbers?", ["django","python"], 18, 0),
    ("How do I keep the footer at the bottom?", "On short pages my footer sits under the form. How can I move it down?", ["css","bootstrap"], 12, 1),
    ("How do I share a header between templates?", "My pages use the same header. Where should I put it?", ["django","html"], 7, -1),
    ("How do I keep a search query between pages?", "The next page link clears my search.", ["django","python"], 9, 0),
    ("When should I use flexbox or grid?", "I have an avatar next to a block of text. Which layout fits better?", ["css","html"], 15, 0),
    ("How do I show a form error?", "I want to put a validation message below a Bootstrap field.", ["bootstrap","javascript"], 5, 0),
    ("How to build a moon park?", "Guys, I have trouble with a moon park. Can’t find the pieces…", ["django","git","docker"], 21, 0),
]
MOON_PARK_DETAIL = (
    "I’m trying to put together a moon park and have the site picked out. "
    "I’m still figuring out what to build first and what can wait until later. "
    "Has anyone worked on something similar?"
)
ANSWER_EXAMPLES = [
    ("Start with a small example. Set up the basic layout and check that each part works before adding the rest.", "Mr. Freeman"),
    ("Put the shared pieces in a separate file. It is easier to change them once than to update every page.", "Dr. House"),
    ("Check the page on a narrow screen before adjusting the spacing.", "Bender"),
    ("Keep a copy of your working version before changing the layout.", "Queen Victoria"),
]

QUESTIONS = {}
for index in range(7):
    for example, (title, text, tags, score, vote) in enumerate(QUESTION_EXAMPLES):
        question_id = index * len(QUESTION_EXAMPLES) + example + 1
        QUESTIONS[question_id] = {
            "id": question_id,
            "title": title,
            "text": text,
            "detail": MOON_PARK_DETAIL if example == 6 else text,
            "tags": tags,
            "score": score + index * 2,
            "vote": vote,
            "created": date(2026, 9, 1) + timedelta(days=question_id),
            "answer_count": 36,
        }


def answers_for(question):
    answers = []
    for index in range(question["answer_count"]):
        text, author = ANSWER_EXAMPLES[index % len(ANSWER_EXAMPLES)]
        answers.append(
            {
                "text": text,
                "author": author,
                "created": question["created"] + timedelta(days=1 + index // 12),
                "score": max(0, 12 - index),
                "vote": 0,
                "accepted": index == 0,
            }
        )
    return sorted(answers, key=lambda answer: (answer["score"], answer["created"]), reverse=True)
