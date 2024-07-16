import React from 'react';
import './commoninput.css';

const CommonInput = React.forwardRef(({ placeholderText, id, name, onChange,type,value }, ref) => {
    return (
        <div>
            <span className='label'>{name}</span>
            <input
            type={type}
            id={id}
            name={name}            
            onChange={onChange}
            placeholder={placeholderText}
            ref={ref}
            value={value}
        />
        </div>
    );
});

export default CommonInput;
