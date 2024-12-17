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

from typing import Dict, Union, List, TypedDict, Any, Optional

Value = Union[float, List[float]]
ComparisonValue = Union[float, List[float], Dict[str, Value]]


class Statistics(TypedDict):
    mean: float
    std: float
    var: float


class PhaseStatisticEntry(TypedDict):
    duration_ms: Statistics
    count: Statistics


class PhaseStatistics(TypedDict):
    mount: PhaseStatisticEntry
    nested_update: PhaseStatisticEntry
    update: PhaseStatisticEntry


class CalculatedPhase(TypedDict):
    duration_ms: float
    count: int


CalculatedPhases = Dict[str, CalculatedPhase]


class FullStatistics(TypedDict):
    long_animation_frames: Statistics
    phase_statistics: Dict[str, PhaseStatistics]


class ComparisonDifference(TypedDict):
    baseline: ComparisonValue
    treatment: ComparisonValue
    difference: ComparisonValue


class ComparisonResult(TypedDict):
    long_animation_frames: ComparisonDifference
    phase_statistics: Dict[str, Dict[str, ComparisonDifference]]


class Metric(TypedDict):
    name: str
    value: Union[float, int]


class Mark(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float


class Paint(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float


class Measure(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float


class Script(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float
    invoker: str
    invokerType: str
    windowAttribution: str
    executionStart: float
    forcedStyleAndLayoutDuration: float
    pauseDuration: float
    sourceURL: str
    sourceFunctionName: str
    sourceCharPosition: int


class LongAnimationFrame(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float
    renderStart: float
    styleAndLayoutStart: float
    firstUIEventTimestamp: float
    blockingDuration: float
    scripts: List[Script]


class LongTaskAttribution(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float
    containerType: str
    containerSrc: str
    containerId: str
    containerName: str


class LongTask(TypedDict):
    name: str
    entryType: str
    startTime: float
    duration: float
    attribution: List[LongTaskAttribution]


class ProfileEntry(TypedDict):
    phase: str
    actualDuration: float
    baseDuration: float
    startTime: float
    commitTime: float


class Profile(TypedDict):
    entries: List[ProfileEntry]
    totalWrittenEntries: int


class CapturedTraces(TypedDict):
    mark: Optional[List[Mark]]
    paint: Optional[List[Paint]]
    measure: Optional[List[Measure]]
    # We can't utilize `long-animation-frame` as a key because it's not a valid
    # Python identifier, but that is the actual key in the JSON file.
    # "long-animation-frame": Optional[List[LongAnimationFrame]]
    longtask: Optional[List[LongTask]]
    profiles: Optional[Dict[str, Profile]]


class PerformanceTraceJSONShape(TypedDict):
    metrics: List[Metric]
    capturedTraces: CapturedTraces
