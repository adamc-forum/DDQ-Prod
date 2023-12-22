import React, { useState } from 'react';
import ResultItem from '../ResultItem/ResultItem';
import './search-results.css';

const SearchResults = ({ results }) => {
    const ResultItems = results.map((item, index) => (
        <ResultItem index={index} item={item} key={index} />
    ));
    console.log(ResultItems)
    return (
        <div className="search-result">
            {ResultItems}
        </div>
    )
}

export default SearchResults