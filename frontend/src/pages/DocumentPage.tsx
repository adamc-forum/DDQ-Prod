import "../styles/global.css";
import "./document-page.css";
import API from "../Api";
import React, { useEffect, useState } from "react";
import Spinner from "../components/Spinner/Spinner";
import DocumentTable from "../components/Table/DocumentTable";
import TableBtnGroup from "../components/Table/TableBtnGroup";
import { useDocumentContext } from "../context/DocumentContext";
import { useNavigate } from "react-router-dom";

export interface ClientDocument {
  id: string;
  clientName: string;
  documentName: string;
  date: string;
}

function DocumentPage() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    null
  );
  const { documents, refetchDocuments } = useDocumentContext();
  const [idDocuments, setIdDocuments] = useState<ClientDocument[]>([]);
  const navigate = useNavigate(); // Create a navigation function

  const handleSelectionChange = (documentId: string | null) => {
    setSelectedDocumentId(documentId);
    console.log(documentId);
  };

  useEffect(() => {
    const clientDocuments: ClientDocument[] = documents.map(
      (doc: ClientDocument) => ({
        ...doc,
        id: `${doc.clientName}_${doc.documentName}_${doc.date}`, // Concatenate to form the id
      })
    );
    setIdDocuments(clientDocuments);
  }, [documents]);

  return (
    <>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="document-page">
          <TableBtnGroup
            onAdd={() => navigate("/upload")}
            onDelete={() =>
              console.log(`Delete Document ${selectedDocumentId}`)
            }
            selectedDocumentId={selectedDocumentId}
          />
          <DocumentTable
            data={idDocuments}
            selectedDocumentId={selectedDocumentId}
            onSelectionChange={handleSelectionChange}
          />
        </div>
      )}
    </>
  );
}

export default DocumentPage;
