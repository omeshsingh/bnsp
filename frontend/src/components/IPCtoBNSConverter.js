import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Paper, CircularProgress, List, ListItem, ListItemText, Divider } from '@mui/material';
import axios from 'axios';

const API_URL = '/convert-ipc-to-bns'; // Use a relative path

function IPCtoBNSConverter() {
  const [ipcSection, setIpcSection] = useState('');
  const [description, setDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConvert = async () => {
    if (!ipcSection.trim()) {
      setError('Please enter an IPC section number.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(API_URL, {
        ipc_section: ipcSection.trim(),
        description: description.trim() || undefined,
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to convert IPC to BNS. Please ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        IPC to BNS Section Converter
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
        Enter an IPC section number and (optionally) a description. The AI will suggest the most relevant BNS section(s) and provide reasoning.
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="IPC Section Number"
          value={ipcSection}
          onChange={(e) => setIpcSection(e.target.value)}
          variant="outlined"
          required
        />
        <TextField
          label="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          variant="outlined"
          fullWidth
        />
        <Button
          variant="contained"
          onClick={handleConvert}
          disabled={loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Convert'}
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
            AI Analysis
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

export default IPCtoBNSConverter; 