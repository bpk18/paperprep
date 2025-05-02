
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("theme-toggle").addEventListener("click", function () {
    fetch("/toggle-theme").then(() => location.reload());
  });
});
