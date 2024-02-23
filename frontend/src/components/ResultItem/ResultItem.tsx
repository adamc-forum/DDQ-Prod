import React from "react";
import "./result-item.css";

const toThreeDecimalsPercentage = (num: number) => {
  return (Math.floor(num * 1000) / 1000) * 100;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0"); // +1 because months are 0-indexed
  const year = date.getFullYear();

  return `${day}-${month}-${year}`;
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
  const similarityScore = toThreeDecimalsPercentage(item.similarityScore);
  const date = formatDate(item.date[0]);
  return (
    <div className="search-result__result-item">
      <div>{`Search Result #${index + 1}`}</div>
      <div>
        {`Similarity Score: ${similarityScore}%, Client: ${item.clientName[0]}, Document: ${item.documentName[0]}, Date: ${date}, Page Number: ${item.page[0]}`}
      </div>
      <div>{`${item.content[0]}`}</div>
    </div>
  );
};

export default ResultItem;
