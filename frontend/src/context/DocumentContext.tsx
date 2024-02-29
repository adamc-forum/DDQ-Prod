import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
} from "react";
import API from "../Api";
import { ClientDocument } from "../pages/DocumentPage";

interface DocumentContextType {
  documents: ClientDocument[];
  refetchDocuments: () => void;
}

const DocumentContext = createContext<DocumentContextType | undefined>(
  undefined
);

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({
  children,
}) => {
  const [documents, setDocuments] = useState<ClientDocument[]>([]);

  useEffect(() => {
    refetchDocuments();
  }, []);

  const refetchDocuments = useCallback(() => {
    API.get("/documents")
      .then((response) => {
        setDocuments(response.data.clientDocuments);
      })
      .catch((error) => {
        console.error("Error fetching documents:", error);
      });
  }, []);

  return (
    <DocumentContext.Provider value={{ documents, refetchDocuments }}>
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocumentContext = () => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error(
      "useDocumentContext must be used within a DocumentProvider"
    );
  }
  return context;
};
