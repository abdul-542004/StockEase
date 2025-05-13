// Product search/filter for product_list.html
// Filters table rows by product name as user types or clicks the search button

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('product-search');
    const searchBtn = document.getElementById('product-search-btn');
    const table = document.getElementById('product-table');
    if (!searchInput || !table) return;

    function filterProducts() {
        const filter = searchInput.value.trim().toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        let anyVisible = false;
        rows.forEach(row => {
            const nameCell = row.querySelector('.product-name');
            if (!nameCell) return;
            const name = nameCell.textContent.trim().toLowerCase();
            if (name.includes(filter)) {
                row.style.display = '';
                anyVisible = true;
            } else {
                row.style.display = 'none';
            }
        });
        // Show/hide 'No products found' row
        const emptyRow = table.querySelector('tbody tr td[colspan]');
        if (emptyRow) {
            emptyRow.parentElement.style.display = anyVisible ? 'none' : '';
        }
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', filterProducts);
    }
});
