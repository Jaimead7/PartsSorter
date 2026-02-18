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


import { initClassSelector, checkClassSelector } from './selectors/class.js';
import { initDateFilter, getDateQueryParameters } from './filters/date.js';
import { initExtensionFilter, getExtensionQueryParameters } from './filters/image/extension.js';
import { initOriginFilter, getOriginQueryParameters } from './filters/origin.js';
import { initModelFilter, getModelQueryParameters } from './filters/model.js';
import { initTrustFilter, getTrustQueryParameters } from './filters/image/trust.js';
import { initClassFilter, getClassQueryParameters } from './filters/class.js';
import { setImgData, initImgButtons } from './components/images.js';
import { showAlert } from './utils.js';


function getQueryParameters(index) {
    let params = [];
    params.push(getDateQueryParameters());
    params.push(getExtensionQueryParameters());
    params.push(getOriginQueryParameters());
    params.push(getModelQueryParameters());
    params.push(getTrustQueryParameters());
    params.push(getClassQueryParameters());
    // TODO: add true result filter
    // TODO: add status filter
    params.push(`index=${index}`);
    return params.filter(item => item !== '').join('&');
};

function setPaginationNumber(id, value) {
    const element = document.getElementById(id);
    if (element) {
        const defaultText = element.dataset.defaultText || '-';
        element.textContent = value || defaultText;
    }
};

function setImageInspection(data) {
    if (data.type === 'img') {
        setImgData('img0', data);
        setPaginationNumber('currentHistImgIndex', data.index + 1);
        setPaginationNumber('totalHistImgIndex', data.total);
        checkClassSelector(data.true_result);
    }
};

function clearImageInspection() {
    setImgData('img0', {});
    setPaginationNumber('currentHistImgIndex', null);
    setPaginationNumber('totalHistImgIndex', null);
    checkClassSelector(null);
};

async function getNewImageFromHist(index) {
    const endpoint = `/api/image/hist/next/?${getQueryParameters(index)}`;
    try {
        const response = await fetch(endpoint);
        if (response.status === 404) {
            showAlert('No images found.', 'warning', 2);
            clearImageInspection();
            return;
        }
        const data = await response.json();
        setImageInspection(data);
    } catch (error) {
        showAlert(`Error fetching image: ${error}`, 'danger', 2);
        clearImageInspection();
    }
};

async function initButtons() {
    document.getElementById('nextHistImgButton')?.addEventListener('click', () => {
        const indexElement = document.getElementById('currentHistImgIndex');
        let currentIndex = parseInt(indexElement.textContent) || 0;
        getNewImageFromHist(currentIndex);
    });

    document.getElementById('prevHistImgButton')?.addEventListener('click', () => {
        const indexElement = document.getElementById('currentHistImgIndex');
        let currentIndex = parseInt(indexElement.textContent) - 2 || 0;
        if (currentIndex < 0) currentIndex = 0;
        getNewImageFromHist(currentIndex);
    });

    const imageArticle = document.getElementById('img0');
    imageArticle?.querySelector('[name="deleteImgBtn"]')?.addEventListener('click', () => {
        const uuid = imageArticle.querySelector('[name="imgName"]')?.textContent;
        if (!uuid) {
            showAlert('Error getting image name', 'danger', 2);
            return;
        }

        const endpoint = `/api/image/${uuid}/`;
        let content = {
            method: 'DELETE',
            headers: {
                'accept': '*/*',
            }
        };

        fetch(endpoint, content)
        .then((response) => {
            if (response.ok) {
                showAlert('Success', 'success', 2);
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const indexElement = document.getElementById('currentHistImgIndex');
            const totalIndexElement = document.getElementById('totalHistImgIndex');
            let currentIndex = parseInt(indexElement.textContent) || 1;
            let totalIndex = parseInt(totalIndexElement.textContent) || 1;
            if (currentIndex >= totalIndex) {
                currentIndex = totalIndex - 1;
            }
            if (currentIndex < 1) {
                currentIndex = 1;
            }
            getNewImageFromHist(currentIndex - 1);
        })
        .catch((error) => {
            console.error('Error:', error);
            showAlert('Error', 'danger', 2);
        });
    });

    document.getElementById('trueResultForm')?.addEventListener('submit', (event) => {
        event.preventDefault();
        const uuid = imageArticle.querySelector('[name="imgName"]')?.textContent;
        if (!uuid) {
            showAlert('Error getting image name', 'danger', 2);
            return;
        }

        const selectedCheckbox = Array.from(
            document.querySelectorAll('input[name="classSelectorOption"]')
        ).find(checkbox => checkbox.checked);

        if (!selectedCheckbox) {
            showAlert('Select a true result', 'warning', 2);
            return;
        }

        const endpoint = `/api/image/${uuid}/true-result/`;
        let content = {
            method: 'PUT',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({true_result: selectedCheckbox.value})
        };
        if (selectedCheckbox.value === 'No result') {
            content = {
                method: 'PUT',
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            }
        }
        fetch(endpoint, content)
        .then((response) => {
            if (response.ok) {
                showAlert('Success', 'success', 2);
                const indexElement = document.getElementById('currentHistImgIndex');
                let currentIndex = parseInt(indexElement.textContent) || 0;
                getNewImageFromHist(currentIndex);
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        })
        .catch((error) => {
            showAlert(`Error: ${error}`, 'danger', 2);
        });
    });
};

document.addEventListener('DOMContentLoaded', () => {
    initClassSelector();
    initDateFilter();
    initExtensionFilter();
    initOriginFilter();
    initModelFilter();
    initTrustFilter();
    initClassFilter();
    
    initImgButtons();
    initButtons();
    getNewImageFromHist(0);
});
