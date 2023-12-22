import React, { useState } from 'react';
import ResultItem from '../ResultItem/ResultItem';
import './search-response.css';

const SearchResponse = ({ response }) => {
    console.log(`Recieved response: ${response}`)
    return (
        <div className="search-response">
            {response}
        </div>
    )
}

export default SearchResponse