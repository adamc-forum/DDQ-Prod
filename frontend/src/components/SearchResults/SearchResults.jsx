import React, { useEffect, useState } from "react";
import ResultItem from "../ResultItem/ResultItem";
import { SORT_BY_DATE, SORT_BY_SIMILARITY } from "../../constants.js";
import "./search-results.css";

const SearchResults = ({ results, sortOption }) => {
  const [ResultItems, setResultItems] = useState();
  useEffect(() => {
    const sortedResults = [...results].sort((a, b) => {
      if (sortOption === SORT_BY_DATE) {
        // console.log(new Date(a.date[0]).getTime() - new Date(b.date[0]).getTime());
        return new Date(b.date[0]).getTime() - new Date(a.date[0]).getTime();
      } else if (sortOption === SORT_BY_SIMILARITY) {
        return b.similarityScore - a.similarityScore;
      }
      return 0;
    });
    setResultItems(
      sortedResults.map((item, index) => (
        <ResultItem index={index} item={item} key={index} />
      ))
    );
  }, [results, sortOption]);

  return (
    <div key={ResultItems}>
      <p className="body-header">Search Results:</p>
      <div className="search-result">{ResultItems}</div>
    </div>
  );
};

export default SearchResults;
