document.querySelectorAll("[data-demo-form]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const status = form.querySelector("[data-form-status]");
    status.textContent = "Preview only.";
    status.hidden = false;
  });
});
