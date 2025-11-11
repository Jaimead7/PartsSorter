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


document.addEventListener('DOMContentLoaded', function() {
    const minElement = document.getElementById('imageTrustMinFilter');
    const maxElement = document.getElementById('imageTrustMaxFilter');
    const minLabel = document.getElementById('imageTrustMinFilterLabel');
    const maxLabel = document.getElementById('imageTrustMaxFilterLabel');

    // LOCAL STORAGE
    function saveImageTrustOptions() {
        const minValue = minElement.value;
        const maxValue = maxElement.value;
        localStorage.setItem('imageTrustFilterOptions', JSON.stringify([minValue, maxValue]));
    };

    function loadImageTrustOptions() {
        const savedImageTrust = localStorage.getItem('imageTrustFilterOptions');

        if (savedImageTrust) {
            const selectedImageExtensions = JSON.parse(savedImageTrust);
            minElement.value = selectedImageExtensions[0];
            maxElement.value = selectedImageExtensions[1];
            minLabel.textContent = `${minElement.value}%`;
            maxLabel.textContent = `${maxElement.value}%`;
        } else {
            minElement.value = 0;
            maxElement.value = 100;
            minLabel.textContent = '0%';
            maxLabel.textContent = '100%';
        }
    };

    // CALLBACKS
    minElement.addEventListener('input', function() {
        if (parseFloat(minElement.value) > parseFloat(maxElement.value)) {
            minElement.value = maxElement.value;
        }
        saveImageTrustOptions();
        minLabel.textContent = `${minElement.value}%`;
    });
    maxElement.addEventListener('input', function() {
        if (parseFloat(maxElement.value) < parseFloat(minElement.value)) {
            maxElement.value = minElement.value;
        }
        saveImageTrustOptions();
        maxLabel.textContent = `${maxElement.value}%`;
    });

    // COLLAPSE
    const collapseElement = document.getElementById('imageTrustFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#imageTrustFilterCollapseCard"] .bi');
    
    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    loadImageTrustOptions();
});
