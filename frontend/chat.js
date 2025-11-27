const backendURL = "http://127.0.0.1:5000/api/query";

function addMessage(text, sender) {
  const msgBox = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.innerText = text;
  msgBox.appendChild(div);
  msgBox.scrollTop = msgBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const question = input.value.trim();

  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  const response = await fetch(backendURL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const data = await response.json();
  addMessage(data.answer, "bot");

  speakText(data.answer);
}

// 🎤 Voice input
function startVoice() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Voice recognition not supported");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    document.getElementById("userInput").value = text;
    sendMessage();
  };

  recognition.start();
}

// 🔊 Text-to-speech
function speakText(text) {
  const speech = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(speech);
}
