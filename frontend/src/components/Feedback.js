import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Badge, ListGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../utils/api';

const Feedback = () => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    category: 'general',
    subject: '',
    message: '',
    rating: 5,
  });

  useEffect(() => {
    fetchFeedbacks();
  }, []);

  const fetchFeedbacks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/feedback/');
      setFeedbacks(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to fetch feedback history');
    } finally {
      setLoading(false);
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
    setSubmitting(true);

    try {
      await api.post('/api/v1/feedback/', formData);
      toast.success('Feedback submitted successfully! Thank you for your input.');
      setFormData({
        category: 'general',
        subject: '',
        message: '',
        rating: 5,
      });
      fetchFeedbacks();
    } catch (error) {
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      general: 'primary',
      bug: 'danger',
      feature: 'success',
      ui: 'info',
      performance: 'warning',
      data: 'secondary',
    };
    return colors[category] || 'primary';
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'warning',
      in_progress: 'info',
      resolved: 'success',
      closed: 'secondary',
    };
    return colors[status] || 'secondary';
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, index) => (
      <span
        key={index}
        className={index < rating ? 'text-warning' : 'text-muted'}
        style={{ fontSize: '1.2em' }}
      >
        ★
      </span>
    ));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <h2>Feedback & Support</h2>
          <p className="text-muted">
            Help us improve InvestWise by sharing your feedback, reporting issues, or suggesting new features.
          </p>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Submit Feedback</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="general">General Feedback</option>
                    <option value="bug">Bug Report</option>
                    <option value="feature">Feature Request</option>
                    <option value="ui">User Interface</option>
                    <option value="performance">Performance Issue</option>
                    <option value="data">Data Accuracy</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Subject</Form.Label>
                  <Form.Control
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    placeholder="Brief description of your feedback"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Message</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    placeholder="Provide detailed feedback, steps to reproduce issues, or suggestions..."
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Overall Rating</Form.Label>
                  <Form.Select
                    name="rating"
                    value={formData.rating}
                    onChange={handleInputChange}
                  >
                    <option value={5}>★★★★★ Excellent (5)</option>
                    <option value={4}>★★★★☆ Good (4)</option>
                    <option value={3}>★★★☆☆ Average (3)</option>
                    <option value={2}>★★☆☆☆ Poor (2)</option>
                    <option value={1}>★☆☆☆☆ Very Poor (1)</option>
                  </Form.Select>
                </Form.Group>

                <Button
                  variant="primary"
                  type="submit"
                  disabled={submitting}
                  className="w-100"
                >
                  {submitting ? 'Submitting...' : 'Submit Feedback'}
                </Button>
              </Form>

              <Alert variant="info" className="mt-3">
                <small>
                  <strong>Privacy Note:</strong> Your feedback helps us improve our service. 
                  We may contact you for follow-up questions. Personal data is handled according 
                  to our privacy policy.
                </small>
              </Alert>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Your Feedback History</h5>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center">
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              ) : feedbacks.length === 0 ? (
                <p className="text-muted text-center">
                  No feedback submitted yet. Your feedback history will appear here.
                </p>
              ) : (
                <ListGroup variant="flush">
                  {feedbacks.slice(0, 5).map((feedback) => (
                    <ListGroup.Item key={feedback.id} className="px-0">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center mb-1">
                            <h6 className="mb-0 me-2">{feedback.subject}</h6>
                            <Badge bg={getCategoryColor(feedback.category)}>
                              {feedback.category}
                            </Badge>
                            {feedback.status && (
                              <Badge bg={getStatusColor(feedback.status)} className="ms-1">
                                {feedback.status.replace('_', ' ')}
                              </Badge>
                            )}
                          </div>
                          <p className="mb-1 text-muted" style={{ fontSize: '0.9em' }}>
                            {feedback.message.length > 100
                              ? `${feedback.message.substring(0, 100)}...`
                              : feedback.message}
                          </p>
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              {formatDate(feedback.created_at)}
                            </small>
                            <div>
                              {renderStars(feedback.rating)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}

              {feedbacks.length > 5 && (
                <div className="text-center mt-3">
                  <Button variant="outline-primary" size="sm">
                    View All Feedback
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Quick Help Section */}
          <Card className="mt-3">
            <Card.Header>
              <h6 className="mb-0">Quick Help</h6>
            </Card.Header>
            <Card.Body>
              <div className="mb-2">
                <strong>Common Issues:</strong>
              </div>
              <ul className="small mb-0">
                <li>Predictions taking too long? Check your internet connection.</li>
                <li>Can't see your data? Try refreshing the page.</li>
                <li>Missing features? Let us know what you'd like to see!</li>
                <li>Need help getting started? Check our documentation.</li>
              </ul>
              <div className="mt-3">
                <Button variant="outline-info" size="sm" className="me-2">
                  Documentation
                </Button>
                <Button variant="outline-secondary" size="sm">
                  Contact Support
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Feedback;
