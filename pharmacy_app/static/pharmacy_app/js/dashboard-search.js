document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('medicine-search');
    const searchResults = document.getElementById('search-results');
    let searchTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value;
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/search-medicines/?query=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    searchResults.innerHTML = '';
                    if (data.medicines.length > 0) {
                        searchResults.style.display = 'block';
                        data.medicines.forEach(medicine => {
                            const div = document.createElement('div');
                            div.className = 'search-result-item';
                            div.innerHTML = `
                                <div class="d-flex justify-content-between align-items-center">
                                    <span>${medicine.name} - $${medicine.price}</span>
                                    <a href="/enter-sale/${medicine.id}/" class="btn btn-primary btn-sm">Enter Sale</a>
                                </div>
                            `;
                            searchResults.appendChild(div);
                        });
                    } else {
                        searchResults.innerHTML = '<div class="search-result-item">No medicines found</div>';
                        searchResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    searchResults.innerHTML = '<div class="search-result-item">Error searching for medicines</div>';
                    searchResults.style.display = 'block';
                });
        }, 300);
    });

    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.style.display = 'none';
        }
    });
});