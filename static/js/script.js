document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const formatSelect = document.getElementById('formatSelect');
    const convertBtn = document.getElementById('convertBtn');
    const statusDiv = document.getElementById('status');
    
    fileInput.addEventListener('change', async function() {
        if (!this.files.length) return;
        
        const filename = this.files[0].name;
        formatSelect.disabled = true;
        formatSelect.innerHTML = '<option value="">Loading formats...</option>';
        
        try {
            const response = await fetch('/get-formats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: filename })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            formatSelect.innerHTML = '<option value="">Select output format</option>';
            
            if (data.formats.length) {
                data.formats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format;
                    option.textContent = format.toUpperCase();
                    formatSelect.appendChild(option);
                });
                formatSelect.disabled = false;
            } else {
                formatSelect.innerHTML = `<option value="">No conversions available from ${data.original_format}</option>`;
            }
        } catch (error) {
            formatSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
            console.error('Error loading formats:', error);
        }
    });
    
    convertBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        if (!fileInput.files.length) {
            showStatus('Please select a file first', 'error');
            return;
        }
        
        if (!formatSelect.value) {
            showStatus('Please select output format', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('format', formatSelect.value);
        
        convertBtn.disabled = true;
        showStatus('Converting file...', 'info');
        
        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            showStatus('Conversion successful!', 'success');
            
            // Auto-download the file
            if (data.download_url) {
                window.location.href = data.download_url;
            }
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
            console.error('Conversion error:', error);
        } finally {
            convertBtn.disabled = false;
        }
    });
    
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `alert alert-${type}`;
        statusDiv.style.display = 'block';
        
        // Hide after 5 seconds
        if (type !== 'info') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
    }
});