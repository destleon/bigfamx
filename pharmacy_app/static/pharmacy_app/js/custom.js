// Handle view shops button click
document.addEventListener('DOMContentLoaded', function() {
    const viewShopsBtn = document.getElementById('viewShopsBtn');
    const shopsContainer = document.getElementById('shopsContainer');
    
    if (viewShopsBtn && shopsContainer) {
        viewShopsBtn.addEventListener('click', function() {
            shopsContainer.classList.toggle('show');
            viewShopsBtn.textContent = shopsContainer.classList.contains('show') ? 
                'Hide Shops' : 'View Shops';
        });
    }
});