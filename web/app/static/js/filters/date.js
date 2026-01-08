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


const startDateFieldElement = document.getElementById('startDateFilterField');
const startDateCheckElement = document.getElementById('startDateFilterCheck');
const endDateFieldElement = document.getElementById('endDateFilterField');
const endDateCheckElement = document.getElementById('endDateFilterCheck');

function initDateFilter() {
    function saveDateOptions() {
        try {
            const options = [
                startDateCheckElement.checked,
                startDateFieldElement.value,
                endDateCheckElement.checked,
                endDateFieldElement.value
            ];
            localStorage.setItem('dateFilterOptions', JSON.stringify(options));
        } catch (error) {
            console.warn('Unable to save date to local storage.')
        }
    };

    function loadDateOptions() {
        try {
            const savedDateOptions = JSON.parse(localStorage.getItem('dateFilterOptions'));
            startDateCheckElement.checked = savedDateOptions[0];
            startDateFieldElement.value = savedDateOptions[1];
            startDateFieldElement.disabled = startDateCheckElement.checked;
            endDateCheckElement.checked = savedDateOptions[2];
            endDateFieldElement.value = savedDateOptions[3];
            endDateFieldElement.disabled = endDateCheckElement.checked;
        } catch (error) {
            startDateFieldElement.valueAsDate = new Date(new Date().setMonth(new Date().getMonth() - 1));
            endDateFieldElement.valueAsDate = new Date(new Date().setDate(new Date().getDate() + 1));
            console.warn('Unable to load dates from local storage.')
        }
        startDateFieldElement.disabled = !startDateCheckElement.checked;
        endDateFieldElement.disabled = !endDateCheckElement.checked;
    };

    if (!startDateFieldElement || !startDateCheckElement || !endDateFieldElement || !endDateCheckElement) {
        console.error("No Date Elements found.");
        return;
    }

    startDateFieldElement?.addEventListener('change', () => {
        saveDateOptions();
    });

    endDateFieldElement?.addEventListener('change', () => {
        saveDateOptions();
    });

    startDateCheckElement?.addEventListener('change', () => {
        startDateFieldElement.disabled = !startDateCheckElement.checked;
        saveDateOptions();
    });

    endDateCheckElement?.addEventListener('change', () => {
        endDateFieldElement.disabled = !endDateCheckElement.checked;
        saveDateOptions();
    });

    // COLLAPSE
    const collapseElement = document.getElementById('dateFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#dateFilterCollapseCard"] .bi');
    
    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    loadDateOptions();
};

function getDateQueryParameters() {
    if (!startDateFieldElement || !endDateFieldElement) {
        console.error("No Date Elements found.");
        return;
    }

    const start = startDateCheckElement.checked ? `start_date=${encodeURIComponent(startDateFieldElement.value)}` : '';
    const end = endDateCheckElement.checked ? `end_date=${encodeURIComponent(endDateFieldElement.value)}` : '';

    return [start, end].filter(part => part !== '').join('&');
};


export { initDateFilter, getDateQueryParameters };
