import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Paper, CircularProgress, List, ListItem, ListItemText, Divider } from '@mui/material';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

function AIAnalysis() {
  const [description, setDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalysis = async () => {
    if (!description.trim()) {
      setError('Please enter a crime description.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/analyse-description`, {
        description: description,
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to get analysis. Please ensure the backend is running and the description is detailed enough.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        AI-Powered Crime Description Analysis
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
        Enter a detailed description of the crime, and the AI will suggest relevant BNS sections with a legal analysis.
      </Typography>

      <TextField
        fullWidth
        multiline
        rows={8}
        label="Enter detailed crime description here..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        variant="outlined"
        sx={{ mb: 2 }}
      />

      <Button
        variant="contained"
        onClick={handleAnalysis}
        disabled={loading}
        sx={{ minWidth: 150, mb: 3 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Analyse Description'}
      </Button>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {result && (
        <Box>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom>
            Analysis Result
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 3, whiteSpace: 'pre-wrap' }}>
            <Typography variant="body1">{result.analysis}</Typography>
          </Paper>

          <Typography variant="h6" gutterBottom>
            Suggested BNS Sections
          </Typography>
          <List>
            {result.suggested_sections.map((section) => (
              <ListItem key={section.bns_section_number} divider>
                <ListItemText
                  primary={`Section ${section.bns_section_number}: ${section.bns_section_title}`}
                  secondary={`Category: ${section.crime_category}`}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
}

export default AIAnalysis; 