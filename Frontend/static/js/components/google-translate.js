const axios = require('axios'); // Make sure you have Axios installed in your project

const API_KEY = 'AIzaSyCq3ffs5B-n2htAQOb33_xjM6nPY_ZL0Jk'; // Replace with your actual API key

async function translate(text) {
  try {
    const res = await axios.post(
      `https://translation.googleapis.com/language/translate/v2?key=${API_KEY}`,
      { q: text, target: 'si' }
    );

    const translation = res.data.data.translations[0].translatedText;
    return translation;
  } catch (error) {
    console.error('Error translating:', error);
    throw error;
  }
}

module.exports = { translate };