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
import { getImgData, setImgData, initImgButtons } from './components/images.js';
import { initOriginFilter, getOriginFilterOptions } from './filters/origin.js';


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

async function scheduleReconnect(msg, type) {
    showAlert(`${msg} Reconnecting to server...`, type, reconnectSeconds);
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
            case 'img':
                setNewImage(data);
                break;
            case 'imgStatus':
                processNewImageStatus(data);
                break;
        }
    };

    ws.onerror = () => {
        scheduleReconnect('Connection error.', 'danger');
    };

    ws.onclose = () => {
        scheduleReconnect('Websocket disconnected.', 'warning');
    };
};

async function setNewImage(data) {
    const originOptions = getOriginFilterOptions();
    if (originOptions.includes(data.origin)) {
        transferImages();
        setImgData('img0', data);
    }
};

async function processNewImageStatus(data) {
    document.querySelectorAll('article[id^="img"]').forEach(image => {
        const imgData = getImgData(image.id);
        if (imgData.id === data.id) {
            imgData.status = data.status;
            setImgData(image.id, imgData);
        }
    });
};

function clearImages() {
    document.querySelectorAll('article[id^="img"]').forEach(image => {
        setImgData(article.id, {});
    });
};

function transferImages() {
    const imgElements = document.querySelectorAll('article[id^="img"]');
    const sortedElements = Array.from(imgElements).sort((a, b) => {
        const numA = parseInt(a.id.replace('img', ''));
        const numB = parseInt(b.id.replace('img', ''));
        return numA - numB;
    });
    for (let i = sortedElements.length - 1; i > 0; i--) {
        try {
            const imgData = getImgData(`img${i-1}`);
            setImgData(`img${i}`, imgData);
        } catch (error) {}
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initImgButtons();

    Promise.all([
        initOriginFilter()
    ])
    .finally(() => initWebSocket());
});
