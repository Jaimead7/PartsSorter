# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import cv2
import numpy as np

PALETTE: tuple[tuple[int, int, int], ...]= (
    (255, 42, 4),
    (235, 219, 11),
    (243, 243, 243),
    (183, 223, 0),
    (104, 31, 17),
    (221, 111, 255),
    (79, 68, 255),
    (0, 237, 204),
    (68, 243, 0),
    (255, 0, 189),
    (128, 128, 128),
    (0, 128, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 0),
    (255, 192, 203),
    (0, 0, 128),
    (64, 224, 208),
    (255, 20, 147)
)

def get_color(i: int) -> tuple[int, int, int]:
    return PALETTE[i % len(PALETTE)]

def get_font_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
    b: int
    g: int
    r: int
    b, g, r = color
    brightness: float = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if brightness > 127.5 else (255, 255, 255)

def plot_rect(
    img: np.ndarray,
    rect: np.ndarray,
    line_width: float | None = None
) -> None:
    if line_width is None:
        line_width = 2
    pt1: tuple = (int(rect[0]), int(rect[1]))
    pt2: tuple = (int(rect[2]), int(rect[3]))
    color: tuple[int, int, int] = get_color(int(rect[-1]))
    cv2.rectangle(
        img= img,
        pt1= pt1,
        pt2= pt2,
        color= color,
        thickness= int(line_width)
    )

def plot_label(
    img: np.ndarray,
    rect: np.ndarray,
    names: dict[int, str],
    conf: bool = True,
    labels: bool = True,
    font_size: float | None = None,
    line_width: float | None = None
) -> None:
    if font_size is None:
        font_size = 0.5
    if line_width is None:
        line_width = 2
    color: tuple[int, int, int] = get_color(int(rect[-1]))
    text: str = ''
    if labels:
        try:
            text: str = f'{names[int(rect[-1])]}'
        except Exception as e:
            text: str = f'{int(rect[-1])}'
    if conf:
        text += f'{rect[-2]:.2f}'
    text = text.strip()
    font: int = cv2.FONT_HERSHEY_SIMPLEX
    font_color: tuple = get_font_color(color)
    (txt_w, txt_h), _ = cv2.getTextSize(
        text,
        font,
        font_size,
        1
    )
    inf_left_corner: tuple[int, int] = (
        int(rect[0] - line_width),
        int(rect[1])
    )
    text_p0: tuple[int, int] = (
        int(rect[0]),
        int(rect[1] - line_width)
    )
    sup_right_corner: tuple[int, int] = (
        int(rect[0] + txt_w + line_width),
        int(rect[1] - txt_h - 2*line_width)
    )
    cv2.rectangle(
        img= img,
        pt1= inf_left_corner,
        pt2= sup_right_corner,
        color= color,
        thickness= -1
    )
    cv2.putText(
        img= img,
        text= text,
        org= text_p0,
        fontFace= font,
        fontScale= font_size,
        color= font_color,
        thickness= 1,
        lineType= cv2.LINE_AA
    )
