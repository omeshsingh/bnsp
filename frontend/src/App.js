import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import KeywordSearch from './components/KeywordSearch'; // Import the new component
import AIAnalysis from './components/AIAnalysis'; // Import the new component
import SectionLookup from './components/SectionLookup'; // Import the new component
import IPCtoBNSConverter from './components/IPCtoBNSConverter'; // Import the new component

// function KeywordSearch() {
//   return <div>Keyword Search Page (to be implemented)</div>;
// }

// function AIAnalysis() {
//   return <div>AI Analysis Page (to be implemented)</div>;
// }

// function SectionLookup() {
//   return <div>Section Lookup Page (to be implemented)</div>;
// }

function App() {
  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Police Assist BNS
          </Typography>
          <Button color="inherit" component={Link} to="/">Keyword Search</Button>
          <Button color="inherit" component={Link} to="/ai-analysis">AI Analysis</Button>
          <Button color="inherit" component={Link} to="/section-lookup">Section Lookup</Button>
          <Button color="inherit" component={Link} to="/ipc-to-bns">IPC→BNS Converter</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<KeywordSearch />} />
          <Route path="/ai-analysis" element={<AIAnalysis />} />
          <Route path="/section-lookup" element={<SectionLookup />} />
          <Route path="/ipc-to-bns" element={<IPCtoBNSConverter />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
