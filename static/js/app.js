document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".notice").forEach(function (notice) {
    window.setTimeout(function () {
      notice.classList.add("notice-dismissed");
    }, 6500);
  });
});