// Basic global JS (flash auto-hide, etc.)
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  if (flashes.length) {
    setTimeout(() => {
      flashes.forEach((f) => (f.style.display = "none"));
    }, 4000);
  }
});
