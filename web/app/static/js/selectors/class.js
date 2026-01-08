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


function initClassSelector() {
    // COLLAPSE
    const collapseElement = document.getElementById('classSelectorCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#classSelectorCollapseCard"] .bi');
    
    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });

    // SELECT ONLY ONE
    const optionCheckboxes = document.querySelectorAll('input[name="class-selector-option"]');

    optionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                optionCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                this.checked = true;
            };
        });
    });
};

function checkClassSelector(option) {
    const optionCheckboxes = document.querySelectorAll('input[name="class-selector-option"]');
    optionCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
        if (checkbox.value === option) {
            checkbox.checked = true;
        }
    });
}


export { initClassSelector, checkClassSelector };
