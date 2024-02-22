import React, { useState } from "react";
import ResultItem from "../ResultItem/ResultItem";
import "./search-response.css";

const SearchResponse = ({ response }) => {
  console.log(`Recieved response: ${response}`);
  return (
    <div>
      <p className="body-header">GPT Response:</p>
      <div className="search-response">{response}</div>
    </div>
  );
};

export default SearchResponse;
