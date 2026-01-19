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


import {
    showAlert,
    askString,
    stringToParamName,
    convertInputValue
} from '../../utils.js';


function getOriginData() {
    const description = document.getElementById('originDescription')?.textContent?.trim() || null;
    const model = document.getElementById('originModel')?.value?.trim() || null;
    const params = {};

    document.querySelectorAll('#originParamsList li').forEach((item) => {
        const nameElement = item.querySelector('label[name="paramName"]');
        const valueElement = item.querySelector('input[name="paramValue"]');

        if (nameElement && valueElement) {
            const name = nameElement.textContent.trim();
            const value = convertInputValue(valueElement);
            if (name && value) {
                params[name] = value;
            }
        }
    });

    return {
        'description': description,
        'model': model,
        'params': params
    };
};

function validateNewParamName(newName) {
    const params = document.querySelectorAll('#originParamsList label[name="paramName"]');
    const duplicated = Array.from(params).some((item) => {
        return stringToParamName(item.textContent) === stringToParamName(newName);
    });
    return !duplicated;
};

function createParamInputElement(paramName) {
    const newElement = document.createElement('li');
    newElement.className = 'd-flex mb-1';

    //key input
    const keyInput = document.createElement('label');
    keyInput.className = 'input-group-text';
    keyInput.setAttribute('name', 'paramName');
    keyInput.htmlFor = `${paramName}-Value`;
    keyInput.textContent = paramName;

    //value input
    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.className = 'form-control';
    valueInput.name = 'paramValue';
    valueInput.id = `${paramName}-Value`;

    //select
    const select = document.createElement('select');
    select.className = 'input-group-text text-start';
    select.name = 'paramType';

    const optionText = document.createElement('option');
    optionText.value = 'text';
    optionText.textContent = 'Text';
    optionText.selected = true;

    const optionNumber = document.createElement('option');
    optionNumber.value = 'number';
    optionNumber.textContent = 'Number';

    select.appendChild(optionText);
    select.appendChild(optionNumber);

    select.addEventListener('change', () => {
        valueInput.type = select.value;
    });

    //div
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group';

    inputGroup.appendChild(keyInput);
    inputGroup.appendChild(valueInput);
    inputGroup.appendChild(select);

    //button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-outline-secondary border-0 pt-0 pb-0';
    deleteBtn.type = 'button';

    const iconSpan = document.createElement('span');
    iconSpan.className = 'bi bi-trash fs-3';

    deleteBtn.appendChild(iconSpan);

    deleteBtn.addEventListener('click', () => {
        newElement.remove();
    });

    newElement.appendChild(inputGroup);
    newElement.appendChild(deleteBtn);

    return newElement;
};

async function initAddParamEvent() {
    document.getElementById('addOriginParam')?.addEventListener('click', () => {
        const paramsList = document.getElementById('originParamsList');
        if (!paramsList) {
            showAlert('Internal error', 'danger', 2);
            return
        }
        let paramName = askString('Insert parameter name:');
        if (!paramName) {
            showAlert('Name needed', 'warning', 2);
            return;
        }
        paramName = stringToParamName(paramName);
        if (!validateNewParamName(paramName)) {
            showAlert('Parameter already exist', 'warning', 2);
            return;
        }
        paramsList.appendChild(createParamInputElement(paramName));
    });
};

async function initDeleteEvents() {
    document.querySelectorAll('#originParamsList li').forEach(function(item) {
        item.querySelector('button[data-action="delete"]')?.addEventListener('click', () => {
            item.remove();
        });
    });
};

async function initChangeParamTypeEvents() {
    document.querySelectorAll('#originParamsList li').forEach(function(item) {
        const typeSelect = item.querySelector('select[name="paramType"]');
        const input = item.querySelector('input[name="paramValue"]');

        if (!typeSelect || !input) return;

        typeSelect.addEventListener('change', () => {
            input.type = typeSelect.value;
        });
    });
};

export {
    getOriginData,
    validateNewParamName,
    createParamInputElement,
    initAddParamEvent,
    initDeleteEvents,
    initChangeParamTypeEvents
};
