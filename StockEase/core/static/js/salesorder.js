// salesorder.js - Handles dynamic sales item add/remove, warehouse filtering, and confirmation UI

document.addEventListener('DOMContentLoaded', function() {
  // Add new sales item row
  const addBtn = document.getElementById('add-item-btn');
  if (addBtn) {
    addBtn.addEventListener('click', function() {
      // This should trigger Django formset add via AJAX or page reload in production
      // For demo, just submit the form
      document.getElementById('salesorder-form').submit();
    });
  }

  // Confirm and delete buttons for sales items
  document.querySelectorAll('.btn-confirm-item').forEach(btn => {
    btn.addEventListener('click', function() {
      this.classList.add('text-green-800');
      this.closest('.flex').classList.add('bg-green-50');
    });
  });
  document.querySelectorAll('.btn-delete-item').forEach(btn => {
    btn.addEventListener('click', function() {
      // Mark for deletion in Django formset
      const deleteInput = this.closest('.flex').querySelector('input[type="checkbox"][name$="-DELETE"]');
      if (deleteInput) {
        deleteInput.checked = true;
        this.closest('.flex').style.display = 'none';
      }
    });
  });

  // Warehouse dropdown filtering (should be handled server-side, but can be enhanced here)
  document.querySelectorAll('select[name$="-product"]').forEach(productSelect => {
    productSelect.addEventListener('change', function() {
      // Optionally, trigger AJAX to update warehouse options based on product
      // For now, submit the form to refresh options
      this.form.submit();
    });
  });
});
