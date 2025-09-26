import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Index from './pages/index';
import DonorDashboard from './pages/donor-dashboard';
import HospitalDashboard from './pages/hospital-dashboard';
import SOS from './pages/sos';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/donor-dashboard" element={<DonorDashboard />} />
                <Route path="/hospital-dashboard" element={<HospitalDashboard />} />
                <Route path="/sos" element={<SOS />} />
            </Routes>
        </Router>
    );
};

export default App;