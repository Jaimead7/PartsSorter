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


async function initWarningFilter() {
    // COLLAPSE
    const collapseElement = document.getElementById('warningFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#warningFilterCollapseCard"] .bi');

    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('warningFilterSelectAll');
    const warningOptions = document.querySelectorAll('input[name="warningFilterOption"]');

    function saveWarningsOptions() {
        const selectedWarnings = Array.from(warningOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('warningFilterOptions', JSON.stringify(selectedWarnings));
    };

    function loadWarningsOptions() {
        const savedWarnings = localStorage.getItem('warningFilterOptions');

        if (savedWarnings) {
            const selectedWarnings = JSON.parse(savedWarnings);
            warningOptions.forEach((checkbox) => {
                checkbox.checked = selectedWarnings.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox?.addEventListener('change', function() {
        const isChecked = this.checked;

        warningOptions.forEach((checkbox) => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveWarningsOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(warningOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(warningOptions).some(checkbox => checkbox.checked);

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }

        saveWarningsOptions();
    };

    warningOptions.forEach((checkbox) => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadWarningsOptions();
    updateSelectAllState();
};

function getWarningQueryParameters() {
    const warningOptions = document.querySelectorAll('input[name="warningFilterOption"]');
    let warningParams = [];
    warningOptions.forEach((checkbox) => {
        if (checkbox.checked) {
            warningParams.push(`warning=${encodeURIComponent(checkbox.value)}`);
        }
    });
    return warningParams.join('&');
};


export { initWarningFilter, getWarningQueryParameters };
