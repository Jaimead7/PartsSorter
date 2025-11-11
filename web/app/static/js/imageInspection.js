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


const prevButton = document.getElementById("prevHistImgButton");
const nextButton = document.getElementById("nextHistImgButton");

let apiIP = null;

document.addEventListener("DOMContentLoaded", function() {
    initClassSelector();
    initDateFilter();
    initExtensionFilter();
    initOriginFilter();
    initModelFilter();
    initTrustFilter();
    initClassFilter();
});

nextButton.addEventListener("click", function() {
    const indexElement = document.getElementById("currentHistImgIndex");
    const totalIndexElement = document.getElementById("totalHistImgIndex");
    currentIndex = parseInt(indexElement.textContent) || 1;
    totalIndex = parseInt(totalIndexElement.textContent) || 1;
    if (currentIndex >= totalIndex - 1) {
        currentIndex = totalIndex - 1;
    }
    getNewImage(currentIndex);
});

prevButton.addEventListener("click", function() {
    const indexElement = document.getElementById("currentHistImgIndex");
    currentIndex = parseInt(indexElement.textContent) || 2;
    if (currentIndex <= 2) {
        currentIndex = 2;
    }
    getNewImage(currentIndex - 2);
});

function getQueryParameters(index) {
    let params = [];
    params.push(getExtensionQueryParameters());
    params.push(getDateQueryParameters());
    params.push(getClassQueryParameters());
    params.push(getOriginQueryParameters());
    params.push(getModelQueryParameters());
    params.push(getTrustQueryParameters());
    params.push(`index=${index}`);
    return params.filter(item => item !== "").join("&");
};

function setImageData(data) {
    if (data.type === "new-image") {
        document.getElementById("img-0-origin").innerText = data.origin;
        document.getElementById("img-0-type").innerText = data.insp_result;
        document.getElementById("img-0-trust").innerText = (data.trust * 100).toFixed(2) + "%";
        document.getElementById("img-0-model").innerText = data.model;
        document.getElementById("currentHistImgIndex").innerText = parseInt(data.index) + 1;
        document.getElementById("totalHistImgIndex").innerText = data.total;
        document.getElementById("img-0-alt").hidden = true;
        img = document.getElementById("img-0-img");
        img.src = data.image_url;
        img.hidden = false;
        checkClassSelector(data.insp_result);
    }
}

function clearImageData() {
    let element = document.getElementById("img-0-origin");
    element.innerText = element.getAttribute("data-default-text");
    element = document.getElementById("img-0-type");
    element.innerText = element.getAttribute("data-default-text");
    element = document.getElementById("img-0-trust");
    element.innerText = element.getAttribute("data-default-text");
    element = document.getElementById("img-0-model");
    element.innerText = element.getAttribute("data-default-text");
    element = document.getElementById("currentHistImgIndex");
    element.innerText = element.getAttribute("data-default-text");
    element = document.getElementById("totalHistImgIndex");
    element.innerText = element.getAttribute("data-default-text");
    document.getElementById("img-0-alt").hidden = false;
    img = document.getElementById("img-0-img");
    img.src = "";
    img.hidden = true;
}

async function getNewImage(index) {
    if (apiIP === null) {
        try {
            const response = await fetch("/api/config");
            const config = await response.json();
            apiIP = config.ip;
        } catch (error) {
            console.error("Error loading config:", error);
            return;
        }
    }
    const endpoint = `http://${apiIP}/image/hist/next`;
    const url = `${endpoint}?${getQueryParameters(index)}`;
    try {
        const response = await fetch(url);
        if (response.status === 404) {
            clearImageData();
            return;
        }
        const data = await response.json();
        setImageData(data);
    } catch (error) {
        console.error("Error fetching image:", error);
        clearImageData();
    }
}
