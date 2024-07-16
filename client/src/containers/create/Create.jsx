import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import logo from './../../assets/logofont.svg';
import { CommonInput, CopyLink, CtaButton, Navbar } from '../../components';
import './create.css';

const inputField = [    
    
    { label: 'Test Name', name: 'testName' },
    { label: 'Test Form Link', name: 'testLink' },    
    { label: 'mm/dd/yy - hh:mm', name: 'startTime' },
    { label: 'Duration', name: 'duration' },    
    { label: 'Total Candidates', name: 'totalCandidates' },    
    { label: 'Keywords', name: 'keywords' },    
];

const Create = () => {
    const email = localStorage.getItem('email');
    const [message, setMessage] = useState("");
    const [testCode, setTestCode] = useState("");
    const [formData, setFormData] = useState({    
        email: email,    
        
        testName: '',
        testLink: '',        
        startTime: '',
        duration: '',    
        totalCandidates: '',        
        keywords: ''   
    });
    const navigate = useNavigate();
    const isAuthenticated = !!localStorage.getItem('token');

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login');
        }
    }, [isAuthenticated, navigate]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;        
        setFormData({
            ...formData,
            [name]: value
        });        
    };    

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const emptyFields = Object.keys(formData).filter(key => !formData[key]);
            console.log(emptyFields);
            if(emptyFields.length !== 0){
                setMessage("Enter all the fields");
                return;
            }            
            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5000/api/create-test', formData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            setMessage(response.data.msg);
            console.log('Response from server:', response.data);
            if(response.status === 201){
                console.log(response.data.data.test_code);
                setTestCode(response.data.data.test_code);                
            }
        } catch (error) {
            console.error('There was an error creating the test!', error);
        }
    };

    const handleDone = () => {
        navigate('/');
    }

    return (
        <div className="client-create">
            <Navbar />
            {!testCode ? (
                <div className="create-form">
                    <h1 className="title-heading">Create a test</h1>
                    <form onSubmit={handleSubmit}>
                        <div className="input-fields">
                            {inputField.map((item, index) => (
                                <div key={index}>                                
                                    <CommonInput
                                        key={index}
                                        placeholderText={item.label}
                                        name={item.name}
                                        value={formData[item.name]}                                                                
                                        onChange={handleInputChange}
                                        type={"text"}
                                    />
                                </div>
                            ))}
                        </div>
                        {message && <p className='errorMessage'>{message}</p>}
                        <CtaButton text="Create" />
                    </form>
                </div>
            ) : (
                <div className="test-code-message">
                    <p className='success'>Test Created Successfully</p>
                    <CopyLink link={testCode}/>             
                </div>
            )}
        </div>
    );
};

export default Create;
