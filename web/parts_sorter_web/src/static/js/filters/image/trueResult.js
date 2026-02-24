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


async function initTrueResultFilter() {
    // COLLAPSE
    const collapseElement = document.getElementById('trueResultFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#trueResultFilterCollapseCard"] .bi');

    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });

    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ALL
    const selectAllCheckbox = document.getElementById('trueResultFilterSelectAll');
    const trueResultOptions = document.querySelectorAll('input[name="trueResultFilterOption"]');

    function saveTrueResultOptions() {
        const selectedTrueResult = Array.from(trueResultOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        localStorage.setItem('trueResultFilterOptions', JSON.stringify(selectedTrueResult));
    };

    function loadTrueResultOptions() {
        const savedTrueResults = localStorage.getItem('trueResultFilterOptions');

        if (savedTrueResults) {
            const selectedTrueResults = JSON.parse(savedTrueResults);
            trueResultOptions.forEach((checkbox) => {
                checkbox.checked = selectedTrueResults.includes(checkbox.value);
            });
        }
    };

    selectAllCheckbox?.addEventListener('change', function() {
        const isChecked = this.checked;

        trueResultOptions.forEach((checkbox) => {
            checkbox.checked = isChecked;
        });

        selectAllCheckbox.indeterminate = false;

        saveTrueResultOptions();
    });

    function updateSelectAllState() {
        const allChecked = Array.from(trueResultOptions).every(checkbox => checkbox.checked);
        const someChecked = Array.from(trueResultOptions).some(checkbox => checkbox.checked);

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }

        saveTrueResultOptions();
    };

    trueResultOptions.forEach((checkbox) => {
        checkbox.addEventListener('change', updateSelectAllState);
    });

    loadTrueResultOptions();
    updateSelectAllState();
};

function getTrueResultQueryParameters() {
    const trueResultOptions = document.querySelectorAll('input[name="trueResultFilterOption"]');
    let trueResultParams = [];
    trueResultOptions.forEach((checkbox) => {
        if (checkbox.checked) {
            trueResultParams.push(`true_result=${encodeURIComponent(checkbox.value)}`);
        }
    });
    return trueResultParams.join('&');
};


export { initTrueResultFilter, getTrueResultQueryParameters };
