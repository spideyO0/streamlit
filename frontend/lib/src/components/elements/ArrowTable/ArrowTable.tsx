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

import React, { ReactElement } from "react"

import range from "lodash/range"

import { Quiver } from "@streamlit/lib/src/dataframes/Quiver"

import {
  StyledEmptyTableCell,
  StyledTable,
  StyledTableCell,
  StyledTableCellHeader,
  StyledTableContainer,
} from "./styled-components"

export interface TableProps {
  element: Quiver
  border: boolean
}

export function ArrowTable(props: Readonly<TableProps>): ReactElement {
  const table = props.element
  const border = props.border
  const { cssId, cssStyles, caption } = table
  const { headerRows, rows, columns } = table.dimensions
  const allRows = range(rows)
  const columnHeaders = allRows.slice(0, headerRows)
  const dataRows = allRows.slice(headerRows)

  return (
    <StyledTableContainer className="stTable" data-testid="stTable">
      {cssStyles && <style>{cssStyles}</style>}
      <StyledTable
        id={cssId}
        tableBorder={border}
        data-testid="stTableStyledTable"
      >
        {caption && (
          <caption>
            <small>{caption}</small>
          </caption>
        )}
        {columnHeaders.length > 0 && (
          <thead>
            {columnHeaders.map(rowIndex =>
              generateTableRow(table, rowIndex, columns, border)
            )}
          </thead>
        )}
        <tbody>
          {dataRows.length === 0 ? (
            <tr>
              <StyledEmptyTableCell
                data-testid="stTableStyledEmptyTableCell"
                colSpan={columns || 1}
              >
                empty
              </StyledEmptyTableCell>
            </tr>
          ) : (
            dataRows.map(rowIndex =>
              generateTableRow(table, rowIndex, columns, border)
            )
          )}
        </tbody>
      </StyledTable>
    </StyledTableContainer>
  )
}

function generateTableRow(
  table: Quiver,
  rowIndex: number,
  columns: number,
  border?: boolean
): ReactElement {
  return (
    <tr key={rowIndex}>
      {range(columns).map(columnIndex =>
        generateTableCell(table, rowIndex, columnIndex, border)
      )}
    </tr>
  )
}

function generateTableCell(
  table: Quiver,
  rowIndex: number,
  columnIndex: number,
  border?: boolean
): ReactElement {
  const {
    type,
    cssId,
    cssClass,
    content,
    contentType,
    displayContent,
    field,
  } = table.getCell(rowIndex, columnIndex)

  const formattedContent =
    displayContent || Quiver.format(content, contentType, field)

  const { headerColumns } = table.dimensions
  const cellDataType =
    table.types.data[columnIndex - headerColumns]?.pandas_type
  const isNumeric = cellDataType === "int64" || cellDataType === "float64"

  const style: React.CSSProperties = {
    textAlign: isNumeric ? "right" : "left",
  }

  switch (type) {
    case "blank": {
      return (
        <StyledTableCellHeader
          key={columnIndex}
          className={cssClass}
          tableBorder={border}
        >
          &nbsp;
        </StyledTableCellHeader>
      )
    }
    case "index": {
      return (
        <StyledTableCellHeader
          key={columnIndex}
          scope="row"
          id={cssId}
          className={cssClass}
          tableBorder={border}
        >
          {formattedContent}
        </StyledTableCellHeader>
      )
    }
    case "columns": {
      return (
        <StyledTableCellHeader
          key={columnIndex}
          scope="col"
          className={cssClass}
          style={style}
          tableBorder={border}
        >
          {formattedContent}
        </StyledTableCellHeader>
      )
    }
    case "data": {
      return (
        <StyledTableCell
          key={columnIndex}
          id={cssId}
          style={style}
          tableBorder={border}
        >
          {formattedContent}
        </StyledTableCell>
      )
    }
    default: {
      throw new Error(`Cannot parse type "${type}".`)
    }
  }
}

export default ArrowTable
