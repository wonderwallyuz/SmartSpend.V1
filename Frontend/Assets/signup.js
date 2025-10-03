// Redirect buttons to external OAuth pages
document.getElementById("googleBtn").addEventListener("click", () => {
  window.location.href = "https://accounts.google.com/signup";
});

document.getElementById("facebookBtn").addEventListener("click", () => {
  window.location.href = "https://www.facebook.com/r.php";
});

document.getElementById("githubBtn").addEventListener("click", () => {
  window.location.href = "https://github.com/signup";
});
