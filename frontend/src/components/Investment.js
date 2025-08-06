import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, Modal, Form, Table } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../utils/api';

const Investment = () => {
  const [investments, setInvestments] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    symbol: '',
    company_name: '',
    shares: '',
    purchase_price: '',
    investment_type: 'stock',
  });

  useEffect(() => {
    fetchInvestments();
  }, []);

  const fetchInvestments = async () => {
    try {
      const response = await api.get('/api/v1/investments/');
      setInvestments(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to fetch investments');
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/api/v1/investments/', formData);
      toast.success('Investment added successfully!');
      setShowModal(false);
      setFormData({
        symbol: '',
        company_name: '',
        shares: '',
        purchase_price: '',
        investment_type: 'stock',
      });
      fetchInvestments();
    } catch (error) {
      toast.error('Failed to add investment');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this investment?')) {
      try {
        await api.delete(`/api/v1/investments/${id}/`);
        toast.success('Investment deleted successfully!');
        fetchInvestments();
      } catch (error) {
        toast.error('Failed to delete investment');
      }
    }
  };

  const getInvestmentTypeColor = (type) => {
    const colors = {
      stock: 'primary',
      bond: 'success',
      etf: 'info',
      crypto: 'warning',
      commodity: 'secondary',
    };
    return colors[type] || 'primary';
  };

  const calculateCurrentValue = (shares, purchasePrice) => {
    // This would integrate with real-time market data
    const currentPrice = purchasePrice * (1 + (Math.random() * 0.2 - 0.1)); // Mock calculation
    return (shares * currentPrice).toFixed(2);
  };

  const calculateGainLoss = (shares, purchasePrice) => {
    const currentValue = calculateCurrentValue(shares, purchasePrice);
    const investedValue = shares * purchasePrice;
    const gainLoss = currentValue - investedValue;
    return {
      value: gainLoss.toFixed(2),
      percentage: ((gainLoss / investedValue) * 100).toFixed(2),
      isPositive: gainLoss >= 0,
    };
  };

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2>My Investments</h2>
            <Button variant="primary" onClick={() => setShowModal(true)}>
              Add Investment
            </Button>
          </div>
        </Col>
      </Row>

      <Row>
        <Col>
          {investments.length === 0 ? (
            <Card>
              <Card.Body className="text-center">
                <p>No investments found. Add your first investment to get started!</p>
              </Card.Body>
            </Card>
          ) : (
            <Card>
              <Card.Body>
                <Table responsive striped>
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Company</th>
                      <th>Type</th>
                      <th>Shares</th>
                      <th>Purchase Price</th>
                      <th>Current Value</th>
                      <th>Gain/Loss</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {investments.map((investment) => {
                      const gainLoss = calculateGainLoss(
                        investment.shares,
                        investment.purchase_price
                      );
                      
                      return (
                        <tr key={investment.id}>
                          <td>
                            <strong>{investment.symbol}</strong>
                          </td>
                          <td>{investment.company_name}</td>
                          <td>
                            <Badge bg={getInvestmentTypeColor(investment.investment_type)}>
                              {investment.investment_type.toUpperCase()}
                            </Badge>
                          </td>
                          <td>{investment.shares}</td>
                          <td>${parseFloat(investment.purchase_price).toFixed(2)}</td>
                          <td>
                            ${calculateCurrentValue(investment.shares, investment.purchase_price)}
                          </td>
                          <td>
                            <span
                              className={
                                gainLoss.isPositive ? 'text-success' : 'text-danger'
                              }
                            >
                              ${gainLoss.value} ({gainLoss.percentage}%)
                            </span>
                          </td>
                          <td>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleDelete(investment.id)}
                            >
                              Delete
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Add Investment Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Investment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Symbol</Form.Label>
              <Form.Control
                type="text"
                name="symbol"
                value={formData.symbol}
                onChange={handleInputChange}
                placeholder="e.g., AAPL, TSLA"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Company Name</Form.Label>
              <Form.Control
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleInputChange}
                placeholder="e.g., Apple Inc."
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Investment Type</Form.Label>
              <Form.Select
                name="investment_type"
                value={formData.investment_type}
                onChange={handleInputChange}
                required
              >
                <option value="stock">Stock</option>
                <option value="bond">Bond</option>
                <option value="etf">ETF</option>
                <option value="crypto">Cryptocurrency</option>
                <option value="commodity">Commodity</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Number of Shares</Form.Label>
              <Form.Control
                type="number"
                name="shares"
                value={formData.shares}
                onChange={handleInputChange}
                placeholder="e.g., 100"
                min="0.01"
                step="0.01"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Purchase Price per Share</Form.Label>
              <Form.Control
                type="number"
                name="purchase_price"
                value={formData.purchase_price}
                onChange={handleInputChange}
                placeholder="e.g., 150.00"
                min="0.01"
                step="0.01"
                required
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Adding...' : 'Add Investment'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Investment;

