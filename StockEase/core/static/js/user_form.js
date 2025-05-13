// filepath: e:\StockEase - Inventory Management System\StockEase\core\static\js\user_form.js
// Toggle password help text on focus/blur for password fields

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('user-form');
    if (!form) return;

    // Find all password fields
    const passwordFields = form.querySelectorAll('input[type="password"]');
    passwordFields.forEach(function (input) {
        input.addEventListener('focus', function () {
            // Show help text for this field
            let help = input.parentElement.querySelector('.password-help');
            if (help) help.style.display = 'block';
        });
        input.addEventListener('blur', function () {
            // Hide help text for this field
            let help = input.parentElement.querySelector('.password-help');
            if (help) help.style.display = 'none';
        });
    });
});
