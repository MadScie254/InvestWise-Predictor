import React, { useState, useEffect } from 'react';import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { toast } from 'react-toastify';
import api from '../utils/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState({
    totalPredictions: 0,
    accuracyRate: 0,
    avgReturn: 0,
    activeInvestments: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [predictionsResponse, statsResponse] = await Promise.all([
        api.get('/api/v1/predictions/'),
        api.get('/api/v1/dashboard/stats/'),
      ]);
      
      setPredictions(predictionsResponse.data.results || []);
      setStats(statsResponse.data || stats);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Investment Returns',
        data: [12, 19, 3, 5, 2, 3],
        borderColor: 'rgb(106, 13, 173)',
        backgroundColor: 'rgba(106, 13, 173, 0.2)',
      },
    ],
  };

  const sectorData = {
    labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Agriculture'],
    datasets: [
      {
        data: [30, 20, 25, 15, 10],
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
        ],
      },
    ],
  };

  if (loading) {
    return (
      <Container className="mt-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="dashboard-container mt-4">
      <Row className="mb-4">
        <Col>
          <h1 className="dashboard-title">Investment Dashboard</h1>
          <p className="text-muted">Welcome back! Here's your investment overview.</p>
        </Col>
      </Row>

      {/* Stats Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stats-card">
            <Card.Body>
              <div className="d-flex justify-content-between">
                <div>
                  <h6 className="text-muted">Total Predictions</h6>
                  <h3 className="text-primary">{stats.totalPredictions}</h3>
                </div>
                <div className="stats-icon">
                  <i className="fas fa-chart-line"></i>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <Card.Body>
              <div className="d-flex justify-content-between">
                <div>
                  <h6 className="text-muted">Accuracy Rate</h6>
                  <h3 className="text-success">{stats.accuracyRate}%</h3>
                </div>
                <div className="stats-icon">
                  <i className="fas fa-bullseye"></i>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <Card.Body>
              <div className="d-flex justify-content-between">
                <div>
                  <h6 className="text-muted">Avg Return</h6>
                  <h3 className="text-warning">{stats.avgReturn}%</h3>
                </div>
                <div className="stats-icon">
                  <i className="fas fa-dollar-sign"></i>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <Card.Body>
              <div className="d-flex justify-content-between">
                <div>
                  <h6 className="text-muted">Active Investments</h6>
                  <h3 className="text-info">{stats.activeInvestments}</h3>
                </div>
                <div className="stats-icon">
                  <i className="fas fa-coins"></i>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col lg={8}>
          <Card>
            <Card.Header>
              <h5>Investment Performance</h5>
            </Card.Header>
            <Card.Body>
              <Line data={chartData} options={{ responsive: true }} />
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card>
            <Card.Header>
              <h5>Sector Distribution</h5>
            </Card.Header>
            <Card.Body>
              <Doughnut data={sectorData} options={{ responsive: true }} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Predictions */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5>Recent Predictions</h5>
              <Button variant="primary" href="/predict">
                New Prediction
              </Button>
            </Card.Header>
            <Card.Body>
              {predictions.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Sector</th>
                        <th>Country</th>
                        <th>Predicted Value</th>
                        <th>Status</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {predictions.slice(0, 5).map((prediction) => (
                        <tr key={prediction.id}>
                          <td>{prediction.sector}</td>
                          <td>{prediction.country}</td>
                          <td>${prediction.predicted_value}</td>
                          <td>
                            <span className={`badge bg-${
                              prediction.status === 'completed' ? 'success' :
                              prediction.status === 'processing' ? 'warning' :
                              'secondary'
                            }`}>
                              {prediction.status}
                            </span>
                          </td>
                          <td>{new Date(prediction.created_at).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted">No predictions yet. Create your first prediction!</p>
                  <Button variant="primary" href="/predict">
                    Get Started
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;

