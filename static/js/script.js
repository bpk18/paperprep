document.getElementById('converterForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('status');
    
    if (!fileInput.files.length) {
        statusDiv.textContent = "Please select a file first";
        statusDiv.style.display = 'block';
        return;
    }

    statusDiv.textContent = "Uploading file...";
    statusDiv.style.display = 'block';

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        // Create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileInput.files[0].name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        statusDiv.textContent = "File downloaded successfully!";
    } catch (error) {
        statusDiv.textContent = "Error: " + error.message;
        console.error('Error:', error);
    }
});