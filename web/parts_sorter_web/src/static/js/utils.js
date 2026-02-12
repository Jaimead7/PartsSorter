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


async function showAlert(message, type, seconds) {
    switch (type) {
        case 'warning':
            console.warn(message);
            break;
        case 'danger':
            console.error(message);
            break;
        case 'success':
            console.info(message);
            break;
        default:
            console.log(message);
    };

    const alertBlock = document.createElement('div');
    alertBlock.className = `alert alert-${type} fade show position-fixed m-1 start-50 translate-middle-x text-truncate`;
    alertBlock.style.cssText = 'top:4rem; z-index: 9999;';
    alertBlock.textContent = message;
    document.getElementById('main-content').appendChild(alertBlock);
    setTimeout(() => {
        if (alertBlock?.parentNode) {
            alertBlock.remove();
        }
    }, seconds * 1000);
};

async function initCollapseCard(elementName) {
    const collapseElement = document.getElementById(elementName);
    const buttonIcon = collapseElement.querySelector(`button[data-bs-toggle="collapse"] .bi`);

    collapseElement?.addEventListener('show.bs.collapse', () => {
        buttonIcon?.classList.remove('bi-caret-down-square');
        buttonIcon?.classList.add('bi-caret-up-square');
    });

    collapseElement?.addEventListener('hide.bs.collapse', () => {
        buttonIcon?.classList.remove('bi-caret-up-square');
        buttonIcon?.classList.add('bi-caret-down-square');
    });
};

function askString(question) {
    const value = prompt(question);
    if (!value) return;
    if (value.trim() === '') return;
    return value;
};

async function disableSubmitButton(button, text = null) {
    const spinner = button.querySelector('span[name="submitSpinner"]');
    const label = button.querySelector('span[name="submitLabel"]');

    if (text && label) {
        label.textContent = text;
    }
    spinner?.removeAttribute('hidden');
    button.disabled = true;
};

async function enableSubmitButton(button, text = null) {
    const spinner = button.querySelector('span[name="submitSpinner"]');
    const label = button.querySelector('span[name="submitLabel"]');

    if (text && label) {
        label.textContent = text;
    }
    spinner?.setAttribute('hidden', true);
    button.disabled = false;
};

function stringToParamName(param) {
    return param.trim().toLocaleLowerCase().replace(' ', '_');
};

function convertInputValue(element) {
    const type = element.getAttribute('type') || 'text';
    switch (type.toLocaleLowerCase()) {
        case 'number':
        case 'number':
            const num = parseFloat(element.value);
            return isNaN(element.value) ? element.value.trim() : num;
        case 'checkbox':
        case 'radio':
            return element.checked;
        default:
            return element.value.trim();
    }
};

export {
    showAlert,
    initCollapseCard,
    askString,
    disableSubmitButton,
    enableSubmitButton,
    stringToParamName,
    convertInputValue
};
