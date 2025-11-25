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


import { initClassSelector } from "./filters/class";
import { initDateFilter } from "./filters/date";
import { initExtensionFilter } from "./filters/image/extension";
import { initOriginFilter } from "./filters/origin";
import { initModelFilter } from "./filters/model";
import { initTrustFilter } from "./filters/image/trust";
import { initClassFilter } from "./filters/class";


document.addEventListener("DOMContentLoaded", function() {
    initClassSelector();
    initDateFilter();
    initExtensionFilter();
    initOriginFilter();
    initModelFilter();
    initTrustFilter();
    initClassFilter();

    getNewImageFromHist(0);
});

// BUTTONS
document.getElementById("nextHistImgButton")?.addEventListener("click", () => {
    const indexElement = document.getElementById("currentHistImgIndex");
    const totalIndexElement = document.getElementById("totalHistImgIndex");
    currentIndex = parseInt(indexElement.textContent) || 1;
    totalIndex = parseInt(totalIndexElement.textContent) || 1;
    if (currentIndex >= totalIndex - 1) {
        currentIndex = totalIndex - 1;
    }
    getNewImageFromHist(currentIndex);
});

document.getElementById("prevHistImgButton")?.addEventListener("click", () => {
    const indexElement = document.getElementById("currentHistImgIndex");
    currentIndex = parseInt(indexElement.textContent) || 2;
    if (currentIndex <= 2) {
        currentIndex = 2;
    }
    getNewImageFromHist(currentIndex - 2);
});

// FILTERS
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

// REFRESH IMAGE DATA
function setImageData(data) {
    if (data.type === "new-image") {
        let element = document.getElementById("img-0-name");
        if (element) {
            element.innerText = data.image_url.split("/").pop();
        }
        element = document.getElementById("img-0-origin");
        if (element) {
            element.innerText = data.origin;
        }
        element = document.getElementById("img-0-type");
        if (element) {
            element.innerText = data.insp_result;
        }
        element = document.getElementById("img-0-trust");
        if (element) {
            element.innerText = (data.trust * 100).toFixed(2) + "%";
        }
        element = document.getElementById("img-0-model");
        if (element) {
            element.innerText = data.model;
        }
        element = document.getElementById("currentHistImgIndex");
        if (element) {
            element.innerText = parseInt(data.index) + 1;
        }
        element = document.getElementById("totalHistImgIndex");
        if (element) {
            element.innerText = data.total;
        }
        element = document.getElementById("img-0-alt");
        if (element) {
            element.hidden = true;
        }
        element = document.getElementById("img-0-img");
        if (element) {
            element.src = data.image_url;
            element.hidden = false;
        }
        checkClassSelector(data.true_result);
    }
}

function clearImageData() {
    let element = document.getElementById("img-0-name");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("img-0-origin");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("img-0-type");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("img-0-trust");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("img-0-model");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("currentHistImgIndex");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("totalHistImgIndex");
    if (element) {
        element.innerText = element.getAttribute("data-default-text");
    }
    element = document.getElementById("img-0-alt");
    if (element) {
        element.hidden = false;
    }
    element = document.getElementById("img-0-img");
    if (element) {
        element.src = "";
        element.hidden = true;
    }
}

// GET DATA
async function getNewImageFromHist(index) {
    const ip = await getAPIIP();
    const endpoint = `http://${ip}/image/hist/next`;
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

// TRUE RESULT FORM
document.getElementById("trueResultForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const imageUUID = document.getElementById("img-0-name").innerText.split(".")[0]
    const selectedCheckbox = Array.from(
        document.querySelectorAll('input[name="class-selector-option"]')
    )
    .find(checkbox => checkbox.checked);
    if (!selectedCheckbox) {
        showAlert("Select a true result", "danger", 2);
        return;
    }
    getAPIIP().then(ip => {
        const endpoint = `http://${ip}/image/${imageUUID}/true-result`;
        let content = {
            method: "PUT",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify(selectedCheckbox.value)
        }
        if (selectedCheckbox.value === 'No result') {
            content = {
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }
            }
        }
        fetch(
            endpoint,
            content
        )
        .then(response => {
            if (response.ok) {
                showAlert("Success", "success", 2);
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showAlert("Error", "danger", 2);
        });
    });

});
