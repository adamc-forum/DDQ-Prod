import "../styles/global.css";
import "../app.css";
import "./search-page.css";
import API from "../Api";
import SearchForm from "../components/SearchForm/SearchForm";
import SearchResults from "../components/SearchResults/SearchResults";
import React, { useState } from "react";
import SearchResponse from "../components/SearchResponse/SearchResponse";
import Spinner from "../components/Spinner/Spinner";
// import { testResults } from "../test.js";
import { SortOption, RESULT_COUNT_LIST, ResultCount } from "../constants";
import { Result } from "../components/ResultItem/ResultItem";
import SearchQuery from "../components/SearchQuery/SearchQuery";

function SearchPage() {
  const [query, setQuery] = useState<string>("");
  const [prevQuery, setPrevQuery] = useState<string>("");
  const [resultCount, setResultCount] = useState<ResultCount>(
    RESULT_COUNT_LIST[0]
  );
  const [results, setResults] = useState<Result[]>([]);
  const [llmResponse, setLlmResponse] = useState<string>(""); // State to store the additional response
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sortOption, setSortOption] = useState<SortOption>(
    SortOption.Similarity
  ); // Default to sorting by similarity
  const [clients, setClients] = useState<string[]>([]);

  const handleClientChange = (selectedClients: string[]) => {
    setClients(selectedClients);
  };

  const fetchData = async (userQuery: string) => {
    setIsLoading(true); // Start loading
    try {
      const response = await API.get(
        `/search?query=${userQuery}&result_count=${resultCount}&client_names=${clients.join(
          ","
        )}`
      );
      if (response.data && response.data.results) {
        setResults(response.data.results); // Update the results state
      }
      if (response.data && response.data.response) {
        setLlmResponse(response.data.response); // Update the LLM response state
      }
    } catch (error) {
      console.error("Error fetching data: ", error);
    }
    setIsLoading(false); // Stop loading
  };

  const handleSubmit = (event: React.KeyboardEvent | React.MouseEvent) => {
    if (event) event.preventDefault();
    if (!query) return;
    if (clients.length === 0) return;
    if (!isLoading) {
      setPrevQuery(query);
      fetchData(query);
    }
  };

  return (
    <div className="search-page">
      <SearchForm
        query={query}
        setQuery={setQuery}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
        resultCount={resultCount}
        setResultCount={setResultCount}
        sortOption={sortOption}
        setSortOption={setSortOption}
        handleClientChange={handleClientChange}
      />
      {isLoading ? (
        <Spinner /> // Display spinner while loading
      ) : (
        <div className="search-content-container">
          {!isLoading && prevQuery && <SearchQuery prevQuery={prevQuery} />}
          {llmResponse && <SearchResponse response={llmResponse} />}
          {results.length > 0 && (
            <SearchResults results={results} sortOption={sortOption} />
          )}
        </div>
      )}
    </div>
  );
}

export default SearchPage;
