import React from "react";
import "./search-query.css";

const SearchQuery = ({ prevQuery }: { prevQuery: string }) => {
  return (
    <div>
      <p className="body-header">Query: </p>
      <p>{prevQuery}</p>
    </div>
  );
};

export default SearchQuery;
