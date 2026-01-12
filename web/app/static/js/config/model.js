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
const resetButton = form?.querySelector('button[type="reset"]');

resetButton?.addEventListener('click', function(event) {
    event.preventDefault();
    location.reload();
});

form?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    console.log('Click success');

    const modelName = document.getElementById('modelName')?.textContent;
    const endpoint = `/api/model/${modelName}`;

    let content = {
        method: 'PUT',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify()
    }

    fetch(endpoint, content)
    .then(response => {
        if (response.ok) {
            location.reload();
            showAlert('Success', 'success', 2); //CHECK
        } else {
            throw new Error('Error en la respuesta del servidor');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        location.reload();
        alert('Error al guardar los datos: ' + error.message); //CHECK
    });
});