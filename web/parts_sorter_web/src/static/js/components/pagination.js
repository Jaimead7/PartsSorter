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


const footer = document.getElementById('pagination');

function setCurrentPage(value) {
    const element = footer.querySelector('[name="currentPage"]');
    if (element) {
        const defaultText = element.dataset.defaultText || '-';
        const text = value == null ? defaultText : value + 1;
        element.textContent = text;
    }
};

function getCurrentPage() {
    const element = footer.querySelector('[name="currentPage"]');
    const parsedValue = element ? parseInt(element.textContent, 10) : 1;
    return isNaN(parsedValue) ? 0 : parsedValue - 1;
};

function setTotalPages(value) {
    const element = footer.querySelector('[name="totalPages"]');
    if (element) {
        const defaultText = element.dataset.defaultText || '-';
        element.textContent = value || defaultText;
    }
};

function getTotalPages() {
    const element = footer.querySelector('[name="totalPages"]');
    const parsedValue = element ? parseInt(element.textContent, 10) : 0;
    return isNaN(parsedValue) ? 0 : parsedValue;
};

function setPrevPageBtnEvent(func) {
    const btn = footer?.querySelector('[name="prevPageBtn"]');
    if (btn) {
        btn.addEventListener('click', func);
    }
};

function setNextPageBtnEvent(func) {
    const btn = footer?.querySelector('[name="nextPageBtn"]');
    if (btn) {
        btn.addEventListener('click', func);
    }
};

function getResultsNumb() {
    const element = footer?.querySelector('[name="nResults"]');
    const parsedValue = element ? parseInt(element.value, 10) : 10;
    return isNaN(parsedValue) ? 0 : parsedValue
};

function setResultsNumbEvent(func) {
    const element = footer?.querySelector('[name="nResults"]');
    if (element) {
        element.addEventListener('change', func);
    }
};


export {
    setCurrentPage,
    getCurrentPage,
    setTotalPages,
    getTotalPages,
    setPrevPageBtnEvent,
    setNextPageBtnEvent,
    getResultsNumb,
    setResultsNumbEvent
};
