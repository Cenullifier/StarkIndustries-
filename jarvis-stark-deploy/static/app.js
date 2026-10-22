(() => {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("message");
  const messagesEl = document.getElementById("messages");
  const send = document.getElementById("send");
  const history = [];
  const clock = document.getElementById("clock");
  const state = document.getElementById("state");
  function tick() { clock.textContent = new Date().toLocaleTimeString([], { hour12: false }); }
  tick(); setInterval(tick, 1000);

  function addMessage(role, text) {
    const box = document.createElement("div");
    box.className = "message " + (role === "user" ? "user" : "jarvis");
    const label = document.createElement("b");
    label.textContent = role === "user" ? "YOU" : "J.A.R.V.I.S.";
    const body = document.createElement("p");
    body.textContent = text;
    box.append(label, body);
    messagesEl.appendChild(box);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function sendMessage(text) {
    history.push({ role: "user", content: text });
    history.splice(0, Math.max(0, history.length - 12));
    addMessage("user", text);
    input.value = "";
    send.disabled = true;
    send.textContent = "PROCESSING…";
    state.textContent = "THINKING";
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed.");
      history.push({ role: "assistant", content: data.reply });
      addMessage("assistant", data.reply);
      state.textContent = "STANDBY";
    } catch (error) {
      addMessage("assistant", "Sorry, Sir. " + (error.message || "The request failed."));
      state.textContent = "CHECK STATUS";
    } finally {
      send.disabled = false;
      send.textContent = "TRANSMIT ↗";
      input.focus();
    }
  }

  form.addEventListener("submit", event => {
    event.preventDefault();
    const text = input.value.trim();
    if (text) sendMessage(text);
  });
  document.querySelectorAll("[data-prompt]").forEach(button => {
    button.addEventListener("click", () => sendMessage(button.dataset.prompt));
  });
})();
