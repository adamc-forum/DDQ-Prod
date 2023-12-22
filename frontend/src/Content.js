import React, { useState } from 'react';
import API from './Api';
import Result from './Components/Result';
import Response from './Components/Response';

const Content = () => {
  const [data, setData] = useState(null);
  const [response, setResponse] = useState('')
  const [results, setResults] = useState([])
  const [query, setQuery] = useState('');

  const fetchData = async (userQuery) => {
    try {
      const response = await API.get(`/search?query=${userQuery}`);
      setData(response.data);
      // console.log(response.data)
      setResults(response.data.results)
      setResponse(response.data.response)
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchData(query);
  };

  return (
    <>
      <p>Forum DDQ Search AI</p>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder="Enter your query"
        />
        <button type="submit">Search</button>
      </form>
      <div className='content'>
        <Response response={response} />
        <Result results={results} />
      </div>
    </>
  );
};

export default Content;
