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

-- Rename a label name.
-- Replace CURRENT with the current label name.
-- Replace NEW with the new label name.

UPDATE project
SET label_config = REPLACE(label_config, '"CURRENT"', '"NEW"')
WHERE label_config LIKE '%"CURRENT"%';
UPDATE project
SET control_weights = REPLACE(control_weights, '"CURRENT"', '"NEW"')
WHERE control_weights LIKE '%"CURRENT"%';
UPDATE project
SET parsed_label_config = REPLACE(parsed_label_config, '"CURRENT"', '"NEW"')
WHERE parsed_label_config LIKE '%"CURRENT"%';
UPDATE projects_projectsummary
SET created_labels = REPLACE(created_labels, '"CURRENT"', '"NEW"')
WHERE created_labels LIKE '%"CURRENT"%';
UPDATE task_completion
SET result = REPLACE(result, '"CURRENT"', '"NEW"')
WHERE result LIKE '%"CURRENT"%';
