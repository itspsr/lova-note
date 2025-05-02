document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    document.getElementById("progressBarContainer").style.display = "block";

    const response = await fetch("/upload", {
        method: "POST",
        body: formData,
    });

    const data = await response.json();

    document.getElementById("transcriptionText").innerText = data.text;
    document.getElementById("duration").innerText = data.duration;
    document.getElementById("language").innerText = data.language;

    // Auto-scroll
    document.getElementById("result").scrollIntoView({ behavior: 'smooth' });
});
