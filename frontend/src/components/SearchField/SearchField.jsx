import React, { useState } from 'react';
import './search-field.css';

const SearchField = ({ query, setQuery }) => {
    return (
        <input 
            type="text" 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            placeholder="Enter your search query"
            className="search-form__input"
        />
    )
}

export default SearchField