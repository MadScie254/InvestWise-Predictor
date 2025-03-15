require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// Safaricom Daraja API Credentials
const CONSUMER_KEY = process.env.CONSUMER_KEY;
const CONSUMER_SECRET = process.env.CONSUMER_SECRET;
const BUSINESS_SHORT_CODE = '174379'; // Default PayBill for testing
const PASSKEY = process.env.PASSKEY; // Get from Safaricom Developer Portal

// Endpoint to initiate M-PESA payment
app.post('/initiate-payment', async (req, res) => {
  const { phoneNumber } = req.body;

  try {
    // Step 1: Get Access Token
    const authResponse = await axios.get('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', {
      auth: {
        username: CONSUMER_KEY,
        password: CONSUMER_SECRET,
      },
    });
    const accessToken = authResponse.data.access_token;

    // Step 2: Initiate STK Push
    const timestamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0];
    const password = Buffer.from(`${BUSINESS_SHORT_CODE}${PASSKEY}${timestamp}`).toString('base64');

    const stkPushResponse = await axios.post(
      'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
      {
        BusinessShortCode: BUSINESS_SHORT_CODE,
        Password: password,
        Timestamp: timestamp,
        TransactionType: 'CustomerPayBillOnline',
        Amount: 1, // Amount in KES
        PartyA: phoneNumber,
        PartyB: BUSINESS_SHORT_CODE,
        PhoneNumber: phoneNumber,
        CallBackURL: 'https://yourdomain.com/callback', // Replace with your callback URL
        AccountReference: 'InvestWise Predictor',
        TransactionDesc: 'Premium Content Payment',
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    if (stkPushResponse.data.ResponseCode === '0') {
      res.json({ success: true });
    } else {
      res.json({ success: false });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ success: false });
  }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});