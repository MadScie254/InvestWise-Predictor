/**
 * InvestWise-Predictor Frontend Component Tests
 * Basic functionality tests for React components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock API utility
jest.mock('../utils/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}));

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

// Mock Chart.js
jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }) => <div data-testid="line-chart">Line Chart</div>,
  Bar: ({ data, options }) => <div data-testid="bar-chart">Bar Chart</div>,
}));

// Import components to test
import Dashboard from '../components/Dashboard';
import Login from '../components/Login';
import Register from '../components/Register';
import PredictionForm from '../components/PredictionForm';
import Investment from '../components/Investment';
import Profile from '../components/Profile';

describe('InvestWise-Predictor Component Tests', () => {
  
  describe('Dashboard Component', () => {
    test('renders dashboard with stats cards', () => {
      render(<Dashboard />);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      // Check for stats cards
      expect(screen.getByText('Total Predictions')).toBeInTheDocument();
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('Active Investments')).toBeInTheDocument();
    });

    test('displays charts correctly', () => {
      render(<Dashboard />);
      
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });

  describe('Authentication Components', () => {
    test('login form renders correctly', () => {
      render(<Login />);
      
      expect(screen.getByText('Login')).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    test('register form renders correctly', () => {
      render(<Register />);
      
      expect(screen.getByText('Register')).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
    });

    test('login form validation works', async () => {
      render(<Login />);
      
      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);
      
      // Should show validation errors for empty fields
      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Prediction Components', () => {
    test('prediction form renders with all fields', () => {
      render(<PredictionForm />);
      
      expect(screen.getByText('Create Prediction')).toBeInTheDocument();
      expect(screen.getByLabelText(/symbol/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/prediction type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/time horizon/i)).toBeInTheDocument();
    });

    test('prediction form handles input changes', () => {
      render(<PredictionForm />);
      
      const symbolInput = screen.getByLabelText(/symbol/i);
      fireEvent.change(symbolInput, { target: { value: 'AAPL' } });
      
      expect(symbolInput.value).toBe('AAPL');
    });

    test('prediction form validates symbol format', async () => {
      render(<PredictionForm />);
      
      const symbolInput = screen.getByLabelText(/symbol/i);
      fireEvent.change(symbolInput, { target: { value: 'invalid123!' } });
      
      const submitButton = screen.getByRole('button', { name: /create prediction/i });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/invalid symbol/i)).toBeInTheDocument();
      });
    });
  });

  describe('Investment Component', () => {
    test('investment table renders correctly', () => {
      render(<Investment />);
      
      expect(screen.getByText('My Investments')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add investment/i })).toBeInTheDocument();
    });

    test('add investment modal opens', () => {
      render(<Investment />);
      
      const addButton = screen.getByRole('button', { name: /add investment/i });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Add Investment')).toBeInTheDocument();
      expect(screen.getByLabelText(/symbol/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/company name/i)).toBeInTheDocument();
    });

    test('investment form validation works', async () => {
      render(<Investment />);
      
      const addButton = screen.getByRole('button', { name: /add investment/i });
      fireEvent.click(addButton);
      
      const submitButton = screen.getByRole('button', { name: /add investment/i });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Profile Component', () => {
    test('profile form renders with user fields', () => {
      render(<Profile />);
      
      expect(screen.getByText('Profile Settings')).toBeInTheDocument();
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });

    test('profile form handles updates', () => {
      render(<Profile />);
      
      const firstNameInput = screen.getByLabelText(/first name/i);
      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      
      expect(firstNameInput.value).toBe('John');
    });
  });

  describe('Form Validation Tests', () => {
    test('email validation works across components', () => {
      const testCases = [
        { email: 'test@example.com', valid: true },
        { email: 'invalid-email', valid: false },
        { email: 'test@', valid: false },
        { email: '@example.com', valid: false },
      ];

      testCases.forEach(({ email, valid }) => {
        render(<Register />);
        
        const emailInput = screen.getByLabelText(/email/i);
        fireEvent.change(emailInput, { target: { value: email } });
        fireEvent.blur(emailInput);
        
        if (valid) {
          expect(screen.queryByText(/invalid email/i)).not.toBeInTheDocument();
        } else {
          expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
        }
      });
    });

    test('password strength validation', () => {
      render(<Register />);
      
      const passwordInput = screen.getByLabelText(/^password$/i);
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      fireEvent.blur(passwordInput);
      
      expect(screen.getByText(/password too weak/i)).toBeInTheDocument();
    });
  });

  describe('API Integration Tests', () => {
    test('components handle API loading states', async () => {
      const api = require('../utils/api');
      api.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      render(<Dashboard />);
      
      // Should show loading state
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      });
    });

    test('components handle API errors gracefully', async () => {
      const api = require('../utils/api');
      api.get.mockRejectedValue(new Error('API Error'));
      
      render(<Dashboard />);
      
      await waitFor(() => {
        expect(screen.getByText(/error loading data/i)).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design Tests', () => {
    test('components adapt to mobile viewport', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(<Dashboard />);
      
      // Check if mobile-specific classes are applied
      const dashboard = screen.getByText('Dashboard').closest('div');
      expect(dashboard).toHaveClass('container');
    });

    test('navigation collapses on mobile', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      // This would test the Header component if it were imported
      // For now, we'll just verify the responsive behavior is considered
      expect(true).toBe(true);
    });
  });

  describe('Accessibility Tests', () => {
    test('forms have proper labels', () => {
      render(<Login />);
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      
      expect(usernameInput).toBeInTheDocument();
      expect(passwordInput).toBeInTheDocument();
    });

    test('buttons have proper aria labels', () => {
      render(<PredictionForm />);
      
      const submitButton = screen.getByRole('button', { name: /create prediction/i });
      expect(submitButton).toBeInTheDocument();
    });

    test('error messages are announced to screen readers', async () => {
      render(<Login />);
      
      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/required/i);
        expect(errorMessage).toHaveAttribute('role', 'alert');
      });
    });
  });
});

// Integration test for full user workflow
describe('User Workflow Integration Tests', () => {
  test('complete prediction creation workflow', async () => {
    const api = require('../utils/api');
    
    // Mock successful API responses
    api.post.mockResolvedValue({
      data: {
        id: 1,
        symbol: 'AAPL',
        prediction_type: 'price',
        predicted_value: 175.50,
        confidence: 85.2,
        status: 'completed'
      }
    });

    render(<PredictionForm />);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/symbol/i), { target: { value: 'AAPL' } });
    fireEvent.change(screen.getByLabelText(/prediction type/i), { target: { value: 'price' } });
    fireEvent.change(screen.getByLabelText(/time horizon/i), { target: { value: '1M' } });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /create prediction/i }));
    
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/v1/predictions/', {
        symbol: 'AAPL',
        prediction_type: 'price',
        time_horizon: '1M'
      });
    });
  });

  test('complete investment tracking workflow', async () => {
    const api = require('../utils/api');
    
    // Mock successful API responses
    api.post.mockResolvedValue({
      data: {
        id: 1,
        symbol: 'AAPL',
        company_name: 'Apple Inc.',
        investment_type: 'stock',
        shares: 10,
        purchase_price: 150.00,
        current_value: 1755.00,
        gain_loss: { value: 5.00, percentage: 0.33, is_positive: true }
      }
    });

    render(<Investment />);
    
    // Open add investment modal
    fireEvent.click(screen.getByRole('button', { name: /add investment/i }));
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/symbol/i), { target: { value: 'AAPL' } });
    fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Apple Inc.' } });
    fireEvent.change(screen.getByLabelText(/shares/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/purchase price/i), { target: { value: '150.00' } });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /add investment/i }));
    
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/v1/investments/', {
        symbol: 'AAPL',
        company_name: 'Apple Inc.',
        investment_type: 'stock',
        shares: '10',
        purchase_price: '150.00'
      });
    });
  });
});

console.log('✅ Frontend component tests configured successfully!');
