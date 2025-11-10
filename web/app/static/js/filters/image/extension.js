document.addEventListener('DOMContentLoaded', function() {
    // COLLAPSE
    const collapseElement = document.getElementById('imageExtensionFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#imageExtensionFilterCollapseCard"] .bi');

    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('imageExtensionFilterSelectAll');
    const imageExtensionOptions = document.querySelectorAll('input[name="image-extension-filter-option"]');

    function saveImageExtensionsOptions() {
        const selectedImageExtensions = Array.from(imageExtensionOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('imageExtensionFilterOptions', JSON.stringify(selectedImageExtensions));
    };

    function loadImageExtensionsOptions() {
        const savedImageExtensions = localStorage.getItem('imageExtensionFilterOptions');

        if (savedImageExtensions) {
            const selectedImageExtensions = JSON.parse(savedImageExtensions);
            imageExtensionOptions.forEach(checkbox => {
                checkbox.checked = selectedImageExtensions.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;

        imageExtensionOptions.forEach(checkbox => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveImageExtensionsOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(imageExtensionOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(imageExtensionOptions).some(checkbox => checkbox.checked);

        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;

        saveImageExtensionsOptions();
    };

    imageExtensionOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadImageExtensionsOptions();
    updateSelectAllState();
});
