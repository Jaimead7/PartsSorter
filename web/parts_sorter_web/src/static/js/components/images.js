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


import { toSnakeCase } from '../utils.js';


function formatTrust(value) {
    if (typeof value === 'number') {
        return (value * 100).toFixed(2) + '%';
    }
    if (typeof value === 'string') {
        return value;
    }
    return null;
};

function resolveURL(url) {
    if (url.startsWith('/api/')) return url;
    if (url.startsWith('/')) return '/api' + url;
    return '/api/' + url;
};

//TODO: Use custom classes for status style
function getBorderClassesFromData(imgData) {
    if (!imgData || !imgData.status) return ['border-4'];

    const status = toSnakeCase(imgData.status);
    switch (status) {
        case 'captured':
            return ['border-4'];
        case 'transition_push':
            return ['border-4', 'border-warning'];
        case 'transition_pass':
            return ['border-4', 'border-info'];
        case 'actuator_push':
            return ['border-4', 'border-warning'];
        case 'actuator_pass':
            return ['border-4', 'border-info'];
        case 'pushed':
            return ['border-4', 'border-success'];
        case 'passed':
            return ['border-4', 'border-success'];
        case 'error_overwrite':
            return ['border-4', 'border-danger'];
        case 'error_lost':
            return ['border-4', 'border-danger'];
        case 'error_skipped':
            return ['border-4', 'border-danger'];
        default:
            return ['border-4'];
    }
};

function setBorderClasses(element, borderClasses) {
    if (!element || !Array.isArray(borderClasses)) return;

    Array.from(element.classList)
        .filter(c => c.startsWith('border-'))
        .forEach(c => element.classList.remove(c));

    borderClasses
        .filter(c => c.startsWith('border-'))
        .forEach(c => element.classList.add(c));
};

function getImgData(imgId) {
    const article = document.getElementById(imgId);

    const img = article?.querySelector('[name="img"]');
    const id = article?.querySelector('[name="imgName"]');
    const origin = article?.querySelector('[name="imgOrigin"]');
    const insp_result = article?.querySelector('[name="imgType"]');
    const trust = article?.querySelector('[name="imgTrust"]');
    const model = article?.querySelector('[name="imgModel"]');
    const status = article?.querySelector('[name="imgStatus"]');

    return {
        url: img && img.hasAttribute('src') ? img.getAttribute('src') : '',
        id: id ? id.textContent : 'Unknown',
        origin: origin ? origin.textContent : 'Unknown',
        insp_result: insp_result ? insp_result.textContent : 'No result',
        trust: trust ? trust.textContent : '0.00%',
        model: model ? model.textContent : 'Unknown',
        status: status ? status.textContent : 'Unknown'
    };
};

function setImgData(imgId, imgData) {
    const article = document.getElementById(imgId);
    if (!article) return;

    const imgSection = article.querySelector('[name="imgSection"]');
    const img = article.querySelector('[name="img"]');
    const alt = article.querySelector('[name="imgAlt"]');
    const id = article.querySelector('[name="imgName"]');
    const origin = article.querySelector('[name="imgOrigin"]');
    const insp_result = article.querySelector('[name="imgType"]');
    const trust = article.querySelector('[name="imgTrust"]');
    const model = article.querySelector('[name="imgModel"]');
    const status = article.querySelector('[name="imgStatus"]');

    if (img && alt) {
        if (imgData.url) {
            img.src = resolveURL(imgData.url);
            img.hidden = false;
            alt.hidden = true;
        } else {
            img.src = '';
            img.hidden = true;
            alt.hidden = false;
        }
    }

    if (id) {
        const defaultText = id.dataset.defaultText || 'Unknown';
        id.textContent = imgData.id || defaultText;
    }
    if (origin) {
        const defaultText = origin.dataset.defaultText || 'Unknown';
        origin.textContent = imgData.origin || defaultText;
    }
    if (insp_result) {
        const defaultText = insp_result.dataset.defaultText || 'No result';
        insp_result.textContent = imgData.insp_result || defaultText;
    }
    if (trust) {
        const defaultText = trust.dataset.defaultText || '0.00%';
        trust.textContent = formatTrust(imgData.trust) || defaultText;
    }
    if (model) {
        const defaultText = model.dataset.defaultText || 'Unknown';
        model.textContent = imgData.model || defaultText;
    }
    if (status) {
        const borderClasses = getBorderClassesFromData(imgData);
        setBorderClasses(imgSection, borderClasses);
        const defaultText = status.dataset.defaultText || 'Unknown';
        status.textContent = imgData.status || defaultText;
    }
};

export {
    getImgData,
    setImgData
};
