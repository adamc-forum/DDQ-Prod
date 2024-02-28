import "../styles/global.css";
import "./document-page.css";
import API from "../Api";
import React, { useEffect, useState } from "react";
import Spinner from "../components/Spinner/Spinner";
import DocumentTable from "../components/Table/DocumentTable";
import TableBtnGroup from "../components/Table/TableBtnGroup";

export interface ClientDocument {
  id: string;
  clientName: string;
  documentName: string;
  date: string;
}

function DocumentPage() {
  const [documents, setDocuments] = useState<ClientDocument[]>([]); // State to store fetched data
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    null
  );

  const handleSelectionChange = (documentId: string | null) => {
    setSelectedDocumentId(documentId);
    console.log(documentId);
  };

  useEffect(() => {
    setIsLoading(true);
    API.get("/documents")
      .then((response) => {
        const clientDocuments: ClientDocument[] =
          response.data.clientDocuments.map((doc: ClientDocument) => ({
            ...doc,
            id: `${doc.clientName}_${doc.documentName}_${doc.date}`, // Concatenate to form the id
          }));
        setDocuments(clientDocuments);
      })
      .catch((error) => console.error("Error fetching documents:", error))
      .finally(() => {
        console.log(documents);
        setIsLoading(false);
      });
  }, []);

  return (
    <>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="document-page">
          <TableBtnGroup
            onAdd={() => console.log("Add Document")}
            onDelete={() => console.log(`Delete Document ${selectedDocumentId}`)}
            selectedDocumentId={selectedDocumentId}
          />
          <DocumentTable
            data={documents}
            selectedDocumentId={selectedDocumentId}
            onSelectionChange={handleSelectionChange}
          />
        </div>
      )}
    </>
  );
}

export default DocumentPage;
