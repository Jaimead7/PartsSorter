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


function initExtensionFilter() {
    // COLLAPSE
    const collapseElement = document.getElementById('imageExtensionFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#imageExtensionFilterCollapseCard"] .bi');

    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement?.addEventListener('hide.bs.collapse', () => {
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

    selectAllCheckbox?.addEventListener('change', () => {
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

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }

        saveImageExtensionsOptions();
    };

    imageExtensionOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadImageExtensionsOptions();
    updateSelectAllState();
};

function getExtensionQueryParameters() {
    const extensionOptions = document.querySelectorAll('input[name="image-extension-filter-option"]');
    let extensionParams = [];
    extensionOptions.forEach(checkbox => {
        if (checkbox.checked) {
            extensionParams.push(`extension=${encodeURIComponent(checkbox.value)}`);
        }
    });
    return extensionParams.join('&');
};
