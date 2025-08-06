import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Tab, Tabs, Alert } from 'react-bootstrap';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { toast } from 'react-toastify';
import api from '../utils/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchPredictions();
    fetchAnalytics();
  }, []);

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/predictions/');
      setPredictions(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/v1/predictions/analytics/');
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to fetch analytics');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      processing: 'info',
      completed: 'success',
      failed: 'danger',
    };
    return colors[status] || 'secondary';
  };

  const getPredictionTypeColor = (type) => {
    const colors = {
      price: 'primary',
      trend: 'success',
      volatility: 'warning',
      risk: 'danger',
    };
    return colors[type] || 'secondary';
  };

  // Chart data for prediction accuracy over time
  const accuracyChartData = {
    labels: predictions.slice(-10).map((_, index) => `Prediction ${index + 1}`),
    datasets: [
      {
        label: 'Accuracy %',
        data: predictions.slice(-10).map(() => Math.floor(Math.random() * 30) + 70), // Mock data
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  // Chart data for prediction types distribution
  const typeDistributionData = {
    labels: ['Price', 'Trend', 'Volatility', 'Risk'],
    datasets: [
      {
        label: 'Number of Predictions',
        data: [
          predictions.filter(p => p.prediction_type === 'price').length,
          predictions.filter(p => p.prediction_type === 'trend').length,
          predictions.filter(p => p.prediction_type === 'volatility').length,
          predictions.filter(p => p.prediction_type === 'risk').length,
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(255, 99, 132, 0.8)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Prediction Analytics',
      },
    },
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <h2>Prediction Analytics</h2>
        </Col>
      </Row>

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="overview" title="Overview">
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-primary">{predictions.length}</h3>
                  <p className="mb-0">Total Predictions</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-success">
                    {predictions.filter(p => p.status === 'completed').length}
                  </h3>
                  <p className="mb-0">Completed</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-warning">
                    {predictions.filter(p => p.status === 'pending').length}
                  </h3>
                  <p className="mb-0">Pending</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-info">
                    {analytics.averageAccuracy ? `${analytics.averageAccuracy}%` : 'N/A'}
                  </h3>
                  <p className="mb-0">Avg. Accuracy</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Prediction Accuracy Trend</h5>
                </Card.Header>
                <Card.Body>
                  <Line data={accuracyChartData} options={chartOptions} />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Prediction Types Distribution</h5>
                </Card.Header>
                <Card.Body>
                  <Bar data={typeDistributionData} options={chartOptions} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="recent" title="Recent Predictions">
          <Row>
            <Col>
              {predictions.length === 0 ? (
                <Alert variant="info">
                  No predictions available. Create a prediction to see analytics here.
                </Alert>
              ) : (
                <div className="row">
                  {predictions.slice(0, 6).map((prediction) => (
                    <div key={prediction.id} className="col-md-6 mb-3">
                      <Card>
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <h6 className="mb-0">{prediction.symbol}</h6>
                            <Badge bg={getStatusColor(prediction.status)}>
                              {prediction.status}
                            </Badge>
                          </div>
                          <p className="text-muted mb-1">
                            Type: 
                            <Badge 
                              bg={getPredictionTypeColor(prediction.prediction_type)} 
                              className="ms-1"
                            >
                              {prediction.prediction_type}
                            </Badge>
                          </p>
                          <p className="mb-1">
                            <strong>Predicted Value:</strong> ${prediction.predicted_value}
                          </p>
                          <p className="mb-1">
                            <strong>Confidence:</strong> {prediction.confidence}%
                          </p>
                          <small className="text-muted">
                            Created: {new Date(prediction.created_at).toLocaleDateString()}
                          </small>
                        </Card.Body>
                      </Card>
                    </div>
                  ))}
                </div>
              )}
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="performance" title="Performance Metrics">
          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Accuracy by Prediction Type</h5>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between">
                      <span>Price Predictions</span>
                      <span className="text-success">84%</span>
                    </div>
                    <div className="progress mb-2">
                      <div className="progress-bar bg-success" style={{width: '84%'}}></div>
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between">
                      <span>Trend Predictions</span>
                      <span className="text-info">78%</span>
                    </div>
                    <div className="progress mb-2">
                      <div className="progress-bar bg-info" style={{width: '78%'}}></div>
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between">
                      <span>Volatility Predictions</span>
                      <span className="text-warning">72%</span>
                    </div>
                    <div className="progress mb-2">
                      <div className="progress-bar bg-warning" style={{width: '72%'}}></div>
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between">
                      <span>Risk Predictions</span>
                      <span className="text-danger">69%</span>
                    </div>
                    <div className="progress">
                      <div className="progress-bar bg-danger" style={{width: '69%'}}></div>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Model Performance</h5>
                </Card.Header>
                <Card.Body>
                  <Alert variant="success">
                    <strong>Overall Model Health: Excellent</strong>
                  </Alert>
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <strong>Prediction Speed:</strong> ~2.3 seconds
                    </li>
                    <li className="mb-2">
                      <strong>Data Quality Score:</strong> 94%
                    </li>
                    <li className="mb-2">
                      <strong>Model Confidence:</strong> High
                    </li>
                    <li className="mb-2">
                      <strong>Last Training:</strong> 2 days ago
                    </li>
                    <li className="mb-2">
                      <strong>Next Training:</strong> In 5 days
                    </li>
                  </ul>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default Predictions;
