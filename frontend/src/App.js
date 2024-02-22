import "./styles/global.css";
import "./app.css";
import API from "./Api.js";
import SearchForm from "./components/SearchForm/SearchForm";
import SearchResults from "./components/SearchResults/SearchResults";
import React, { useState } from "react";
import SearchResponse from "./components/SearchResponse/SearchResponse";
import Spinner from "./components/Spinner/Spinner";
import Header from "./components/Header/Header";
import { testResults } from "./test.js";
import { SORT_BY_SIMILARITY, RESULT_COUNT_LIST } from "./constants.js";

function App() {
  const [query, setQuery] = useState("");
  const [prevQuery, setPrevQuery] = useState("");
  const [resultCount, setResultCount] = useState(RESULT_COUNT_LIST[0]);
  const [results, setResults] = useState([]);
  const [llmResponse, setLlmResponse] = useState(""); // State to store the additional response
  const [isLoading, setIsLoading] = useState(false);
  const [sortOption, setSortOption] = useState(SORT_BY_SIMILARITY); // Default to sorting by date
  const [clients, setClients] = useState([]);

  const handleClientChange = (selectedClients) => {
    setClients(selectedClients);
  };

  const fetchData = async (userQuery) => {
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

  const handleSubmit = (event) => {
    if (event) event.preventDefault();
    if (!query) return;
    if (clients.length === 0) return;
    if (!isLoading) {
      setPrevQuery(query);
      fetchData(query);
      setQuery(""); // Clear the input field
    }
  };

  return (
    <div className="app">
      <Header text={"REIIF DDQ Assistant"} />
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
          {!isLoading && prevQuery && (
            <div>
              <p className="body-header">Query: </p>
              <p>{prevQuery}</p>
            </div>
          )}
          {llmResponse && <SearchResponse response={llmResponse} />}
          {results.length > 0 && (
            <SearchResults results={results} sortOption={sortOption} />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
