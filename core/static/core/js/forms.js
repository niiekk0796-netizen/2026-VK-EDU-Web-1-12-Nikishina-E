document.querySelectorAll(".form-control").forEach((field) => {
  if (field.getAttribute("aria-invalid") === "true") field.classList.add("is-invalid");
});
