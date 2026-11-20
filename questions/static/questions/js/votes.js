async function postAction(url, data) {
  const token = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const response = await fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": token, "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(data),
    credentials: "same-origin",
  });
  if (response.status === 401) {
    location.href = "/login/?next=" + encodeURIComponent(location.pathname + location.search);
    throw new Error("Войдите, чтобы продолжить.");
  }
  if (!response.ok) throw new Error("Не удалось сохранить изменение. Обновите страницу и повторите.");
  return response.json();
}

document.querySelectorAll(".votes[data-url]").forEach((widget) => {
  widget.querySelectorAll("[data-vote]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (widget.dataset.pending) return;
      widget.dataset.pending = "true";
      try {
        const result = await postAction(widget.dataset.url, { value: button.dataset.vote });
        widget.querySelector(".vote-count").textContent = result.score;
        widget.querySelectorAll("[data-vote]").forEach((option) => {
          option.setAttribute("aria-pressed", Number(option.dataset.vote) === result.vote);
        });
      } catch (error) {
        alert(error.message);
      } finally {
        delete widget.dataset.pending;
      }
    });
  });
});

document.querySelectorAll("[data-accept-url]").forEach((checkbox) => {
  checkbox.addEventListener("change", async () => {
    checkbox.disabled = true;
    try {
      const result = await postAction(checkbox.dataset.acceptUrl, { answer: checkbox.dataset.answer });
      document.querySelectorAll("[data-accept-url]").forEach((option) => {
        option.checked = Number(option.dataset.answer) === result.answer && result.accepted;
      });
    } catch (error) {
      checkbox.checked = !checkbox.checked;
      alert(error.message);
    } finally {
      checkbox.disabled = false;
    }
  });
});
