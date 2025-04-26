document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const formatSelect = document.getElementById('formatSelect');
    const convertBtn = document.getElementById('convertBtn');
    const statusDiv = document.getElementById('status');
    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.getElementById('progressContainer');
    const converterForm = document.getElementById('converterForm');
    
    // File selection handler
    fileInput.addEventListener('change', async function() {
        resetUI();
        
        if (!this.files || !this.files.length) return;
        
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
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            formatSelect.innerHTML = '<option value="">Select output format</option>';
            
            if (data.formats && data.formats.length) {
                data.formats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format;
                    option.textContent = format.toUpperCase();
                    formatSelect.appendChild(option);
                });
                formatSelect.disabled = false;
            } else {
                formatSelect.innerHTML = `<option value="">No conversions from ${data.original_format}</option>`;
            }
        } catch (error) {
            console.error('Error:', error);
            showStatus(`Error: ${error.message}`, 'danger');
            formatSelect.innerHTML = '<option value="">Error loading formats</option>';
        }
    });
    
    // Form submission handler
    converterForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!fileInput.files || !fileInput.files.length) {
            showStatus('Please select a file first', 'danger');
            return;
        }
        
        if (!formatSelect.value) {
            showStatus('Please select output format', 'danger');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('format', formatSelect.value);
        
        // UI updates
        convertBtn.disabled = true;
        showStatus('Converting file...', 'info');
        progressContainer.style.display = 'block';
        updateProgress(10);
        
        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Simulate progress
            updateProgress(50);
            
            // Wait a moment before download to show progress
            setTimeout(() => {
                updateProgress(100);
                showStatus('Conversion successful! Download starting...', 'success');
                
                // Trigger download
                if (data.download_url) {
                    const link = document.createElement('a');
                    link.href = data.download_url;
                    link.download = data.filename || 'converted_file';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                
                // Reset after 3 seconds
                setTimeout(resetUI, 3000);
            }, 1000);
            
        } catch (error) {
            console.error('Conversion error:', error);
            showStatus(`Error: ${error.message}`, 'danger');
            resetUI();
        }
    });
    
    // Helper functions
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `alert alert-${type}`;
        statusDiv.style.display = 'block';
    }
    
    function updateProgress(percent) {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = `${percent}%`;
    }
    
    function resetUI() {
        convertBtn.disabled = false;
        progressContainer.style.display = 'none';
        updateProgress(0);
        // Don't hide status immediately - let user see success/error
    }
});