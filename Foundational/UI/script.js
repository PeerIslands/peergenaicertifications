const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const fileList = document.getElementById("fileList");
const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

// --- File upload ---
dropZone.addEventListener("click", () => fileInput.click());
uploadBtn.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", handleFiles);

fileInput.addEventListener("change", (e) => handleFiles(e));

function handleFiles(e) {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;

  [...files].forEach(uploadFile);
}

async function uploadFile(file) {
  const li = document.createElement("li");
  li.textContent = `Uploading ${file.name}...`;
  fileList.appendChild(li);

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://127.0.0.1:8000/upload/", {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  li.textContent = `${file.name} ✅ Uploaded (${data.chunks_stored} chunks)`;
}

// --- Chat functionality ---
sendBtn.addEventListener("click", async () => {
  const query = userInput.value.trim();
  if (!query) return;

  addMessage("user", query);
  userInput.value = "";

  const res = await fetch("http://127.0.0.1:8000/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  const data = await res.json();
  addMessage("bot", data.response || "No response");
});

function addMessage(role, msg) {
  const chatOutput = document.getElementById("chatOutput");
  const div = document.createElement("div");

  // Convert Markdown to HTML
  const htmlContent = marked.parse(msg || "No response");

  div.innerHTML = `<b>${role}:</b><br>${htmlContent}`;
  chatOutput.appendChild(div);
  chatOutput.scrollTop = chatOutput.scrollHeight;
}
