function showToast(msg, timeout = 3000) {
  const container = document.getElementById("toasts");
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => {
    t.remove();
  }, timeout);
}
