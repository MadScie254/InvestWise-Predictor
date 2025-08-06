import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, Alert, ListGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../utils/api';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/notifications/');
      const notificationData = response.data.results || response.data;
      setNotifications(notificationData);
      setUnreadCount(notificationData.filter(n => !n.read).length);
    } catch (error) {
      toast.error('Failed to fetch notifications');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.patch(`/api/v1/notifications/${id}/`, { read: true });
      setNotifications(notifications.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      toast.error('Failed to mark notification as read');
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/api/v1/notifications/mark-all-read/');
      setNotifications(notifications.map(notification => ({
        ...notification,
        read: true
      })));
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all notifications as read');
    }
  };

  const deleteNotification = async (id) => {
    try {
      await api.delete(`/api/v1/notifications/${id}/`);
      const deletedNotification = notifications.find(n => n.id === id);
      setNotifications(notifications.filter(notification => notification.id !== id));
      if (!deletedNotification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      toast.success('Notification deleted');
    } catch (error) {
      toast.error('Failed to delete notification');
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      prediction: '📊',
      investment: '💰',
      alert: '⚠️',
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌',
    };
    return icons[type] || 'ℹ️';
  };

  const getNotificationVariant = (type) => {
    const variants = {
      prediction: 'primary',
      investment: 'success',
      alert: 'warning',
      info: 'info',
      success: 'success',
      warning: 'warning',
      error: 'danger',
    };
    return variants[type] || 'secondary';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
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
          <div className="d-flex justify-content-between align-items-center">
            <h2>
              Notifications 
              {unreadCount > 0 && (
                <Badge bg="danger" className="ms-2">
                  {unreadCount}
                </Badge>
              )}
            </h2>
            {unreadCount > 0 && (
              <Button variant="outline-primary" onClick={markAllAsRead}>
                Mark All as Read
              </Button>
            )}
          </div>
        </Col>
      </Row>

      <Row>
        <Col>
          {notifications.length === 0 ? (
            <Card>
              <Card.Body className="text-center">
                <h5>No notifications</h5>
                <p className="text-muted">You're all caught up!</p>
              </Card.Body>
            </Card>
          ) : (
            <Card>
              <ListGroup variant="flush">
                {notifications.map((notification) => (
                  <ListGroup.Item
                    key={notification.id}
                    className={`d-flex justify-content-between align-items-start ${
                      !notification.read ? 'border-start border-primary border-3' : ''
                    }`}
                    style={{
                      backgroundColor: !notification.read ? '#f8f9fa' : 'white',
                    }}
                  >
                    <div className="ms-2 me-auto">
                      <div className="d-flex align-items-center mb-1">
                        <span className="me-2" style={{ fontSize: '1.2em' }}>
                          {getNotificationIcon(notification.type)}
                        </span>
                        <h6 className="mb-0">{notification.title}</h6>
                        <Badge 
                          bg={getNotificationVariant(notification.type)} 
                          className="ms-2"
                        >
                          {notification.type}
                        </Badge>
                        {!notification.read && (
                          <Badge bg="info" className="ms-1">
                            New
                          </Badge>
                        )}
                      </div>
                      <p className="mb-1">{notification.message}</p>
                      <small className="text-muted">
                        {formatDate(notification.created_at)}
                      </small>
                    </div>
                    <div className="d-flex flex-column gap-1">
                      {!notification.read && (
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => markAsRead(notification.id)}
                        >
                          Mark Read
                        </Button>
                      )}
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => deleteNotification(notification.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          )}
        </Col>
      </Row>

      {/* Summary Alert */}
      {notifications.length > 0 && (
        <Row className="mt-4">
          <Col>
            <Alert variant="info">
              <strong>Summary:</strong> You have {notifications.length} total notifications
              {unreadCount > 0 && `, ${unreadCount} unread`}.
            </Alert>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default Notifications;
