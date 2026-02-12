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


import { showAlert } from './utils.js';
import { getOriginFilterOptions } from './filters/origin.js';


let ws;
let reconnectSeconds = 10;
let reconnectTimeout;


async function initWebSocket() {
    try {
        connectWebSocket(`ws://${window.location.host}/api/ws/image-stream/`);
    } catch (error) {
        console.error('Error connecting to the web socket:', error);
    }
};

async function scheduleReconnect() {
    showAlert('Reconnecting to server...', 'warning', reconnectSeconds);
    clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(() => {
        initWebSocket();
    }, reconnectSeconds * 1000);
};

function connectWebSocket(url) {
    ws = new WebSocket(url);

    ws.onopen = () => {
        showAlert('Connected to server.', 'success', 5);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('New message received:', data);
        switch (data.type) {
            case 'new-image':
                processNewImage(data);
        }
    };

    ws.onerror = () => {
        console.error('Connection error');
        scheduleReconnect();
    };

    ws.onclose = () => {
        console.warn('Websocket disconnected');
        scheduleReconnect();
    };
};

async function processNewImage(data) {
    const originOptions = getOriginFilterOptions();
    data.origin = data.origin ? data.origin : 'Unknown';
    if (originOptions.includes(data.origin)) {
        transferImages();
        const imgData = {
            src: `/api/${data.image_url}`,
            name: data.image_url.split('/').pop() || 'Unknown',
            origin: data.origin,
            insp_result: data.insp_result,
            trust: (data.trust * 100).toFixed(2) + '%',
            model: data.model
        };
        setImgInfo('img0', imgData);
    }
};

function clearImages() {
    for (let i = 4; i >= 0; i--) {
        const imgData = {
            src: null,
            name: 'Unknown',
            origin: 'Unknown',
            insp_result: 'No result',
            trust: 'NULL',
            model: 'Unknown'
        };
        setImgInfo(`img${i}`, imgData);
    }
};

function transferImages() {
    for (let i = 4; i > 0; i--) {
        try {
            const imgData = getImgInfo(`img${i-1}`);
            setImgInfo(`img${i}`, imgData);
        } catch (error) {}
    }
};

function getImgInfo(imgId) {
    const article = document.getElementById(imgId);
    const img = article?.querySelector('[name="img"]');
    const name = article?.querySelector('[name="imgName"]');
    const origin = article?.querySelector('[name="imgOrigin"]');
    const insp_result = article?.querySelector('[name="imgType"]');
    const trust = article?.querySelector('[name="imgTrust"]');
    const model = article?.querySelector('[name="imgModel"]');

    return {
        src: img && img.hasAttribute('src') ? img.getAttribute('src') : '',
        name: name ? name.textContent : '',
        origin: origin ? origin.textContent : '',
        insp_result: insp_result ? insp_result.textContent : '',
        trust: trust ? trust.textContent : '',
        model: model ? model.textContent : ''
    };
};

function setImgInfo(imgId, imgData) {
    const article = document.getElementById(imgId);
    if (!article) return;

    const img = article.querySelector('[name="img"]');
    const alt = article.querySelector('[name="imgAlt"]');
    const name = article.querySelector('[name="imgName"]');
    const origin = article.querySelector('[name="imgOrigin"]');
    const insp_result = article.querySelector('[name="imgType"]');
    const trust = article.querySelector('[name="imgTrust"]');
    const model = article.querySelector('[name="imgModel"]');

    if (img && alt) {
        if (imgData.src) {
            img.src = imgData.src;
            img.hidden = false;
            alt.hidden = true;
        } else {
            img.src = '';
            img.hidden = true;
            alt.hidden = false;
        }
    }

    if (name && 'name' in imgData) name.textContent = imgData.name;
    if (origin && 'origin' in imgData) origin.textContent = imgData.origin;
    if (insp_result && 'insp_result' in imgData) insp_result.textContent = imgData.insp_result;
    if (trust && 'trust' in imgData) trust.textContent = imgData.trust;
    if (model && 'model' in imgData) model.textContent = imgData.model;
};

export { initWebSocket };
