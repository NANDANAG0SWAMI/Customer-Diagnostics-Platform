import axios from 'axios';

// --- Configuration ---
// These paths are configured to work with our Nginx reverse proxy
const TEXT_TO_SQL_API_BASE_URL = '/api/text-to-sql';
const DIAGNOSTICS_API_BASE_URL = '/api/diagnostics';

// --- API Functions ---

/**
 * Sends a natural language question to the Text-to-SQL API.
 * @param {string} question - The user's question.
 * @returns {Promise<object>} The API response data.
 */
export const askTextToSqlApi = async (question) => {
    try {
        const response = await axios.post(`${TEXT_TO_SQL_API_BASE_URL}/ask`, { question });
        return response.data;
    } catch (error) {
        console.error("Error calling Text-to-SQL API:", error);
        throw error;
    }
};

/**
 * Triggers a product diagnosis from the Diagnostics API.
 * @param {number} productId - The ID of the product.
 * @param {string} productName - The name of the product.
 * @returns {Promise<object>} The API response data.
 */
export const runDiagnosticsApi = async (productId, productName) => {
    try {
        const response = await axios.post(`${DIAGNOSTICS_API_BASE_URL}/tools/diagnose-product`, {
            product_id: productId,
            product_name: productName,
        });
        return response.data;
    } catch (error) {
        console.error("Error calling Diagnostics API:", error);
        throw error;
    }
};