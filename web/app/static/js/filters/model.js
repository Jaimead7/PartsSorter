// MIT License

// Copyright (c) 2025 Jaime Álvarez Díaz
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the “Software”), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do
// so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
// COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
// IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
// CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


function initModelFilter() {
    // COLLAPSE
    const collapseElement = document.getElementById('modelFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#modelFilterCollapseCard"] .bi');

    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement?.addEventListener('hide.bs.collapse', () => {
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

    selectAllCheckbox?.addEventListener('change', function() {
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

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }

        saveModelsOptions();
    };

    modelOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadModelsOptions();
    updateSelectAllState();
};

function getModelQueryParameters() {
    const modelOptions = document.querySelectorAll('input[name="model-filter-option"]');
    let modelParams = [];
    modelOptions.forEach(checkbox => {
        if (checkbox.checked) {
            modelParams.push(`model=${encodeURIComponent(checkbox.value)}`);
        }
    });
    return modelParams.join('&');
};


export { initModelFilter, getModelQueryParameters };
