import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../utils/api';

const PredictionForm = () => {
  const [formData, setFormData] = useState({
    sector: '',
    country: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const sectors = [
    'Technology',
    'Healthcare',
    'Finance',
    'Agriculture',
    'Energy',
    'Real Estate',
    'Manufacturing',
    'Tourism',
    'Education',
    'Transportation',
  ];

  const countries = [
    'Kenya',
    'United States',
    'United Kingdom',
    'Germany',
    'Japan',
    'China',
    'India',
    'Brazil',
    'Canada',
    'Australia',
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/v1/predictions/', formData);
      toast.success('Prediction created successfully!');
      navigate('/predictions');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white">
              <h4 className="mb-0">Create New Prediction</h4>
            </Card.Header>
            <Card.Body className="p-4">
              <p className="text-muted mb-4">
                Generate AI-powered investment predictions by selecting a sector and country.
              </p>

              {error && <Alert variant="danger">{error}</Alert>}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Sector *</Form.Label>
                  <Form.Select
                    name="sector"
                    value={formData.sector}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Choose a sector...</option>
                    {sectors.map((sector) => (
                      <option key={sector} value={sector}>
                        {sector}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Text className="text-muted">
                    Select the industry sector you want to analyze.
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Country *</Form.Label>
                  <Form.Select
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Choose a country...</option>
                    {countries.map((country) => (
                      <option key={country} value={country}>
                        {country}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Text className="text-muted">
                    Select the country for market analysis.
                  </Form.Text>
                </Form.Group>

                <div className="d-grid gap-2">
                  <Button
                    variant="primary"
                    type="submit"
                    size="lg"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        Generating Prediction...
                      </>
                    ) : (
                      'Generate Prediction'
                    )}
                  </Button>
                  <Button
                    variant="outline-secondary"
                    onClick={() => navigate('/predictions')}
                  >
                    View Existing Predictions
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PredictionForm;
