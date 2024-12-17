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

import sys
import os
import json
from typing import List, Dict, Tuple, Set, Union
import numpy as np
from scipy import stats  # type: ignore
from collections import defaultdict
from .perf_traces import (
    calculate_phases_for_all_profiles,
    sum_long_animation_frames,
)
from .types import (
    FullStatistics,
    PhaseStatistics,
    CalculatedPhases,
)
from .test_run_utils import get_stable_test_name


def process_directory(directory_path: str):
    """
    Process each file in the given directory and calculate statistics.

    Args:
        directory_path: The path to the directory containing the files.
    """
    filenames, all_phases, all_long_animation_frames = load_files(directory_path)
    outliers = find_test_run_outliers(filenames, all_phases, all_long_animation_frames)
    return [
        outliers,
        filenames,
        all_phases,
        all_long_animation_frames,
    ]


def load_files(
    directory_path: str,
) -> Tuple[
    List[str],
    List[Dict[str, CalculatedPhases]],
    List[float],
]:
    """
    Load files from the directory and extract relevant data.

    Args:
        directory_path: The path to the directory containing the files.

    Returns:
        A tuple containing filenames, phases, long animation frames sums, and
        entry counts per phase.
    """
    filenames = []
    all_phases = []
    all_long_animation_frames = []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if (
            os.path.isfile(file_path)
            and filename.endswith("json")
            and not filename.startswith("statistics")
        ):
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = json.load(file)

            phases = calculate_phases_for_all_profiles(file_content)
            long_animation_frames_sum = sum_long_animation_frames(file_content)

            filenames.append(filename)
            all_phases.append(phases)
            all_long_animation_frames.append(long_animation_frames_sum)

    return filenames, all_phases, all_long_animation_frames


def find_test_run_outliers(
    filenames: List[str],
    all_phases: List[Dict[str, CalculatedPhases]],
    all_long_animation_frames: List[float],
) -> Set[Tuple[str, float]]:
    """
    Compare results and find statistically significant outliers.

    Args:
        filenames: List of filenames.
        all_phases: List of phases from all files.
        all_long_animation_frames: List of long animation frames sums from all files.
        all_entry_counts: List of entry counts per phase from all files.

    Returns:
        A set of all outliers.
    """
    outliers = set()

    long_animation_frame_outliers = identify_outliers(
        filenames, all_long_animation_frames
    )
    outliers.update(long_animation_frame_outliers)

    phase_outliers = find_phase_outliers(
        filenames,
        calculate_phase_durations(all_phases),
        calculate_phase_counts(all_phases),
    )
    outliers.update(phase_outliers)

    return outliers


def identify_outliers(
    filenames: List[str], values: Union[List[float], List[int]], threshold: int = 2
) -> Set[Tuple[str, float]]:
    """
    Find statistically significant outliers in the given values using the
    Z-score method.

    Args:
        filenames: List of filenames.
        values: List of values to analyze.
        threshold: The Z-score threshold to use for identifying outliers. Default is 2.

    Returns:
        A set of outliers.
    """
    mean_value = np.mean(values)
    std_value = np.std(values)

    outliers = {
        (filenames[i], value)
        for i, value in enumerate(values)
        if abs(value - mean_value) > threshold * std_value
    }

    return outliers


def calculate_phase_durations(
    all_phases: List[Dict[str, CalculatedPhases]],
) -> Dict[str, Dict[str, List[float]]]:
    """
    Calculate summed actualDuration for each phase.

    Args:
        all_phases: List of phases from all files.

    Returns:
        A dictionary containing phase durations for each profile.
    """
    phase_durations: Dict[str, Dict[str, List[float]]] = {}
    for phases in all_phases:
        for profile_name, profile_phases in phases.items():
            if profile_name not in phase_durations:
                phase_durations[profile_name] = {}
            for phase, data in profile_phases.items():
                if phase not in phase_durations[profile_name]:
                    phase_durations[profile_name][phase] = []
                phase_durations[profile_name][phase].append(data["duration_ms"])

    return phase_durations


def calculate_phase_counts(
    all_phases: List[Dict[str, CalculatedPhases]],
) -> Dict[str, Dict[str, List[int]]]:
    """
    Calculate summed count for each phase.

    Args:
        all_phases: List of phases from all files.

    Returns:
        A dictionary containing phase durations for each profile.
    """
    phase_counts: Dict[str, Dict[str, List[int]]] = {}
    for phases in all_phases:
        for profile_name, profile_phases in phases.items():
            if profile_name not in phase_counts:
                phase_counts[profile_name] = {}
            for phase, data in profile_phases.items():
                if phase not in phase_counts[profile_name]:
                    phase_counts[profile_name][phase] = []
                phase_counts[profile_name][phase].append(data["count"])

    return phase_counts


def find_phase_outliers(
    filenames: List[str],
    phase_durations: Dict[str, Dict[str, List[float]]],
    phase_counts: Dict[str, Dict[str, List[int]]],
) -> Set[Tuple[str, float]]:
    """
    Detect outliers for each phase.

    Args:
        filenames: List of filenames.
        phase_durations: Dictionary containing phase durations for each profile.
        phase_counts: Dictionary containing phase counts for each profile.

    Returns:
        A set of phase outliers.
    """
    outliers = set()
    for profile_name, phases in phase_durations.items():
        for phase, durations in phases.items():
            duration_outliers = identify_outliers(filenames, durations)
            outliers.update(duration_outliers)

            counts = phase_counts[profile_name][phase]
            count_outliers = identify_outliers(filenames, counts)
            outliers.update(count_outliers)

    return outliers


def find_entry_count_outliers(
    filenames: List[str], all_entry_counts: List[Dict[str, Dict[str, int]]]
) -> Set[Tuple[str, float]]:
    """
    Detect outliers based on entry counts per phase.

    Args:
        filenames: List of filenames.
        all_entry_counts: List of entry counts per phase from all files.

    Returns:
        A set of entry count outliers.
    """
    outliers = set()
    for profile_counts in all_entry_counts:
        for profile_name, phase_counts in profile_counts.items():
            for phase, count in phase_counts.items():
                counts: List[float] = [
                    float(counts[profile_name][phase])
                    for counts in all_entry_counts
                    if profile_name in counts and phase in counts[profile_name]
                ]
                phase_outliers = identify_outliers(filenames, counts)
                outliers.update(phase_outliers)

    return outliers


def process_test_runs(directory_path: str) -> None:
    """
    Process each test group derived from the test result files in the directory
    twice, omitting outliers from the first run in the second run to calculate
    statistics.

    Args:
        directory_path: The path to the directory containing the files.
    """
    # Group files by their stable test name
    grouped_files = defaultdict(list)
    for filename in os.listdir(directory_path):
        if filename.endswith(".json") and not filename.startswith("statistics"):
            stable_test_name = get_stable_test_name(filename)
            grouped_files[stable_test_name].append(filename)

    for stable_test_name, filenames in grouped_files.items():
        # First run to find outliers
        [outliers, filenames, all_phases, all_long_animation_frames] = (
            process_directory(directory_path)
        )
        print(f"First run outliers for {stable_test_name}: {outliers}")

        # Filter out outliers
        filtered_phases = [
            phases
            for i, phases in enumerate(all_phases)
            if filenames[i] not in {outlier[0] for outlier in outliers}
        ]
        filtered_long_animation_frames = [
            frames
            for i, frames in enumerate(all_long_animation_frames)
            if filenames[i] not in {outlier[0] for outlier in outliers}
        ]

        # Second run - with outliers from the first run removed
        # Collect statistics
        phase_durations = calculate_phase_durations(filtered_phases)
        phase_counts = calculate_phase_counts(filtered_phases)

        phase_statistics: Dict[str, PhaseStatistics] = {
            profile_name: {  # type: ignore
                phase: {
                    "duration_ms": {
                        "mean": np.mean(durations),
                        "std": np.std(durations),
                        "var": np.var(durations),
                    },
                    "count": {
                        "mean": np.mean(phase_counts[profile_name][phase]),
                        "std": np.std(phase_counts[profile_name][phase]),
                        "var": np.var(phase_counts[profile_name][phase]),
                    },
                }
                for phase, durations in phases.items()
            }
            for profile_name, phases in phase_durations.items()
        }

        statistics: FullStatistics = {
            "long_animation_frames": {
                "mean": np.mean(filtered_long_animation_frames),
                "std": np.std(filtered_long_animation_frames),
                "var": np.var(filtered_long_animation_frames),
            },
            "phase_statistics": phase_statistics,
        }

        print(
            f"Second run statistics for {stable_test_name}: {json.dumps(statistics, indent=2)}"
        )

        # write the statistics json file to disk
        statistics_dir = f"{directory_path}/statistics"
        os.makedirs(statistics_dir, exist_ok=True)
        with open(f"{statistics_dir}/{stable_test_name}.json", "w") as file:
            json.dump(statistics, file)


if __name__ == "__main__":
    process_test_runs(sys.argv[1])
