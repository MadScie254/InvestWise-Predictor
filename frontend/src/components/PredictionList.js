import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Form } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../utils/api';

const PredictionList = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/predictions/');
      setPredictions(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'P': { variant: 'secondary', text: 'Pending' },
      'PR': { variant: 'warning', text: 'Processing' },
      'C': { variant: 'success', text: 'Completed' },
      'F': { variant: 'danger', text: 'Failed' },
    };
    
    const statusInfo = statusMap[status] || { variant: 'secondary', text: status };
    return <Badge bg={statusInfo.variant}>{statusInfo.text}</Badge>;
  };

  const filteredPredictions = predictions.filter(prediction => {
    if (filter === 'all') return true;
    return prediction.status === filter;
  });

  if (loading) {
    return (
      <Container className="mt-5">
        <div className="text-center">
          <div className="spinner-border text-primary" />
          <p className="mt-2">Loading predictions...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2>Your Predictions</h2>
            <Button variant="primary" href="/predict">
              New Prediction
            </Button>
          </div>
        </Col>
      </Row>

      <Row className="mb-3">
        <Col md={4}>
          <Form.Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Predictions</option>
            <option value="P">Pending</option>
            <option value="PR">Processing</option>
            <option value="C">Completed</option>
            <option value="F">Failed</option>
          </Form.Select>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              {filteredPredictions.length === 0 ? (
                <div className="text-center py-5">
                  <h5 className="text-muted">No predictions found</h5>
                  <p className="text-muted">Create your first prediction to get started!</p>
                  <Button variant="primary" href="/predict">
                    Create Prediction
                  </Button>
                </div>
              ) : (
                <div className="table-responsive">
                  <Table hover>
                    <thead>
                      <tr>
                        <th>Sector</th>
                        <th>Country</th>
                        <th>Predicted Value</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPredictions.map((prediction) => (
                        <tr key={prediction.id}>
                          <td>
                            <strong>{prediction.sector}</strong>
                          </td>
                          <td>{prediction.country}</td>
                          <td>
                            {prediction.predicted_value ? (
                              <span className="text-success">
                                ${parseFloat(prediction.predicted_value).toLocaleString()}
                              </span>
                            ) : (
                              <span className="text-muted">-</span>
                            )}
                          </td>
                          <td>{getStatusBadge(prediction.status)}</td>
                          <td>
                            {new Date(prediction.created_at).toLocaleDateString()}
                          </td>
                          <td>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              href={`/predictions/${prediction.id}`}
                            >
                              View Details
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PredictionList;
