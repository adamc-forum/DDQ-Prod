import React, { useEffect, useState } from "react";
import ResultItem, { Result } from "../ResultItem/ResultItem";
import { SortOption } from "../../constants";
import "./search-results.css";

const SearchResults = ({
  results,
  sortOption,
}: {
  results: Result[];
  sortOption: SortOption;
}) => {
  const [sortedResults, setSortedResults] = useState<Result[]>();
  useEffect(() => {
    setSortedResults(
      [...results].sort((a, b) => {
        if (sortOption === SortOption.Date) {
          // console.log(new Date(a.date[0]).getTime() - new Date(b.date[0]).getTime());
          return new Date(b.date[0]).getTime() - new Date(a.date[0]).getTime();
        } else if (sortOption === SortOption.Similarity) {
          return b.similarityScore - a.similarityScore;
        }
        return 0;
      })
    );
  }, [results, sortOption]);

  return (
    <div>
      <p className="body-header">Search Results:</p>
      <div className="search-result">
        {sortedResults?.map((item, index) => (
          <ResultItem index={index} item={item} key={index} />
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
