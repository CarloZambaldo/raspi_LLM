// static/script.js
async function send() {
	const input = document.getElementById("input").value;
	const responseElem = document.getElementById("response");

	try {
		const res = await fetch('/ask', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ question: input })
		});

		if (!res.ok) throw new Error(`Server error: ${res.status}`);

		const data = await res.json();
		responseElem.textContent = data.answer || "No answer received.";
	} catch (error) {
		responseElem.textContent = `⚠️ Error: ${error.message}`;
	}
}
