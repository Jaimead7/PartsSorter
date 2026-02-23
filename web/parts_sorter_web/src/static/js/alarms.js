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


import { showAlert, escapeHtml, formatDate } from './utils.js';
import { getCurrentPage, getTotalPages, setCurrentPage, setTotalPages } from './components/pagination.js';
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

function getQueryParameters(limit= 10, page= 0) {
    let params = [queryParameters];
    params.push(`limit=${limit}`);
    params.push(`page=${page}`);
    return params.filter(item => item !== '').join('&');
};

function getTableRow(alarm) {
    const row = document.createElement('tr');
    const formattedDate = formatDate(alarm.date);
    row.innerHTML = `
        <td>${formattedDate}</td>
        <td>${escapeHtml(alarm.origin)}</td>
        <td>${escapeHtml(alarm.alarm_type)}</td>
        <td>${escapeHtml(alarm.message)}</td>
    `;
    return row;
};

async function updateAlarmTable(data) {
    await clearAlarmTable();

    const tbody = document.querySelector('#alarmsTable tbody');
    if (!tbody) return;
    if (!data || data.length === 0) return;

    setCurrentPage(data.current_page);
    setTotalPages(data.total_pages);
    console.log(data);
    data.alarms?.forEach(alarm => {
        tbody.appendChild(getTableRow(alarm));
    });    
};

async function clearAlarmTable() {
    const tbody = document.querySelector('#alarmsTable tbody');
    if (tbody) {
        tbody.innerHTML = '';
    }
    setCurrentPage(0);
    setTotalPages(0);
};

async function loadAlarms(limit= 10, page= 0) {
    const endpoint = `/api/alarm/?${getQueryParameters(limit, page)}`;
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

        let page = getCurrentPage() - 1;
        page = page < 0 ? 0 : page;

        await loadAlarms(nAlarmsPage, page);
    });

    document.getElementById('nextPageButton')?.addEventListener('click', async () => {
        const nAlarmsPage = 10; //TODO: insert a selector

        let nextPage = Math.min(getCurrentPage() + 1, getTotalPages());
        nextPage = nextPage < 0 ? 0 : nextPage;

        await loadAlarms(nAlarmsPage, nextPage);
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
