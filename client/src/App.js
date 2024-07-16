import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/navbar/Navbar'; // Corrected path
import {
    Create,
    Dashboard,
    Landing,
    Login,
    Register,
    Status,
    Exam,
    EditTest  
} from './containers';
import './App.css';
import SelectRole from './components/oAuth/SelectRole';


const App = () => {
    return (
        <div className="App">
            <BrowserRouter>                 
                <Routes>
                    <Route path="/" element={<Landing />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/create" element={<Create />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/exam/:formLinkCode" element={<Exam />} />
                    <Route path="/editTest" element={<EditTest />} />
                    <Route path="/selectRole" element={<SelectRole />} />
                    <Route path="/status" element={<Status />} />
                </Routes>
            </BrowserRouter>
        </div>
    );
};

export default App;
