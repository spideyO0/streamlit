# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2024)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Sequence

TYPE_PAIRS = [
    (".jpg", ".jpeg"),
    (".mpg", ".mpeg"),
    (".mp4", ".mpeg4"),
    (".tif", ".tiff"),
    (".htm", ".html"),
]

ALLOWED_MIME_TYPES = ["image", "audio", "video", "text"]


def normalize_upload_file_type(file_type: str | Sequence[str]) -> Sequence[str]:
    if isinstance(file_type, str):
        file_type = [file_type]

    file_type = [t.lower() for t in file_type]

    # Convert mime types to wildcard format, otherwise add dot prefix.
    # Note that we are not checking here if the file extension is valid.
    file_type = [
        f"{file_type_entry}/*"
        if file_type_entry in ALLOWED_MIME_TYPES
        else (file_type_entry if file_type_entry[0] == "." else f".{file_type_entry}")
        for file_type_entry in file_type
    ]

    for x, y in TYPE_PAIRS:
        if x in file_type and y not in file_type:
            file_type.append(y)
        if y in file_type and x not in file_type:
            file_type.append(x)

    return file_type
