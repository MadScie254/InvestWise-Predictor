import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  return (
    <footer className="bg-dark text-light py-4 mt-5">
      <Container>
        <Row>
          <Col md={6}>
            <h5>InvestWise Predictor</h5>
            <p className="mb-0">
              AI-driven investment analysis for data-backed decisions.
            </p>
          </Col>
          <Col md={3}>
            <h6>Quick Links</h6>
            <ul className="list-unstyled">
              <li><a href="/" className="text-light text-decoration-none">Dashboard</a></li>
              <li><a href="/predictions" className="text-light text-decoration-none">Predictions</a></li>
              <li><a href="/about" className="text-light text-decoration-none">About</a></li>
            </ul>
          </Col>
          <Col md={3}>
            <h6>Support</h6>
            <ul className="list-unstyled">
              <li><a href="/contact" className="text-light text-decoration-none">Contact</a></li>
              <li><a href="/help" className="text-light text-decoration-none">Help</a></li>
              <li><a href="/privacy" className="text-light text-decoration-none">Privacy</a></li>
            </ul>
          </Col>
        </Row>
        <hr className="my-3" />
        <Row>
          <Col className="text-center">
            <p className="mb-0">
              &copy; 2025 InvestWise Predictor. All rights reserved.
            </p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
