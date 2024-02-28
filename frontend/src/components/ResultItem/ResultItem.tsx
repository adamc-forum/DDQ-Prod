import React, { useState } from "react";
import "./result-item.css";
import { formatDate } from "../../utils";
import API from "../../Api";
import Spinner from "../Spinner/Spinner";

const toThreeDecimalsPercentage = (num: number) => {
  return (Math.floor(num * 1000) / 1000) * 100;
};

export interface Result {
  similarityScore: number;
  clientName: string[];
  documentName: string[];
  page: number[];
  date: string[];
  content: string[];
}

const ResultItem = ({ item, index }: { item: Result; index: number }) => {
  const [isLoading, setIsLoading] = useState<boolean>(false); // Add loading state

  const similarityScore = toThreeDecimalsPercentage(item.similarityScore);
  const date = formatDate(item.date[0]);

  // Updated handleClick to use fetchDocumentUrl
  const handleClick = async () => {
    await fetchDocumentUrl(`{generate your user query string here if needed}`);
  }

  const fetchDocumentUrl = async (userQuery: string) => {
    setIsLoading(true); // Start loading
    try {
      const response = await API.get(
        `/documentUrl?client_name=${encodeURIComponent(item.clientName[0])}&document_name=${encodeURIComponent(item.documentName[0])}&date=${encodeURIComponent(date)}&page_number=${item.page[0]}`
      );
      window.open(response.data.documentUrl, "_blank");
    } catch (error) {
      console.error("Error fetching document URL: ", error);
    }
    setIsLoading(false); // Stop loading
  };

  return (
    <div className="search-result__result-item" onClick={handleClick}>
      <div>{`Search Result #${index + 1}`}</div>
      <div>
        {`Similarity Score: ${similarityScore}%, Client: ${item.clientName[0]}, Document: ${item.documentName[0]}, Date: ${date}, Page Number: ${item.page[0]}`}
      </div>
      <div>{`${item.content[0]}`}</div>
    </div>
  );
};

export default ResultItem;