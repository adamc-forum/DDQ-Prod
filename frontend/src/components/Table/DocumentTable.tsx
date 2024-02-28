import React, { useMemo } from "react";
import "./document-table.css";
import { useTable, Column, Row } from "react-table";
import { ClientDocument } from "../../pages/DocumentPage";
import { formatDate } from "../../utils";

interface DocumentTableProps {
  data: ClientDocument[];
  selectedDocumentId: string | null;
  onSelectionChange: (documentId: string | null) => void;
}

const DocumentTable: React.FC<DocumentTableProps> = ({
  data,
  selectedDocumentId,
  onSelectionChange,
}) => {
  const columns: Column<ClientDocument>[] = useMemo(
    () => [
      {
        Header: "",
        id: "selection",
        Cell: ({ row }: { row: Row<ClientDocument> }) => (
          <input
            type="checkbox"
            checked={selectedDocumentId === row.original.id}
            onChange={() => {
              const newSelectedId = selectedDocumentId === row.original.id ? null : row.original.id;
              onSelectionChange(newSelectedId);
            }}
          />
        ),
      },
      {
        Header: "Client Name",
        accessor: "clientName",
      },
      {
        Header: "Document Name",
        accessor: "documentName",
      },
      {
        Header: "Date",
        accessor: "date",
        Cell: ({ value }) => <span>{formatDate(value)}</span>,
      },
    ],
    [selectedDocumentId, onSelectionChange]
  );

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable({
      columns,
      data,
    });

  return (
    <div className="document-table">
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <th {...column.getHeaderProps()}>{column.render("Header")}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default DocumentTable;
