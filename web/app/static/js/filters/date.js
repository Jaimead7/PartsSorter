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


function initDateFilter() {
    // SET DATE
    document.getElementById('startDateFilter').valueAsDate = new Date(new Date().setMonth(new Date().getMonth() - 1));
    document.getElementById('endDateFilter').valueAsDate = new Date();

    // COLLAPSE
    const collapseElement = document.getElementById('dateFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#dateFilterCollapseCard"] .bi');
    
    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });
};

function getDateQueryParameters() {
    const startDateElement = document.getElementById('startDateFilter');
    const endDateElement = document.getElementById('endDateFilter');
    return `start_date=${encodeURIComponent(startDateElement.value)}&end_date=${encodeURIComponent(endDateElement.value)}`;
};
