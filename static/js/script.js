document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const formatSelect = document.getElementById('formatSelect');
    const convertForm = document.querySelector('form');
    const convertBtn = document.querySelector('button[type="submit"]');
    
    // Loading animation elements
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
    
    // Success animation elements
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
    // Replace the form submit event listener with this:
convertForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(convertForm);
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    // Show loading state
    convertBtn.disabled = true;
    convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    progressContainer.style.display = 'block';
    
    // Simulate progress (replace with actual progress events if available)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 90) clearInterval(progressInterval);
        progressFill.style.width = `${Math.min(progress, 90)}%`;
    }, 300);
    
    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Complete progress bar
            progressFill.style.width = '100%';
            progressText.textContent = 'Conversion complete!';
            
            // Show success modal
            successModal.style.display = 'flex';
            document.getElementById('downloadBtn').onclick = function() {
                window.location.href = data.download_url;
                successModal.style.display = 'none';
                resetForm();
            };
        } else {
            throw new Error(data.message || 'Conversion failed');
        }
    } catch (error) {
        alert(error.message);
    } finally {
        clearInterval(progressInterval);
        resetButton();
    }
});

function resetButton() {
    convertBtn.disabled = false;
    convertBtn.innerHTML = '<i class="bi bi-magic"></i> Prepare My Document';
    progressContainer.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Preparing your document...';
}

function resetForm() {
    convertForm.reset();
    formatSelect.innerHTML = '<option value="" selected disabled>Select output format</option>';
    resetButton();
}
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const fileName = this.files[0].name;
            const fileExt = fileName.split('.').pop().toLowerCase();
            
            // Clear previous options
            formatSelect.innerHTML = '<option value="" selected disabled>Select output format</option>';
            
            // Simulate API call (replace with actual fetch in production)
            setTimeout(() => {
                const formats = getSupportedFormats(fileExt);
                if (formats.length > 0) {
                    formats.forEach(format => {
                        const option = document.createElement('option');
                        option.value = format;
                        option.textContent = format.toUpperCase();
                        formatSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.textContent = 'No conversions available';
                    option.disabled = true;
                    formatSelect.appendChild(option);
                }
            }, 500);
        }
    });
    
    convertForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading animation
        loadingOverlay.style.display = 'flex';
        
        // Simulate conversion delay (replace with actual form submission)
        setTimeout(() => {
            // Hide loading animation
            loadingOverlay.style.display = 'none';
            
            // Show success animation
            successModal.style.display = 'flex';
            
            // Set up download button (in real app this would use the actual download URL)
            document.getElementById('downloadBtn').onclick = function() {
                window.location.href = "#"; // Replace with actual download URL
                successModal.style.display = 'none';
            };
        }, 2000);
    });
    
    // Close modals when clicking outside
    [loadingOverlay, successModal].forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Helper function (replace with actual API call in production)
    function getSupportedFormats(ext) {
        const formatMap = {
            'pdf': ['docx', 'txt', 'jpg', 'png'],
            'docx': ['pdf', 'txt', 'odt'],
            'jpg': ['pdf', 'png', 'webp'],
            'png': ['pdf', 'jpg', 'webp']
        };
        return formatMap[ext] || [];
    }
});