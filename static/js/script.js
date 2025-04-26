document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const formatSelect = document.getElementById('formatSelect');
    const convertForm = document.querySelector('form');
    const convertBtn = document.querySelector('button[type="submit"]');
    
    // Create loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Preparing your document...</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
    
    // Create success modal
    const successModal = document.createElement('div');
    successModal.className = 'success-modal';
    successModal.innerHTML = `
        <div class="success-content">
            <div class="success-checkmark">
                <div class="check-icon">
                    <span class="icon-line line-tip"></span>
                    <span class="icon-line line-long"></span>
                    <div class="icon-circle"></div>
                    <div class="icon-fix"></div>
                </div>
            </div>
            <h3>Conversion Complete!</h3>
            <p>Your document is ready for download</p>
            <button class="btn btn-primary mt-3" id="downloadBtn">
                <i class="bi bi-download"></i> Download Now
            </button>
        </div>
    `;
    document.body.appendChild(successModal);
    
    // Progress elements
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    progressContainer.id = 'progressContainer';
    progressContainer.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        <small class="text-muted" id="progressText">Preparing your document...</small>
    `;
    convertForm.appendChild(progressContainer);
    
    // File input change handler
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const fileName = this.files[0].name;
            const fileExt = fileName.split('.').pop().toLowerCase();
            
            // Clear previous options
            formatSelect.innerHTML = '<option value="" selected disabled>Select output format</option>';
            
            // Get supported formats via API
            fetch('/get-output-formats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ext: fileExt })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (data.formats && data.formats.length > 0) {
                    data.formats.forEach(format => {
                        const option = document.createElement('option');
                        option.value = format;
                        option.textContent = format.toUpperCase();
                        formatSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.textContent = 'No conversions available for this file type';
                    option.disabled = true;
                    formatSelect.appendChild(option);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const option = document.createElement('option');
                option.textContent = 'Error loading formats';
                option.disabled = true;
                formatSelect.appendChild(option);
            });
        }
    });
    
    // Form submission handler
    convertForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(convertForm);
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        // Show loading state
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        
        // Simulate progress (first part)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 50) clearInterval(progressInterval);
            progressFill.style.width = `${Math.min(progress, 50)}%`;
        }, 300);
        
        try {
            const response = await fetch('/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Conversion failed');
            }
            
            // Complete progress bar animation
            let progress = 50;
            const finishInterval = setInterval(() => {
                progress += 2;
                if (progress >= 100) {
                    clearInterval(finishInterval);
                    progressText.textContent = 'Conversion complete!';
                }
                progressFill.style.width = `${progress}%`;
            }, 50);
            
            // Show success modal
            successModal.style.display = 'flex';
            document.getElementById('downloadBtn').onclick = function() {
                window.location.href = data.download_url;
                successModal.style.display = 'none';
                resetForm();
            };
            
        } catch (error) {
            // Show error message
            progressText.textContent = 'Error: ' + error.message;
            progressFill.style.backgroundColor = '#dc3545';
            
            // Re-enable form after delay
            setTimeout(() => {
                resetButton();
            }, 3000);
            
        } finally {
            clearInterval(progressInterval);
        }
    });
    
    // Close modals when clicking outside
    [loadingOverlay, successModal].forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    function resetButton() {
        convertBtn.disabled = false;
        convertBtn.innerHTML = '<i class="bi bi-magic"></i> Prepare My Document';
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
        progressFill.style.backgroundColor = '';
        progressText.textContent = 'Preparing your document...';
    }
    
    function resetForm() {
        convertForm.reset();
        formatSelect.innerHTML = '<option value="" selected disabled>Select output format</option>';
        fileInput.value = '';
        resetButton();
    }
});