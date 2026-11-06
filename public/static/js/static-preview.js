const questionData = document.getElementById("preview-questions");

if (questionData) {
  const questions = JSON.parse(questionData.textContent);
  const id = Number(new URLSearchParams(location.search).get("id"));
  if (Number.isInteger(id) && id > 1 && id <= questions.length) {
    const [title, text, tags, score, vote] = questions[id - 1];
    const question = document.getElementById("preview-question");
    question.querySelector("h1").textContent = title;
    question.querySelector(".post-text").textContent = text;
    question.querySelector(".vote-count").textContent = score;
    question.querySelectorAll("[data-vote]").forEach((button) => {
      button.setAttribute("aria-pressed", Number(button.dataset.vote) === vote);
    });
    const day = 24 + id;
    const time = question.querySelector("time");
    time.dateTime = "2026-10-" + day;
    time.textContent = "Oct " + day + ", 2026";
    const tagLinks = question.querySelector(".tags");
    tagLinks.replaceChildren(...tags.map((tag) => {
      const link = document.createElement("a");
      link.className = "tag";
      link.href = "tag.html?tag=" + encodeURIComponent(tag);
      link.textContent = tag;
      return link;
    }));
    document.title = title + " · Message.Me";
  }
}

const list = document.querySelector("[data-preview-list]");

if (list) {
  const parameters = new URLSearchParams(location.search);
  const tag = parameters.get("tag");
  const query = parameters.get("q")?.trim().toLowerCase();
  const posts = [...list.querySelectorAll(".post-card")];
  const visible = posts.filter((post) =>
    (!tag || [...post.querySelectorAll(".tag")].some((link) => link.textContent === tag)) &&
    (!query || post.textContent.toLowerCase().includes(query))
  );
  const pageSize = Number(list.dataset.previewList);
  const pages = Math.max(1, Math.ceil(visible.length / pageSize));
  const requested = Number(parameters.get("page"));
  const page = Number.isInteger(requested) && requested >= 1 && requested <= pages ? requested : 1;
  const start = (page - 1) * pageSize;
  const pagePosts = new Set(visible.slice(start, start + pageSize));

  posts.forEach((post) => { post.hidden = !pagePosts.has(post); });
  if (tag) document.querySelector("h1").textContent = "Tag: " + tag;
  if (query) document.querySelector(".search").value = parameters.get("q");
  const empty = document.querySelector("[data-empty]");
  if (empty) empty.hidden = visible.length > 0;

  const pagination = document.querySelector(".pagination");
  pagination.replaceChildren();
  for (let number = 1; number <= pages && pages > 1; number += 1) {
    const item = document.createElement("li");
    item.className = "page-item";
    const link = document.createElement("a");
    link.className = "page-link";
    parameters.set("page", number);
    link.href = "?" + parameters.toString();
    link.textContent = number;
    if (number === page) {
      item.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
    item.append(link);
    pagination.append(item);
  }
}
