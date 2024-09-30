document.addEventListener('DOMContentLoaded', function () {
    const transcriptForm = document.getElementById('transcriptForm');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const sentimentBtn = document.getElementById('sentimentBtn');
    const keywordBtn = document.getElementById('keywordBtn');
    const askQuestionForm = document.getElementById('askQuestionForm');

    if (transcriptForm) {
        transcriptForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('url').value;
            try {
                const response = await fetch('/transcript', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ url })
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('transcript').textContent = data.transcript;
                summarizeBtn.style.display = 'block';
                sentimentBtn.style.display = 'block';
                keywordBtn.style.display = 'block';
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    if (summarizeBtn) {
        summarizeBtn.addEventListener('click', async () => {
            try {
                const transcript = document.getElementById('transcript').textContent;
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ transcript })
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('summary').textContent = `Summary: ${data.summary}`;
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    if (sentimentBtn) {
        sentimentBtn.addEventListener('click', async () => {
            try {
                const transcript = document.getElementById('transcript').textContent;
                const response = await fetch('/sentiment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ transcript })
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('sentiment').textContent = `Sentiment: ${data.sentiment.label} (${(data.sentiment.score * 100).toFixed(2)}%)`;
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    if (keywordBtn) {
        keywordBtn.addEventListener('click', async () => {
            try {
                const transcript = document.getElementById('transcript').textContent;
                const response = await fetch('/keywords', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ transcript })
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('keywords').textContent = `Keywords: ${data.keywords}`;
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    if (askQuestionForm) {
        askQuestionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const transcript = document.getElementById('transcript').textContent;
            const question = document.getElementById('question').value;
            try {
                const response = await fetch('/answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ transcript, question })
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('answer').textContent = `Answer: ${data.answer}`;
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }
});
