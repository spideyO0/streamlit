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

from playwright.sync_api import Page, expect

from e2e_playwright.shared.app_utils import check_top_level_class


def test_spinner_execution(app: Page):
    app.get_by_test_id("stButton").locator("button").nth(0).click()
    expect(app.get_by_test_id("stSpinner")).to_have_text("Loading...")
    check_top_level_class(app, "stSpinner")


def test_spinner_elapsed_time(app: Page):
    app.get_by_test_id("stButton").locator("button").nth(1).click()
    expect(app.get_by_test_id("stSpinner")).to_contain_text("Loading...")

    # To not make this flaky, we don't check that the timer shows exactly 0.0 seconds,
    # but just that it's somewhere around 0.x seconds
    expect(app.get_by_test_id("stSpinner")).to_contain_text("0.")
    expect(app.get_by_test_id("stSpinner")).to_contain_text("seconds")

    # Similarly, we wait for 1 second and check that it shows 1.x seconds.
    # TODO: Need to check in practice if this is flaky.
    # app.wait_for_timeout(1000)
    # expect(app.get_by_test_id("stSpinner")).to_contain_text("1.")
    # expect(app.get_by_test_id("stSpinner")).to_contain_text("seconds")
    # check_top_level_class(app, "stSpinner")
