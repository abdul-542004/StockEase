document.addEventListener('DOMContentLoaded', function () {
    const formContainer = document.getElementById('item-forms-container');
    const addBtn = document.getElementById('add-item-btn');
    const totalFormsInput = document.querySelector('input[name="items-TOTAL_FORMS"]');

    // Function to add a new form
    addBtn.addEventListener('click', function () {
        const formCount = document.querySelectorAll('.item-form').length;
        const template = document.getElementById('empty-form-template');
        let newFormHTML = template.innerHTML.replace(/__prefix__/g, formCount);

        // Insert the new form
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormHTML;
        const newForm = tempDiv.querySelector('.item-form');
        formContainer.appendChild(newForm);

        // Update TOTAL_FORMS
        totalFormsInput.value = formCount + 1;

        // Bind remove button
        bindRemoveButtons();
    });

    // Function to bind all remove buttons
    function bindRemoveButtons() {
        const removeButtons = document.querySelectorAll('.remove-item-btn');
        removeButtons.forEach(button => {
            button.removeEventListener('click', handleRemove); // Prevent double-binding
            button.addEventListener('click', handleRemove);
        });
    }

    // Function to handle removal of form
    function handleRemove(event) {
        const formItem = event.target.closest('.item-form');
        formItem.remove();

        // Reindex all forms
        reindexForms();
    }

    // Function to reindex all forms
    function reindexForms() {
        const forms = document.querySelectorAll('.item-form');
        forms.forEach((form, index) => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.name) {
                    input.name = input.name.replace(/items-\d+/, `items-${index}`);
                }
                if (input.id) {
                    input.id = input.id.replace(/items-\d+/, `items-${index}`);
                }
            });

            const labels = form.querySelectorAll('label');
            labels.forEach(label => {
                if (label.htmlFor) {
                    label.htmlFor = label.htmlFor.replace(/items-\d+/, `items-${index}`);
                }
            });
        });

        // Update TOTAL_FORMS
        totalFormsInput.value = forms.length;
    }

    // Initial binding of remove buttons
    bindRemoveButtons();
});
