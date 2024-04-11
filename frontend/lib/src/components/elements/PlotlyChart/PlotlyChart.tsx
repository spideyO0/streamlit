/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2024)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { ReactElement, useState, useCallback } from "react"
import { useTheme } from "@emotion/react"
import { EmotionTheme } from "@streamlit/lib/src/theme"
import {
  Figure as FigureProto,
  PlotlyChart as PlotlyChartProto,
} from "@streamlit/lib/src/proto"
import { withFullScreenWrapper } from "@streamlit/lib/src/components/shared/FullScreenWrapper"
import Plot from "react-plotly.js"
import {
  applyStreamlitTheme,
  layoutWithThemeDefaults,
  replaceTemporaryColors,
} from "./CustomTheme"
import { PlotRelayoutEvent } from "plotly.js"
import { WidgetStateManager } from "@streamlit/lib/src/WidgetStateManager"
import { keysToSnakeCase } from "@streamlit/lib/src/util/utils"
import { logMessage } from "@streamlit/lib/src/util/log"

export interface PlotlyChartProps {
  width: number
  element: PlotlyChartProto
  height: number | undefined
  isFullScreen: boolean
  widgetMgr: WidgetStateManager
  disabled: boolean
  fragmentId?: string
}

export interface PlotlyIFrameProps {
  width: number
  height: number | undefined
  url: string
}

// Copied and Pasted from Plotly type def
export interface SelectionRange {
  x: number[]
  y: number[]
}

export interface Selection extends SelectionRange {
  xref: string
  yref: string
}

export const DEFAULT_HEIGHT = 450
const SELECTIONS_KEY = "selections"
const RELAYOUT_KEY = "relayout"

/**
 * Parses an SVG path string into separate x and y coordinates.
 *
 * The function takes a single SVG path string as input. This path string should start with 'M'
 * (move to command), followed by pairs of x and y coordinates separated by commas, and optionally
 * end with 'Z' to close the path. Each pair of coordinates is separated by 'L' (line to command).
 *
 * Example Input:
 * "M4.016412414518674,8.071685352641575L4.020620725933719,7.8197516509841165Z"
 *
 * Example Output:
 * {
 *   x: [4.016412414518674, 4.020620725933719],
 *   y: [8.071685352641575, 7.8197516509841165]
 * }
 *
 * @param {string} pathData - The SVG path string to be parsed.
 * @returns {SelectionRange} An object containing two arrays: `x` for all x coordinates and `y` for all y coordinates.
 */
export function parseLassoPath(pathData: string): SelectionRange {
  if (pathData === "") {
    return {
      x: [],
      y: [],
    }
  }
  const points = pathData.replace("M", "").replace("Z", "").split("L")

  const x: number[] = []
  const y: number[] = []

  points.forEach(point => {
    const [xVal, yVal] = point.split(",").map(Number)
    x.push(xVal)
    y.push(yVal)
  })

  return { x, y }
}

export function parseBoxSelection(selection: any): SelectionRange {
  const hasRequiredFields =
    "x0" in selection &&
    "x1" in selection &&
    "y0" in selection &&
    "y1" in selection

  if (!hasRequiredFields) {
    return { x: [], y: [] }
  }

  const x: number[] = [selection.x0, selection.x1]
  const y: number[] = [selection.y0, selection.y1]
  return { x, y }
}

/** Render an iframed Plotly chart from a URL */
function renderIFrame({
  url,
  width,
  height: propHeight,
}: PlotlyIFrameProps): ReactElement {
  const height = propHeight || DEFAULT_HEIGHT
  return (
    <iframe
      title="Plotly"
      src={url}
      style={{ width, height, colorScheme: "normal" }}
    />
  )
}

/** Render a Plotly chart from a FigureProto */
function PlotlyFigure({
  element,
  width,
  height,
  isFullScreen,
  widgetMgr,
  disabled,
  fragmentId,
}: PlotlyChartProps): ReactElement {
  const figure = element.figure as FigureProto

  const [config] = useState(JSON.parse(figure.config))

  const theme: EmotionTheme = useTheme()
  const getInitialValue = useCallback((): any => {
    const spec = JSON.parse(
      replaceTemporaryColors(figure.spec, theme, element.theme)
    )
    const storedValue = widgetMgr.getJsonValue(element)

    // we store serialized json in widgetStateManager when resetting so need to check an empty dictionary string
    if (storedValue !== undefined && storedValue !== "{}") {
      const parsedStoreValue = JSON.parse(storedValue.toString())
      // check if there is a selection
      if (parsedStoreValue.select) {
        const { data, selections } = widgetMgr.getExtraWidgetInfo(
          element,
          SELECTIONS_KEY
        )

        // https://plotly.com/javascript/reference/index/
        // data is originalData + selectedpoints
        spec.data = data
        spec.layout.selections = selections
        if (spec.data) {
          const hasSelectedPoints: boolean = spec.data.some(
            (trace: any) =>
              "selectedpoints" in trace &&
              trace.selectedpoints &&
              trace.selectedpoints.length > 0
          )
          if (hasSelectedPoints) {
            spec.data.forEach((trace: any) => {
              if (!trace.selectedpoints) {
                // Plotly will automatically set traces in selectedpoints with the 100% opaqueness
                // setting selectedpoints to an empty array will set these points to be opaque, thus representing that they're unselected
                trace.selectedpoints = []
              }
            })
          }
        }
      }
    }
    const zoom = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)

    try {
      if (zoom?.[RELAYOUT_KEY]) {
        const zoomDetails = zoom[RELAYOUT_KEY]

        if (zoomDetails["xaxis.range[0]"]) {
          spec.layout.xaxis.range = [
            zoomDetails["xaxis.range[0]"],
            zoomDetails["xaxis.range[1]"],
          ]
          spec.layout.yaxis.range = [
            zoomDetails["yaxis.range[0]"],
            zoomDetails["yaxis.range[1]"],
          ]
        } else if (zoomDetails["xaxis.autorange"]) {
          spec.layout.xaxis.autorange = true
          spec.layout.yaxis.autorange = true
        }

        if (zoomDetails.dragmode) {
          spec.layout.dragmode = zoomDetails.dragmode
        }
      }
    } catch (e) {
      logMessage(e)
      logMessage(spec)
      logMessage(zoom)
    }
    return spec
  }, [element, figure.spec, theme, widgetMgr])

  const spec = getInitialValue()

  const initialHeight = spec.layout.height
  const initialWidth = spec.layout.width

  if (isFullScreen) {
    spec.layout.width = width
    spec.layout.height = height
  } else if (element.useContainerWidth) {
    spec.layout.width = width
  } else {
    spec.layout.width = initialWidth
    spec.layout.height = initialHeight
  }

  // https://plotly.com/javascript/reference/layout/#layout-clickmode
  // This allows single selections and shift click to add / remove selections
  if (element.isSelectEnabled) {
    spec.layout.clickmode = "event+select"
    spec.layout.hovermode = "closest"
  }
  if (element.theme === "streamlit") {
    applyStreamlitTheme(spec, theme)
  } else {
    // Apply minor theming improvements to work better with Streamlit
    spec.layout = layoutWithThemeDefaults(spec.layout, theme)
  }

  const handleSelect = (event: Readonly<Plotly.PlotSelectionEvent>): void => {
    const returnValue: any = { select: {} }
    const { data } = spec
    const pointIndices: number[] = []
    const selectedBoxes: Selection[] = []
    const selectedLassos: Selection[] = []
    const selectedPoints: Array<any> = []

    // event.selections doesn't show up in the PlotSelectionEvent
    // @ts-expect-error
    const selections = event.selections
    if (event.points.length === 0 && selections && selections.length === 0) {
      return
    }

    event.points.forEach(function (point: any) {
      selectedPoints.push({
        ...point,
        legendgroup: point.data.legendgroup || undefined,
        // Remove data and full data as they have been deemed to be unnecessary data overhead
        data: undefined,
        fullData: undefined,
      })
      pointIndices.push(point.pointIndex)

      // build graph representation to retain state
      if (
        data[point.curveNumber] &&
        !data[point.curveNumber].selectedpoints.includes(point.pointIndex)
      ) {
        data[point.curveNumber].selectedpoints.push(point.pointIndex)
      } else {
        data[point.curveNumber].selectedpoints = [point.pointIndex]
      }
    })

    returnValue.select.points = selectedPoints

    // point_indices to replicate pythonic return value
    returnValue.select.point_indices = pointIndices

    // event.selections doesn't show up in the PlotSelectionEvent
    // @ts-expect-error
    if (event.selections) {
      // @ts-expect-error
      event.selections.forEach((selection: any) => {
        // box selection
        if (selection.type === "rect") {
          const xAndy = parseBoxSelection(selection)
          const returnSelection: Selection = {
            xref: selection.xref,
            yref: selection.yref,
            x: xAndy.x,
            y: xAndy.y,
          }
          selectedBoxes.push(returnSelection)
        }
        // lasso selection
        if (selection.type === "path") {
          const xAndy = parseLassoPath(selection.path)
          const returnSelection: Selection = {
            xref: selection.xref,
            yref: selection.yref,
            x: xAndy.x,
            y: xAndy.y,
          }
          selectedLassos.push(returnSelection)
        }
      })
    }

    returnValue.select.box = selectedBoxes
    returnValue.select.lasso = selectedLassos
    returnValue.select.points = returnValue.select.points.map((point: any) =>
      keysToSnakeCase(point)
    )
    widgetMgr.setExtraWidgetInfo(element, SELECTIONS_KEY, {
      data: data,
      // @ts-expect-error
      selections: event.selections,
    })
    widgetMgr.setJsonValue(element, returnValue, { fromUi: true }, fragmentId)
  }

  const { data, layout, frames } = spec

  const handleDoubleClick = useCallback((): void => {
    const relayout = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)?.[
      RELAYOUT_KEY
    ]
    const dragmode = relayout?.dragmode
    if (dragmode === "select" || dragmode === "lasso") {
      const xrange0 = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)[
        RELAYOUT_KEY
      ]?.["xaxis.range[0]"]
      if (xrange0) {
        const xrange1 = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)[
          RELAYOUT_KEY
        ]?.["xaxis.range[1]"]
        const yrange0 = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)[
          RELAYOUT_KEY
        ]?.["yaxis.range[0]"]
        const yrange1 = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)[
          RELAYOUT_KEY
        ]?.["yaxis.range[1]"]
        widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
          [RELAYOUT_KEY]: {
            ["xaxis.range[0]"]: xrange0 ?? [spec.layout.xaxis.range[0]],
            ["xaxis.range[1]"]: xrange1 ?? [spec.layout.xaxis.range[1]],
            ["yaxis.range[0]"]: yrange0 ?? [spec.layout.yaxis.range[0]],
            ["yaxis.range[1]"]: yrange1 ?? [spec.layout.yaxis.range[1]],
            dragmode: dragmode ?? spec.layout.dragmode,
          },
        })
      }
      widgetMgr.setExtraWidgetInfo(element, SELECTIONS_KEY, {})
      widgetMgr.setJsonValue(element, {}, { fromUi: true }, fragmentId)
    } else {
      widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
        [RELAYOUT_KEY]: {
          dragmode: dragmode ?? spec.layout.dragmode,
          "yaxis.autorange": true,
          "xaxis.autorange": true,
        },
      })
    }
  }, [widgetMgr, element])

  const handleRelayout = (event: PlotRelayoutEvent): void => {
    const storedEvent = widgetMgr.getExtraWidgetInfo(element, RELAYOUT_KEY)

    if (event["xaxis.range[0]"] || event.dragmode) {
      if (storedEvent && storedEvent[RELAYOUT_KEY]) {
        widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
          [RELAYOUT_KEY]: { ...storedEvent[RELAYOUT_KEY], ...event },
        })
      } else {
        widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
          [RELAYOUT_KEY]: { ...event },
        })
      }
    }
    if (event["xaxis.autorange"]) {
      if (storedEvent && storedEvent[RELAYOUT_KEY]) {
        widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
          // remove xaxis.range in order to remove zoom boundaries
          [RELAYOUT_KEY]: {
            ...storedEvent[RELAYOUT_KEY],
            ...event,
            "xaxis.range[0]": undefined,
          },
        })
      } else {
        widgetMgr.setExtraWidgetInfo(element, RELAYOUT_KEY, {
          [RELAYOUT_KEY]: { ...event },
        })
      }
    }
  }

  return (
    <Plot
      key={isFullScreen ? "fullscreen" : "original"}
      className="stPlotlyChart"
      data={data}
      layout={layout}
      config={config}
      frames={frames}
      onSelected={
        element.isSelectEnabled || !disabled ? handleSelect : () => {}
      }
      onDeselect={
        element.isSelectEnabled || !disabled ? handleDoubleClick : () => {}
      }
      onDoubleClick={
        element.isSelectEnabled || !disabled ? handleDoubleClick : () => {}
      }
      onRelayout={
        element.isSelectEnabled || !disabled ? handleRelayout : () => {}
      }
    />
  )
}

export function PlotlyChart({
  width,
  element,
  height,
  isFullScreen,
  widgetMgr,
  disabled,
}: PlotlyChartProps): ReactElement {
  switch (element.chart) {
    case "url":
      return renderIFrame({
        url: element.url as string,
        height,
        width,
      })
    case "figure":
      return (
        <PlotlyFigure
          width={width}
          element={element}
          height={height}
          isFullScreen={isFullScreen}
          widgetMgr={widgetMgr}
          disabled={disabled}
        />
      )
    default:
      throw new Error(`Unrecognized PlotlyChart type: ${element.chart}`)
  }
}

export default withFullScreenWrapper(PlotlyChart)
