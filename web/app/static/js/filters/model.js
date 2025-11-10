document.addEventListener('DOMContentLoaded', function() {
    // COLLAPSE
    const collapseElement = document.getElementById('modelFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#modelFilterCollapseCard"] .bi');

    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('modelFilterSelectAll');
    const modelOptions = document.querySelectorAll('input[name="model-filter-option"]');

    function saveModelsOptions() {
        const selectedModels = Array.from(modelOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('modelFilterOptions', JSON.stringify(selectedModels));
    };

    function loadModelsOptions() {
        const savedModels = localStorage.getItem('modelFilterOptions');

        if (savedModels) {
            const selectedModels = JSON.parse(savedModels);
            modelOptions.forEach(checkbox => {
                checkbox.checked = selectedModels.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;

        modelOptions.forEach(checkbox => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveModelsOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(modelOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(modelOptions).some(checkbox => checkbox.checked);

        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;

        saveModelsOptions();
    };

    modelOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadModelsOptions();
    updateSelectAllState();
});
