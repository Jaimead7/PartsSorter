-- Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Affero General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-- GNU Affero General Public License for more details.
--
-- You should have received a copy of the GNU Affero General Public License
-- along with this program. If not, see <https://www.gnu.org/licenses/>.

-- SQLite 3.45+
-- Chek the number of annotations for each label in a project.
-- Replace PROJECT with the name of the project.


WITH labels AS (
    SELECT json_extract(json_extract(t.result, '$[0].value.rectanglelabels'), '$[0]') as label
    FROM task_completion AS t
        INNER JOIN project AS p
        ON t.project_id = p.id
    WHERE p.title = 'PROJECT'
)
SELECT 
    label,
    COUNT(*)
FROM labels
GROUP BY label;
