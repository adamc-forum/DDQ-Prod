import React from 'react';

const Response = ({ response }) => { // Destructure the results from props
    console.log(`Recieved response: ${response}`);
    return (
        <div className='response-container'>
            {response}
        </div>
    );
};

export default Response;