import React, { useState } from "react";
import "./upload-page.css";
import API from "../Api";

function UploadPage() {
  const [clientName, setClientName] = useState<string>("");
  const [documentName, setDocumentName] = useState<string>("");
  const [date, setDate] = useState<string>("");
  const [docxFile, setDocxFile] = useState<File | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);

  const handleDocxFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      setDocxFile(files[0]);
    }
  };

  const handlePdfFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      setPdfFile(files[0]);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("client_name", clientName);
    formData.append("document_name", documentName);
    formData.append("date", date);
    if (docxFile) formData.append("docx_document", docxFile);
    if (pdfFile) formData.append("pdf_document", pdfFile);

    try {
      const response = await API.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 200) {
        console.log("Upload successful:", response.data);
        // Handle success, e.g., show a success message or clear the form
      } else {
        console.error("Upload failed:", response.data.error);
        // Handle error, e.g., show an error message
      }
    } catch (error) {
      console.error("Error uploading document:", error);
      // Handle network error, e.g., show an error message
    }

    console.log({ clientName, documentName, date, docxFile, pdfFile });
  };

  return (
    <div className="upload-page">
      <form onSubmit={handleSubmit} className="upload-page__form">
        <div>
          <label htmlFor="clientName">Client Name:</label>
          <input
            type="text"
            id="clientName"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="documentName">Document Name:</label>
          <input
            type="text"
            id="documentName"
            value={documentName}
            onChange={(e) => setDocumentName(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="date">Date:</label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="docxFile">Upload Document (DOCX):</label>
          <input type="file" id="docxFile" onChange={handleDocxFileChange} />
        </div>
        <div>
          <label htmlFor="pdfFile">Reupload Document (PDF):</label>
          <input type="file" id="pdfFile" onChange={handlePdfFileChange} />
        </div>
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default UploadPage;
