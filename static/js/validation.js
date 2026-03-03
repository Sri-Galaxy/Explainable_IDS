const form = document.getElementById('upload-form');
const fileInput = document.getElementById('data_file');
const loader = document.getElementById('loading');

const MAX_FILE_SIZE = 5 * 1024 * 1024;  // 5MB

if (fileInput) {
    fileInput.addEventListener('change', function (e) {
        const file = this.files[0];

        if (!file) return;

        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            alert(`File size exceeds 5MB limit (${(file.size / 1024 / 1024).toFixed(2)}MB)`);
            this.value = '';
            return;
        }

        // Check file type
        if (!file.name.endsWith('.csv')) {
            alert('Please upload a CSV file');
            this.value = '';
            return;
        }
    });
}

if (form) {
    form.addEventListener('submit', function (e) {
        if (!fileInput.files[0]) {
            e.preventDefault();
            alert('Please select a file');
            return;
        }

        // Show loading
        if (loader) {
            loader.style.display = 'block';
        }

        // Disable button
        const button = form.querySelector('button');
        button.disabled = true;
        button.textContent = '⏳ Processing...';
    });
}