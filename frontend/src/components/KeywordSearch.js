import React, { useState, useEffect } from 'react';
import { Button, Box, Typography, Paper, List, ListItem, ListItemText, CircularProgress, Chip, Divider } from '@mui/material';
import axios from 'axios';

const API_URL = '/suggest-sections'; // Use a relative path

// A predefined list of common crime-related keywords.
// In a real application, this might be fetched from the backend or a static file.
const commonKeywords = [
  "Murder", "Theft", "Assault", "Kidnapping", "Robbery", "Fraud", "Extortion",
  "Burglary", "Arson", "Rioting", "Forgery", "Perjury", "Bribery", "Smuggling",
  "Trafficking", "Vandalism", "Trespassing", "Harassment", "Stalking",
  "Cybercrime", "Embezzlement", "Conspiracy", "Espionage", "Sedition",
  "Domestic Violence", "Dowry", "Abetment", "Negligence", "Rape", "Sexual Assault"
];

function KeywordSearch() {
  const [selectedKeywords, setSelectedKeywords] = useState(new Set());
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChipClick = (keyword) => {
    const newSelection = new Set(selectedKeywords);
    if (newSelection.has(keyword)) {
      newSelection.delete(keyword);
    } else {
      newSelection.add(keyword);
    }
    setSelectedKeywords(newSelection);
  };

  const handleSearch = async () => {
    if (selectedKeywords.size === 0) {
      setError('Please select at least one keyword.');
      return;
    }
    setError('');
    setLoading(true);
    setResults([]);

    try {
      const keywordList = Array.from(selectedKeywords);
      const response = await axios.post(API_URL, {
        keywords: keywordList,
      });
      setResults(response.data);
    } catch (err) {
      setError('Failed to fetch results. Please ensure the backend is running and CORS is configured.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        Select Keywords to Find BNS Sections
      </Typography>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3, p: 2, border: '1px solid #ddd', borderRadius: 2 }}>
        {commonKeywords.map((keyword) => (
          <Chip
            key={keyword}
            label={keyword}
            onClick={() => handleChipClick(keyword)}
            color={selectedKeywords.has(keyword) ? "primary" : "default"}
            variant={selectedKeywords.has(keyword) ? "filled" : "outlined"}
          />
        ))}
      </Box>

      <Button
        variant="contained"
        onClick={handleSearch}
        disabled={loading || selectedKeywords.size === 0}
        sx={{ minWidth: 150, mb: 3 }}
      >
        {loading ? <CircularProgress size={24} /> : `Search with ${selectedKeywords.size} Keywords`}
      </Button>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {results.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Search Results
          </Typography>
          <List>
            {results.map((section) => (
              <ListItem key={section.bns_section_number} divider>
                <ListItemText
                  primary={`Section ${section.bns_section_number}: ${section.bns_section_title}`}
                  secondary={
                    <>
                      <Typography variant="body2" color="text.primary" component="span" sx={{ my: 1, display: 'block' }}>
                        {section.bns_section_text}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Category: {section.crime_category} | Matched Keywords: {section.match_count}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
}

export default KeywordSearch; 