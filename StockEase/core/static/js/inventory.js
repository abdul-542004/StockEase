// Sleek inventory page search and filter UX
// Handles instant search and warehouse dropdown change

document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('input[name="q"]');
  const warehouseSelect = document.getElementById('warehouse-select');

  // Submit form on warehouse change
  if (warehouseSelect) {
    warehouseSelect.addEventListener('change', function() {
      this.form.submit();
    });
  }

  // Instant search on input (optional: debounce for large datasets)
  if (searchInput) {
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        this.form.submit();
      }
    });
  }
});
