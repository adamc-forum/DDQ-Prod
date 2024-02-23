import React from "react";
import "./search-field.css";

const SearchField = ({
  query,
  setQuery,
}: {
  query: string;
  setQuery: React.Dispatch<React.SetStateAction<string>>;
}) => {
  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Enter your search query"
      className="search-form__input"
    />
  );
};

export default SearchField;
