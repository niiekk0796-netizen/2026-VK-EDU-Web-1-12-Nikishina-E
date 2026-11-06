from datetime import date, timedelta


POPULAR_TAGS = ["django","python","html","css","bootstrap","javascript"]
BEST_MEMBERS = ["Alex Morgan","Nina Chen","Sam Rivera","Taylor Brooks"]
QUESTION_EXAMPLES = [
    ("How do I paginate a Django queryset?", "I’m building a question feed and want to keep the page links readable. How should I handle a missing or invalid page number?", ["django","python"], 18, 0),
    ("How can I keep a footer at the bottom of the viewport?", "On pages with only a short form, the footer sits halfway up the screen. Is there a simple layout that lets it move down as content grows?", ["css","bootstrap"], 12, 1),
    ("How do I share a header between Django templates?", "The question feed and account pages share the same navigation. I’d like to keep that markup in one place.", ["django","html"], 7, -1),
    ("How do I preserve a search term during pagination?", "I can filter the results with a search form, but clicking the next page clears the search.", ["django","python"], 9, 0),
    ("When should I use flexbox or grid?", "My layout has a card with an avatar, a score, and a block of text. Which tool fits that layout best?", ["css","html"], 15, 0),
    ("How do I show an error under a Bootstrap form field?", "I want to show a validation message beside the field and make it readable by a screen reader.", ["bootstrap","html"], 5, 0),
    ("Where should Django look for static files?", "I’m using app templates and a shared styles folder. Which settings control the files served in development?", ["django","css"], 21, 0),
]
PAGINATION_ANSWERS = [
    ("Use Django’s Paginator to split your queryset into pages. Catch PageNotAnInteger and EmptyPage, then return the first page when the value is invalid.", "Alex"),
    ("Give the queryset a stable ordering before paginating. Otherwise records can shift between pages when their order is undefined.", "Nina"),
    ("Use the query string for the page number and keep existing filters when you build the pagination links.", "Sam"),
    ("Check the first and last pages, along with an empty list, so you can handle every edge of the list.", "Taylor"),
]
GENERAL_ANSWERS = [
    ("Try reproducing the problem on a small page with just the affected elements. That makes it easier to identify which settings matter.", "Alex"),
    ("Check the rendered HTML and the browser console to see which resource or style is applied.", "Nina"),
    ("Include the smallest example that reproduces the problem, along with the expected and actual output.", "Sam"),
]
VARIATIONS = ("", " in a small project", " with a shared layout", " on mobile", " in development", " in a team project", " in a local preview")

QUESTIONS = {}
for index, suffix in enumerate(VARIATIONS):
    for example, (title, text, tags, score, vote) in enumerate(QUESTION_EXAMPLES):
        question_id = index * len(QUESTION_EXAMPLES) + example + 1
        QUESTIONS[question_id] = {
            "id": question_id,
            "title": title.removesuffix("?") + suffix + "?",
            "text": text,
            "tags": tags,
            "score": score + index * 2,
            "vote": vote,
            "created": date(2026, 9, 1) + timedelta(days=question_id),
            "answer_count": 36,
            "answer_examples": PAGINATION_ANSWERS if example == 0 else GENERAL_ANSWERS,
        }


def answers_for(question):
    examples = question["answer_examples"]
    answers = [
        {
            "text": examples[index % len(examples)][0],
            "author": examples[index % len(examples)][1],
            "created": question["created"] + timedelta(days=1 + index // 12),
            "score": max(0, 12 - index),
            "vote": 0,
            "accepted": index == 0,
        }
        for index in range(question["answer_count"])
    ]
    return sorted(answers, key=lambda answer: (answer["score"], answer["created"]), reverse=True)
