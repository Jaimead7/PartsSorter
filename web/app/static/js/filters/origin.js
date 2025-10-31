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
    const originOptions = document.querySelectorAll('input[name="origin-filter-option"]');

    function saveOriginsOptions() {
        const selectedOrigins = Array.from(originOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('originFilterOptions', JSON.stringify(selectedOrigins));
    };

    function loadOriginsOptions() {
        const savedOrigins = localStorage.getItem('originFilterOptions');

        if (savedOrigins) {
            const selectedOrigins = JSON.parse(savedOrigins);
            originOptions.forEach(checkbox => {
                checkbox.checked = selectedOrigins.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;

        originOptions.forEach(checkbox => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveOriginsOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(originOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(originOptions).some(checkbox => checkbox.checked);

        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;

        saveOriginsOptions();
    };

    originOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadOriginsOptions();
    updateSelectAllState();
});
