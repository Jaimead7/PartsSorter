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


const minElement = document.getElementById('imageTrustMinFilter');
const maxElement = document.getElementById('imageTrustMaxFilter');
const minCheck = document.getElementById('minTrustFilterCheck');
const maxCheck = document.getElementById('maxTrustFilterCheck');
const minLabel = document.getElementById('imageTrustMinFilterLabel');
const maxLabel = document.getElementById('imageTrustMaxFilterLabel');

async function initTrustFilter() {
    if (!minElement || !maxElement || !minCheck || !maxCheck || !minLabel || !maxLabel) {
        console.error('No Trust Elements found.');
        return;
    }

    // LOCAL STORAGE
    function saveImageTrustOptions() {
        const minValue = minElement.value;
        const minChecked = minCheck.checked;
        const maxValue = maxElement.value;
        const maxChecked = maxCheck.checked;
        localStorage.setItem('imageTrustFilterOptions', JSON.stringify([minChecked, minValue, maxChecked, maxValue]));
    };

    function loadImageTrustOptions() {
        const savedImageTrust = localStorage.getItem('imageTrustFilterOptions');

        if (savedImageTrust) {
            const selectedImageExtensions = JSON.parse(savedImageTrust);
            minCheck.checked = selectedImageExtensions[0];
            maxCheck.checked = selectedImageExtensions[2];
            minElement.value = selectedImageExtensions[1];
            maxElement.value = selectedImageExtensions[3];
            minLabel.textContent = `${minElement.value}%`;
            maxLabel.textContent = `${maxElement.value}%`;
        } else {
            minCheck.checked = false;
            maxCheck.checked = false;
            minElement.value = 0;
            maxElement.value = 100;
            minLabel.textContent = '0%';
            maxLabel.textContent = '100%';
        }
        minElement.disabled = !minCheck.checked;
        maxElement.disabled = !maxCheck.checked;
    };

    // CALLBACKS
    minElement.addEventListener('input', () => {
        if (parseFloat(minElement.value) > parseFloat(maxElement.value)) {
            minElement.value = maxElement.value;
        }
        saveImageTrustOptions();
        minLabel.textContent = `${minElement.value}%`;
    });

    maxElement.addEventListener('input', () => {
        if (parseFloat(maxElement.value) < parseFloat(minElement.value)) {
            maxElement.value = minElement.value;
        }
        saveImageTrustOptions();
        maxLabel.textContent = `${maxElement.value}%`;
    });

    minCheck.addEventListener('change', () => {
        minElement.disabled = !minCheck.checked;
        saveImageTrustOptions();
    });

    maxCheck.addEventListener('change', () => {
        maxElement.disabled = !maxCheck.checked;
        saveImageTrustOptions();
    });

    // COLLAPSE
    const collapseElement = document.getElementById('imageTrustFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#imageTrustFilterCollapseCard"] .bi');
    
    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    loadImageTrustOptions();
};

function getTrustQueryParameters() {
    if (!minElement || !maxElement || !minCheck || !maxCheck || !minLabel || !maxLabel) {
        console.error('No Trust Elements found.');
        return;
    }

    const minValue = minCheck.checked ? `min_trust=${parseFloat(minElement.value) / 100}` : '';
    const maxValue = maxCheck.checked ? `max_trust=${parseFloat(maxElement.value) / 100}` : '';

    return [minValue, maxValue].filter(part => part !== '').join('&');
};


export { initTrustFilter, getTrustQueryParameters };
