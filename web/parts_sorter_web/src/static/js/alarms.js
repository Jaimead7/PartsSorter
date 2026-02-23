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
import { getCurrentPage, getTotalPages } from './components/pagination.js';
import { getAlarmTypeQueryParameters, initAlarmTypeFilter } from './filters/alarm/type.js';
import { getDateQueryParameters, initDateFilter } from './filters/date.js';
import { getOriginQueryParameters, initOriginFilter } from './filters/origin.js';


let queryParameters = '';

function updateQueryParameters() {
    let params = [];
    params.push(getDateQueryParameters());
    params.push(getOriginQueryParameters());
    params.push(getAlarmTypeQueryParameters());
    queryParameters = params.filter(item => item !== '').join('&');
};

function getQueryParameters(limit= 10, offset= 0) {
    let params = [queryParameters];
    params.push(`limit=${limit}`);
    params.push(`offset=${offset}`);
    return params.filter(item => item !== '').join('&');
};

function updateAlarmTable(data) {
    console.log(data); //TODO
};

async function clearAlarmTable() {
    const tbody = document.querySelector('#alarmsTable tbody');
    if (tbody) {
        tbody.innerHTML = '';
    }
};

async function loadAlarms(limit= 10, offset= 0) {
    const endpoint = `/api/alarm/?${getQueryParameters(limit, offset)}`;
    fetch(endpoint)
    .then(async (response) => {
        if (response.status === 404) {
            showAlert('No alrams found.', 'warning', 2);
            clearAlarmTable();
            return;
        }
        if (!response.ok) {
            throw new Error(`${response.status} (${response.statusText})`)
        }
        const data = await response.json();
        updateAlarmTable(data);
    })
    .catch((error) => {
        showAlert(`Error fetching alarms: ${error.message}`, 'danger', 2);
        clearAlarmTable();
    });
};

async function updateFilters() {
    updateQueryParameters();
    const nAlarmsPage = 10; //TODO: insert a selector
    await loadAlarms(nAlarmsPage, 0);
};

async function initButtons() {
    document.getElementById('applyFiltersBtn')?.addEventListener('click', async () => {
        await updateFilters();
    });

    document.getElementById('prevPageButton')?.addEventListener('click', async () => {
        const nAlarmsPage = 10; //TODO: insert a selector
        const currentPage = getCurrentPage();

        let offset = (currentPage - 1) * nAlarmsPage;
        offset = offset < 0 ? 0 : offset;

        await loadAlarms(nAlarmsPage, offset);
    });

    document.getElementById('nextPageButton')?.addEventListener('click', async () => {
        const nAlarmsPage = 10; //TODO: insert a selector
        const totalPages = getTotalPages();
        const currentPage = getCurrentPage();

        const nextPage = Math.min(currentPage + 1, totalPages);

        let offset = nextPage * nAlarmsPage;
        offset = offset < 0 ? 0 : offset;

        await loadAlarms(nAlarmsPage, offset);
    });
};

document.addEventListener('DOMContentLoaded', () => {
    initButtons();

    Promise.all([
        initDateFilter(),
        initOriginFilter(),
        initAlarmTypeFilter()
    ])
    .finally(() => updateFilters());
});
