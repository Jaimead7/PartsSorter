document.addEventListener('DOMContentLoaded', function() {
    // COLLAPSE
    const collapseElement = document.getElementById('originFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#originFilterCollapseCard"] .bi');
    
    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('originFilterSelectAll');
    const optionCheckboxes = document.querySelectorAll('input[name="origin-filter-option"]');
    
    function updateSelectAllState() {
        const allChecked = Array.from(optionCheckboxes).every(checkbox => checkbox.checked);
        const someChecked = Array.from(optionCheckboxes).some(checkbox => checkbox.checked);
        
        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;
    }
    
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        optionCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        selectAllCheckbox.indeterminate = false;
    });

    optionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    updateSelectAllState();
});