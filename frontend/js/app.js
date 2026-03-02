async function summarize(id) {
  const res = await fetch(`http://127.0.0.1:8000/summarize?video_id=${encodeURIComponent(id)}`);
  const data = await res.json();
  document.getElementById(`sum_${id}`).innerText = data.summary || data.error || "No summary available.";
}

async function search() {
  const q = document.getElementById("searchBox").value;
  const res = await fetch(`http://127.0.0.1:8000/search?query=${encodeURIComponent(q)}`);
  const data = await res.json();

  const container = document.getElementById("results");
  container.innerHTML = "";

  if (!data.results) {
    container.innerHTML = `<p style="color:red;">${data.error}</p>`;
    return;
  }

  data.results.forEach(v => {
    container.innerHTML += `
      <div class="card">
        <h3>${v.title}</h3>
        <p>${v.channel_name}</p>
        <button onclick="summarize('${v.video_id}')">Summarize</button>
        <p id="sum_${v.video_id}"></p>
      </div>`;
  });
}
