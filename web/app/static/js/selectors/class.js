document.addEventListener('DOMContentLoaded', function() {
    // COLLAPSE
    const collapseElement = document.getElementById('classSelectorCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#classSelectorCollapseCard"] .bi');
    
    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const optionCheckboxes = document.querySelectorAll('input[name="class-selector-option"]');

    optionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                optionCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                this.checked = true;
            };
        });
    });
});