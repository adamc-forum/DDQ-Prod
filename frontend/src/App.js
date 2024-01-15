import './styles/global.css';
import './app.css';
import API from './Api.js';
import SearchForm from './components/SearchForm/SearchForm';
import SearchResults from './components/SearchResults/SearchResults';
import React, { useState } from 'react';
import SearchResponse from './components/SearchResponse/SearchResponse';
import Spinner from './components/Spinner/Spinner';
import Header from './components/Header/Header';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [llmResponse, setLlmResponse] = useState(''); // State to store the additional response
  const [isLoading, setIsLoading] = useState(false)

  const fetchData = async (userQuery) => {
    setIsLoading(true); // Start loading
    try {
      const response = await API.get(`/search?query=${userQuery}`);
      if(response.data && response.data.results) {
        setResults(response.data.results); // Update the results state
      }
      if(response.data && response.data.response) {
        setLlmResponse(response.data.response); // Update the LLM response state
      }
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
    setIsLoading(false); // Stop loading
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if(!isLoading) {
      fetchData(query);
      setQuery(''); // Clear the input field
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
      />
      {isLoading ? (
        <Spinner /> // Display spinner while loading
      ) : (
        <>
          {llmResponse && <SearchResponse response={llmResponse} />}
          <SearchResults results={results} />
        </>
      )}
    </div>
  );
}

export default App;
