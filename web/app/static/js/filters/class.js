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


function initClassFilter() {
    // COLLAPSE
    const collapseElement = document.getElementById('classFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#classFilterCollapseCard"] .bi');

    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('classFilterSelectAll');
    const classOptions = document.querySelectorAll('input[name="class-filter-option"]');

    function saveClasssOptions() {
        const selectedClasss = Array.from(classOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('classFilterOptions', JSON.stringify(selectedClasss));
    };

    function loadClasssOptions() {
        const savedClasss = localStorage.getItem('classFilterOptions');

        if (savedClasss) {
            const selectedClasss = JSON.parse(savedClasss);
            classOptions.forEach(checkbox => {
                checkbox.checked = selectedClasss.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;

        classOptions.forEach(checkbox => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveClasssOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(classOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(classOptions).some(checkbox => checkbox.checked);

        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;

        saveClasssOptions();
    };

    classOptions.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadClasssOptions();
    updateSelectAllState();
};

function getClassQueryParameters() {
    const classOptions = document.querySelectorAll('input[name="class-filter-option"]');
    let classParams = [];
    classOptions.forEach(checkbox => {
        if (checkbox.checked) {
            classParams.push(`inspection_result=${encodeURIComponent(checkbox.value)}`);
        }
    });
    return classParams.join('&');
};
