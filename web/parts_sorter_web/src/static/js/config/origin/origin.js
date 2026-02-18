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
    initCollapseCard,
    enableSubmitButton,
    disableSubmitButton,
} from '../../utils.js';

import {
    getOriginData,
    initAddParamEvent,
    initDeleteEvents,
    initChangeParamTypeEvents
} from './common.js'


async function initDeleteOrigin() {
    const deleteBtn = document.getElementById('deleteOriginButton');

    if (!deleteBtn) {
        throw new Error('Couldn\'t obtain the origin delete button');
    }

    deleteBtn.addEventListener('click', () => {
        const originName = document.getElementById('originName')?.textContent;

        if (!originName) {
            showAlert('No name found', 'danger', 2);
            return;
        }

        const endpoint = `/api/origin/${originName}/`

        let content = {
            method: 'DELETE',
            headers: {
                'accept': '*/*'
            }
        };

        fetch(endpoint, content)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`${response.status} (${response.statusText})`)
            }
            window.location.replace('/config/origins/');
        })
        .catch((error) => {
            showAlert(`Error deleting origin: ${error.message}`, 'danger', 2);
        });
    });
};

async function initFormEvents() {
    const form = document.getElementById('originForm');

    if (!form) {
        throw new Error('Couldn\'t obtain the origin form');
    }

    form.querySelector('button[type="submit"]')?.addEventListener('click', async function(event) {
        event.preventDefault();

        const originName = document.getElementById('originName')?.textContent;
        if (!originName) {
            showAlert('No name found', 'danger', 2);
            return;
        }
        const endpoint = `/api/origin/${originName}/`;

        disableSubmitButton(this, 'Saving...');

        let content = {
            method: 'PUT',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(getOriginData())
        };

        fetch(endpoint, content)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`${response.status} (${response.statusText})`)
            }
            location.reload();
        })
        .catch((error) => {
            showAlert(`Error saving origin: ${error.message}`, 'danger', 2);
        })
        .finally(() => {
            enableSubmitButton(this, 'Save');
        });
    });

    form.querySelector('button[type="reset"]')?.addEventListener('click', (event) => {
        event.preventDefault();
        location.reload();
    });
};

document.addEventListener('DOMContentLoaded', () => {
    initCollapseCard('originParamsCard');
    initAddParamEvent();
    initDeleteEvents();
    initChangeParamTypeEvents();
    initFormEvents();
    initDeleteOrigin();
});
