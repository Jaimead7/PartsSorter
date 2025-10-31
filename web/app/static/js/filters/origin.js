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
        const expirationDate = new Date();

        expirationDate.setDate(expirationDate.getDate() + 30);
        document.cookie = `originFilterOptions=${JSON.stringify(selectedOrigins)}; expires=${expirationDate.toUTCString()}; path=/`;
    };

    function loadOriginsOptions() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('originFilterOptions='));

        if (cookieValue) {
            const selectedOrigins = JSON.parse(cookieValue.split('=')[1]);
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
