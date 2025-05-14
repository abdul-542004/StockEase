
document.addEventListener('DOMContentLoaded', function () {
    const addItemButton = document.getElementById('add-item-btn');
    const formsContainer = document.getElementById('item-forms-container');
    const emptyFormTemplate = document.getElementById('empty-form-template').innerHTML;
    const totalFormsInput = document.querySelector('input[name="items-TOTAL_FORMS"]');
    const initialFormsInput = document.querySelector('input[name="items-INITIAL_FORMS"]'); // Keep track of initial forms
    const maxFormsInput = document.querySelector('input[name="items-MAX_NUM_FORMS"]');

    // Removed redundant formCount variable, will use totalFormsInput.value directly

    addItemButton.addEventListener('click', function () {
        let currentTotalForms = parseInt(totalFormsInput.value);
        if (maxFormsInput && currentTotalForms >= parseInt(maxFormsInput.value)) {
            alert("Maximum number of items reached.");
            return;
        }
        
        // New form gets index = currentTotalForms (e.g., if 1 form exists, index is 1 for the 2nd form)
        let newFormHtml = emptyFormTemplate.replace(/__prefix__/g, currentTotalForms);
        formsContainer.insertAdjacentHTML('beforeend', newFormHtml);
        totalFormsInput.value = currentTotalForms + 1; // Increment TOTAL_FORMS

        initializeRemoveButtons(); // Initialize remove buttons for the new form
    });

    function initializeRemoveButtons() {
        formsContainer.querySelectorAll('.remove-item-btn').forEach(button => {
            // Clone and replace to ensure only one event listener is attached
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);

            newButton.addEventListener('click', function(event) {
                event.preventDefault();
                const formToRemove = newButton.closest('.item-form');
                if (formToRemove) {
                    const deleteInput = formToRemove.querySelector('input[type="checkbox"][name$="-DELETE"]');
                    if (deleteInput) { // This is an existing form (has a DELETE checkbox)
                        deleteInput.checked = true;
                        formToRemove.style.display = 'none'; // Hide it
                        // TOTAL_FORMS is not decremented here by JS; Django handles deletion of initial forms.
                    } else { // This is a new form (added via JS, no DELETE checkbox yet)
                        formToRemove.remove();
                        
                        // Decrement TOTAL_FORMS count
                        totalFormsInput.value = parseInt(totalFormsInput.value) - 1;

                        // Re-index all remaining forms to be sequential 0, 1, 2...
                        let newIndex = 0;
                        formsContainer.querySelectorAll('.item-form').forEach(itemForm => {
                            // Update all form fields (inputs, selects, textareas) and labels within this itemForm
                            itemForm.querySelectorAll('input, select, textarea, label').forEach(element => {
                                // Update attributes that contain the form index
                                ['name', 'id', 'for'].forEach(attrName => {
                                    const attrValue = element.getAttribute(attrName);
                                    if (attrValue) {
                                        // Regex to find items-NUMBER- and replace NUMBER with newIndex
                                        // Example: items-2-product -> items-0-product if newIndex is 0
                                        element.setAttribute(attrName, attrValue.replace(/-(\d+)-/g, `-${newIndex}-`));
                                    }
                                });
                            });
                            newIndex++;
                        });
                    }
                }
            });
        });
    }
    
    initializeRemoveButtons(); // Initialize for existing forms on page load
});
