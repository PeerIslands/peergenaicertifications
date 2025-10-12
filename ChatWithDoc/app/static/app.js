async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return await res.json();
}

async function refreshList() {
  try {
    const data = await fetchJSON('/api/pdfs');
    const ul = document.getElementById('pdfs');
    ul.innerHTML = '';
    data.sources.forEach((s) => {
      const li = document.createElement('li');
      li.textContent = s;
      const del = document.createElement('button');
      del.textContent = 'Delete';
      del.onclick = async () => {
        try {
          await fetchJSON(`/api/pdfs/${encodeURIComponent(s)}`, { method: 'DELETE' });
          await refreshList();
        } catch (e) { alert(e.message); }
      };
      li.appendChild(del);
      ul.appendChild(li);
    });
  } catch (e) {
    console.error(e);
  }
}

async function uploadFiles() {
  const input = document.getElementById('file-input');
  const status = document.getElementById('upload-status');
  const files = input.files;
  if (!files || files.length === 0) { status.textContent = 'Select PDF files first.'; return; }
  const form = new FormData();
  for (const f of files) form.append('files', f);
  status.textContent = 'Uploading...';
  try {
    await fetchJSON('/api/upload', { method: 'POST', body: form });
    status.textContent = 'Uploaded and ingested successfully.';
    input.value = '';
    await refreshList();
  } catch (e) {
    status.textContent = 'Upload failed: ' + e.message;
  }
}

async function askQuestion() {
  const q = document.getElementById('question').value.trim();
  const out = document.getElementById('answer');
  const src = document.getElementById('sources');
  if (!q) { out.textContent = 'Enter a question.'; return; }
  out.textContent = 'Thinking...';
  src.textContent = '';
  try {
    const res = await fetchJSON('/api/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q, k: 4 }) });
    out.textContent = res.answer;
    src.textContent = res.sources && res.sources.length ? 'Sources: ' + res.sources.join(', ') : '';
  } catch (e) {
    out.textContent = 'Error: ' + e.message;
  }
}

document.getElementById('upload-btn').onclick = uploadFiles;
document.getElementById('ask-btn').onclick = askQuestion;
document.querySelectorAll('.sample').forEach((btn) => {
  btn.onclick = () => {
    document.getElementById('question').value = btn.textContent;
  };
});

refreshList();


