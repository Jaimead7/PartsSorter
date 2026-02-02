# MIT License

# Copyright (c) 2025 Jaime Álvarez Díaz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os


def pytest_configure() -> None:
    os.environ['ORIGIN_NAME'] = 'Test'
    os.environ['API_URL'] = ''
    os.environ['ACTUATOR_PIN'] = '14'
    os.environ['CAMERA_SENSOR_PIN'] = '23'
    os.environ['ACTUATOR_SENSOR_PIN'] = '24'

def pytest_unconfigure() -> None:
    os.environ.pop('ORIGIN_NAME', None)
    os.environ.pop('API_URL', None)
    os.environ.pop('ACTUATOR_PIN', None)
    os.environ.pop('CAMERA_SENSOR_PIN', None)
    os.environ.pop('ACTUATOR_SENSOR_PIN', None)
