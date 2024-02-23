import React from "react";
import "./search-response.css";

const SearchResponse = ({ response }: { response: string }) => {
  console.log(`Recieved response: ${response}`);
  return (
    <div>
      <p className="body-header">GPT Response:</p>
      <div className="search-response">{response}</div>
    </div>
  );
};

export default SearchResponse;
