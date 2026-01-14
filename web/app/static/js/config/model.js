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


import { showAlert } from '../utils.js';

const form = document.getElementById('modelForm');
const saveButton = form?.querySelector('button[type="submit"]');
const resetButton = form?.querySelector('button[type="reset"]');
const deleteButton = document.getElementById('deleteModelButton');

function get_form_as_body() {
    const description = document.getElementById('modelDescription')?.textContent;

    return {
        'description': description
    };
}

deleteButton?.addEventListener('click', () => {
    const modelName = document.getElementById('modelName')?.textContent;
    const endpoint = `/api/model/${modelName}/`;

    let content = {
        method: 'DELETE',
        headers: {
            'accept': '*/*'
        }
    };

    fetch(endpoint, content)
    .then((response) => {
        if (response.ok) {
            location.reload();
        } else {
            throw new Error(`Error on server response (${response.status})`);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        showAlert('Error deleting model: ' + error.message, 'danger', 2);
    });
});

resetButton?.addEventListener('click', (event) => {
    event.preventDefault();
    location.reload();
});

saveButton?.addEventListener('click', async function(event) {
    event.preventDefault();

    const modelName = document.getElementById('modelName')?.textContent;
    const endpoint = `/api/model/${modelName}/`;
    const spinner = document.getElementById('submitSpinner');
    const label = document.getElementById('submitLabel');

    label.innerText = 'Saving...';
    spinner.removeAttribute('hidden');
    this.disabled = true;

    let content = {
        method: 'PUT',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(get_form_as_body())
    };

    fetch(endpoint, content)
    .then((response) => {
        if (response.ok) {
            location.reload();
        } else {
            throw new Error(`Error on server response (${response.status})`);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        showAlert('Error saving model: ' + error.message, 'danger', 2);
    })
    .finally(() => {
        label.innerText = 'Save';
        spinner.setAttribute('hidden', true);
        this.disabled = false;
    });
});