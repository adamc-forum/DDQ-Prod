import React from 'react';

const Result = ({ results }) => { // Destructure the results from props
    console.log(`Recieved results: ${results}`);
    const results_div = results.map((item, index) => (
        <div key={index} className='search-result'>
            <div>
                {`Search Result #${index + 1}`}
            </div>
            <div>
                {`Similarity Score: ${item.similarityScore}, File: ${item.filename[0]}, Page Number: ${item.page[0]}`}
            </div>
            <div>
                {`${item.content[0]}`}
            </div>
        </div>
    ));
    return (
        <div className='search-result-container'>
            {results_div}
        </div>
    );
};

export default Result;