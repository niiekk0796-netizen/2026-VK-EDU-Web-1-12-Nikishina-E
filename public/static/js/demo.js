document.querySelectorAll(".votes").forEach((widget) => {
  const buttons = [...widget.querySelectorAll("[data-vote]")];
  const score = widget.querySelector(".vote-count");
  let vote = Number(buttons.find((button) => button.getAttribute("aria-pressed") === "true")?.dataset.vote ?? 0);
  const base = Number(score.textContent) - vote;

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = Number(button.dataset.vote);
      vote = selected === vote ? 0 : selected;
      score.textContent = base + vote;
      buttons.forEach((option) => {
        option.setAttribute("aria-pressed", Number(option.dataset.vote) === vote);
      });
    });
  });
});

document.querySelectorAll("[data-demo-form]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const status = form.querySelector("[data-form-status]");
    status.textContent = "Preview only.";
    status.hidden = false;
  });
});
