import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Paper, CircularProgress, Divider, Chip } from '@mui/material';
import axios from 'axios';

const API_BASE_URL = '/sections'; // Use a relative base path

function SectionLookup() {
  const [sectionNumber, setSectionNumber] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLookup = async () => {
    if (!sectionNumber.trim()) {
      setError('Please enter a section number.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/${sectionNumber.trim()}`);
      setResult(response.data);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError(`Section '${sectionNumber.trim()}' not found.`);
      } else {
        setError('Failed to fetch section details. Please ensure the backend is running.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        BNS Section Lookup
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
        Enter a BNS section number (e.g., 101, 63) to retrieve its full details.
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          label="Enter BNS Section Number"
          value={sectionNumber}
          onChange={(e) => setSectionNumber(e.target.value)}
          variant="outlined"
          onKeyPress={(e) => e.key === 'Enter' && handleLookup()}
        />
        <Button
          variant="contained"
          onClick={handleLookup}
          disabled={loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Lookup'}
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {result && (
        <Box>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom>
            Section {result.bns_section_number}: {result.bns_section_title}
          </Typography>
          <Typography variant="body1" sx={{ my: 2, whiteSpace: 'pre-wrap' }}>
            {result.bns_section_text}
          </Typography>
          <Typography variant="subtitle2" color="text.secondary">
            Category: {result.crime_category}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
            <Typography variant="subtitle2" sx={{ mr: 1 }}>Keywords:</Typography>
            {Array.isArray(result.keywords) && result.keywords.map((keyword) => (
              <Chip key={keyword} label={keyword} size="small" />
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
}

export default SectionLookup; 