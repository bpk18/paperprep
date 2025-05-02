
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("theme-toggle");
  toggle.addEventListener("click", () => {
    fetch("/toggle-theme").then(() => location.reload());
  });
});
